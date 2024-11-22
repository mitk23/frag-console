from typing import Any

from httpx import Response

from apis.assets import get_asset_id
from utils.http_request import http_delete, http_get, http_post


async def get_asset_catalogs(fqdn: str, api_key: str, provider_id: str) -> dict[str, Any]:
    endpoint = f"{fqdn}/api/dataspace/catalogs?{provider_id=}"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_get(endpoint, headers=headers)
    assert response.status_code == 200

    return response.json()


async def download_asset_distribution(
    fqdn: str, api_key: str, provider_id: str, asset_title: str, distribution_title: str
) -> Response:
    asset_id = await get_asset_id(fqdn, api_key, asset_title)

    endpoint = f"{fqdn}/api/dataspace/assets?{provider_id=}&{asset_id=}&{distribution_title=}"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_get(endpoint, headers=headers)
    assert response.status_code == 200

    print(f"[INFO] Succeeded to download the distribution: [{distribution_title}]\n")
    return response


async def retrieve_knowledge(
    fqdn: str, api_key: str, providers: list[str], embedding: list[float], top_k: int, rerank_method: str
):
    endpoint = f"{fqdn}/api/dataspace/knowledges"
    headers = {"X-Management-Api-Key": api_key}

    query = {
        "providers": providers,
        "include_provider_contribution": True,
        "knowledge_rerank_method": rerank_method,
        "query": {
            "embedding": embedding,
            "config": {
                "top_k": top_k,
                "include_embedding": True,
                "filter": None,
            },
        },
    }

    response = await http_post(endpoint, headers=headers, json=query)
    assert response.status_code == 200

    knowledges: list[dict[str, Any]] = response.json()
    print(f"[INFO] Succeeded to retrieve {len(knowledges)} knowledges\n")
    return knowledges


async def create_asset(fqdn: str, api_key: str, asset: dict[str, Any]) -> None:
    endpoint = f"{fqdn}/api/management/assets"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_post(endpoint, headers=headers, json=asset)
    assert response.status_code == 201

    print(f"[INFO] Succeeded to create the asset: {asset}\n")


async def delete_asset(fqdn: str, api_key: str, asset_title: str) -> None:
    asset_id = await get_asset_id(fqdn, api_key, asset_title)

    endpoint = f"{fqdn}/api/management/assets/{asset_id}"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_delete(endpoint, headers=headers)
    assert response.status_code == 204

    print(f"[INFO] Succeeded to delete the asset: {asset_title}\n")
