import asyncio

from apis.connectors import create_connector, delete_connector, get_connector_all
from config import API_KEYS, LOCATIONS

INIT_CONNECTORS = {
    "frag-connector-01": [
        {"id": "frag-connector-03", "url": LOCATIONS["frag-connector-03"], "trust": "medium"},
    ],
    "frag-connector-03": [
        {"id": "frag-connector-01", "url": LOCATIONS["frag-connector-01"], "trust": "medium"},
    ],
}


async def init_connectors(connector_name: str) -> None:
    fqdn = LOCATIONS[connector_name]
    api_key = API_KEYS[connector_name]

    prev_connectors = await get_connector_all(fqdn, api_key)
    for connector_id in prev_connectors.keys():
        await delete_connector(fqdn, api_key, connector_id=connector_id)

    for connector in INIT_CONNECTORS[connector_name]:
        await create_connector(fqdn, api_key, connector)

    print(f"[INFO] Completed to create {len(INIT_CONNECTORS[connector_name])} assets")


async def main():
    connector_name = "frag-connector-03"
    char = input(f"Initialize connectors in [{connector_name}]? [y/n] ")

    if char not in {"y", "Y"}:
        print("Exit")
        return

    await init_connectors(connector_name=connector_name)


if __name__ == "__main__":
    asyncio.run(main())
