import asyncio

from apis.assets import create_asset, delete_asset, get_asset_all
from apis.connectors import create_connector, delete_connector, get_connector_all
from experiments import config


async def register_initial_assets() -> None:
    """
    Register assets to all providers
    """

    async def _register(idx: int):
        fqdn = config.EXPERIMENT_CONNECTOR_LOCATIONS[idx]

        prev_assets = await get_asset_all(fqdn, api_key=config.CONNECTOR_API_KEY)
        for _, asset in prev_assets.items():
            await delete_asset(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, asset_title=asset["title"])

        for asset in config.INITIAL_ASSETS:
            await create_asset(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, asset=asset)

    try:
        async with asyncio.TaskGroup() as tg:
            for idx in range(config.EXPERIMENT_NUM_CONSUMERS + 1, config.EXPERIMENT_NUM_CONNECTORS + 1):
                tg.create_task(_register(idx))
    except* Exception as err:
        print(f"{err.exceptions=}")


async def register_initial_counter_connectors() -> None:
    async def _register_consumer(idx: int):
        fqdn = config.EXPERIMENT_CONNECTOR_LOCATIONS[idx]

        prev_connectors = await get_connector_all(fqdn, api_key=config.CONNECTOR_API_KEY)
        for connector_id in prev_connectors.keys():
            await delete_connector(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, connector_id=connector_id)

        for connector in config.INITIAL_CONNECTORS_FOR_CONSUMER:
            await create_connector(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, connector=connector)

    async def _register_provider(idx: int):
        fqdn = config.EXPERIMENT_CONNECTOR_LOCATIONS[idx]

        prev_connectors = await get_connector_all(fqdn, api_key=config.CONNECTOR_API_KEY)
        for connector_id in prev_connectors.keys():
            await delete_connector(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, connector_id=connector_id)

        for connector in config.INITIAL_CONNECTORS_FOR_PROVIDER:
            await create_connector(fqdn=fqdn, api_key=config.CONNECTOR_API_KEY, connector=connector)

    try:
        async with asyncio.TaskGroup() as tg:
            for idx in range(1, config.EXPERIMENT_NUM_CONSUMERS + 1):
                tg.create_task(_register_consumer(idx))

            for idx in range(config.EXPERIMENT_NUM_CONSUMERS + 1, config.EXPERIMENT_NUM_CONNECTORS + 1):
                tg.create_task(_register_provider(idx))
    except* Exception as err:
        print(f"{err.exceptions=}")


async def initialize_connectors() -> None:
    print("Initialize Connectors...")

    await register_initial_assets()
    print("[INFO] Completed to register initial assets.")

    await register_initial_counter_connectors()
    print("[INFO] Completed to register initial connectors.")


async def main():
    char = input("Please make sure that containers are started [y/n] ")
    if char not in {"y", "Y"}:
        print("Exit")
        return

    await initialize_connectors()


if __name__ == "__main__":
    asyncio.run(main())
