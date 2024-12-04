import asyncio

from apis.assets import create_asset, delete_asset, get_asset_all
from apis.connectors import create_connector, delete_connector, get_connector_all
from experiments.config import BaseExperimentConfig


async def register_initial_assets(exp_config: BaseExperimentConfig) -> None:
    async def _register(connector_index: int):
        fqdn = exp_config.connector_location(connector_index)

        prev_assets = await get_asset_all(fqdn, api_key=exp_config.CONNECTOR_API_KEY)
        for _, asset in prev_assets.items():
            await delete_asset(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, asset_title=asset["title"])

        initial_assets = exp_config.initial_assets(connector_index)
        for asset in initial_assets:
            await create_asset(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, asset=asset)

    try:
        async with asyncio.TaskGroup() as tg:
            for provider_index in exp_config.provider_index_range():
                tg.create_task(_register(provider_index))
    except* Exception as err:
        print(f"{err.exceptions=}")


async def register_initial_counter_connectors(exp_config: BaseExperimentConfig) -> None:
    async def _register_consumer(connector_index: int):
        fqdn = exp_config.connector_location(connector_index)

        prev_connectors = await get_connector_all(fqdn, api_key=exp_config.CONNECTOR_API_KEY)
        for connector_id in prev_connectors.keys():
            await delete_connector(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, connector_id=connector_id)

        initial_connectors = exp_config.initial_connectors(connector_type="consumer")
        for connector in initial_connectors:
            await create_connector(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, connector=connector)

    async def _register_provider(connector_index: int):
        fqdn = exp_config.connector_location(connector_index)

        prev_connectors = await get_connector_all(fqdn, api_key=exp_config.CONNECTOR_API_KEY)
        for connector_id in prev_connectors.keys():
            await delete_connector(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, connector_id=connector_id)

        initial_connectors = exp_config.initial_connectors(connector_type="provider")
        for connector in initial_connectors:
            await create_connector(fqdn=fqdn, api_key=exp_config.CONNECTOR_API_KEY, connector=connector)

    try:
        async with asyncio.TaskGroup() as tg:
            for consumer_index in exp_config.consumer_index_range():
                tg.create_task(_register_consumer(consumer_index))

            for provider_idx in exp_config.provider_index_range():
                tg.create_task(_register_provider(provider_idx))
    except* Exception as err:
        print(f"{err.exceptions=}")


async def main(exp_config: BaseExperimentConfig) -> None:
    await register_initial_assets(exp_config)
    print("[INFO] Completed to register initial assets.")

    await register_initial_counter_connectors(exp_config)
    print("[INFO] Completed to register initial connectors.")
