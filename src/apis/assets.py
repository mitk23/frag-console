import sys
from typing import Any

from utils.http_request import http_delete, http_get, http_post


async def get_asset_all(fqdn: str, api_key: str) -> dict[str, Any]:
    endpoint = f"{fqdn}/api/management/assets"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_get(endpoint, headers=headers)
    assert response.status_code == 200

    return response.json()


async def get_asset_id(fqdn: str, api_key: str, asset_title: str) -> str:
    endpoint = f"{fqdn}/api/management/assets"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_get(endpoint, headers=headers)
    assets: dict[str, Any] = response.json()

    for asset_id, asset in assets.items():
        if asset["title"] == asset_title:
            return asset_id

    print(f"[ERROR] Asset title [{asset_title}] not found")
    sys.exit(1)


async def create_asset(fqdn: str, api_key: str, asset: dict[str, Any]) -> None:
    endpoint = f"{fqdn}/api/management/assets"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_post(endpoint, headers=headers, json=asset)
    assert response.status_code == 201

    # print(f"[INFO] Succeeded to create the asset: {asset}\n")


async def delete_asset(fqdn: str, api_key: str, asset_title: str) -> None:
    asset_id = await get_asset_id(fqdn, api_key, asset_title)

    endpoint = f"{fqdn}/api/management/assets/{asset_id}"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_delete(endpoint, headers=headers)
    assert response.status_code == 204

    # print(f"[INFO] Succeeded to delete the asset: {asset_title}\n")
