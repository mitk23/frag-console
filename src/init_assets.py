import asyncio

from apis.assets import create_asset, delete_asset, get_asset_all
from config import API_KEYS, LOCATIONS

INIT_ASSETS = [
    {
        "title": "c-asset",
        "description": "confidential dataset",
        "usage_policy": {"security_level": "confidential"},
        "distributions": [
            {
                "title": "confidential.txt",
                "description": "document file",
                "media_type": "text/plain",
                "url": "http://172.26.16.10:1080/confidential.txt",
            }
        ],
    },
    {
        "title": "r-asset",
        "description": "restricted dataset",
        "usage_policy": {"security_level": "restricted"},
        "distributions": [
            {
                "title": "restricted.txt",
                "description": "document file",
                "media_type": "text/plain",
                "url": "http://172.26.16.10:1080/restricted.txt",
            }
        ],
    },
    {
        "title": "p-asset",
        "description": "public dataset",
        "usage_policy": {"security_level": "public"},
        "distributions": [
            {
                "title": "public.txt",
                "description": "document file",
                "media_type": "text/plain",
                "url": "http://172.26.16.10:1080/public.txt",
            }
        ],
    },
    {
        "title": "qdrant-example-index-confidential",
        "description": "confidential embeddings in qdrant",
        "usage_policy": {"security_level": "confidential"},
        "vectors": {"has_metadata": {"genre": "movie"}, "has_id": []},
    },
    {
        "title": "qdrant-example-index-restricted",
        "description": "restricted embeddings in qdrant",
        "usage_policy": {"security_level": "restricted"},
        "vectors": {"has_metadata": {"genre": "music"}, "has_id": []},
    },
    {
        "title": "qdrant-example-index-public",
        "description": "public embeddings in qdrant",
        "usage_policy": {"security_level": "public"},
        "distributions": [],
        "vectors": {"has_metadata": {}, "has_id": ["3", "4"]},
    },
    {
        "title": "beir-nq",
        "description": "BEIR: Natural Questions",
        "usage_policy": {"security_level": "public"},
        "distributions": [],
        "vectors": {"has_metadata": {}, "has_id": ["*"]},
    },
    {
        "title": "beir-trec-covid",
        "description": "BEIR: TREC Covid",
        "usage_policy": {"security_level": "public"},
        "distributions": [],
        "vectors": {"has_metadata": {}, "has_id": ["*"]},
    },
]


async def init_assets(connector_name: str) -> None:
    fqdn = LOCATIONS[connector_name]
    api_key = API_KEYS[connector_name]

    prev_assets = await get_asset_all(fqdn, api_key)
    for _, asset in prev_assets.items():
        await delete_asset(fqdn, api_key, asset_title=asset["title"])

    for asset in INIT_ASSETS:
        await create_asset(fqdn, api_key, asset)

    print(f"[INFO] Completed to create {len(INIT_ASSETS)} assets")


async def main():
    connector_name = "frag-connector-01"
    char = input(f"Initialize assets in [{connector_name}]? [y/n] ")

    if char not in {"y", "Y"}:
        print("Exit")
        return

    await init_assets(connector_name=connector_name)


if __name__ == "__main__":
    asyncio.run(main())
