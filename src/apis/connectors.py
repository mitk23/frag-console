from utils.http_request import http_delete, http_get, http_post


async def get_connector_all(fqdn: str, api_key: str) -> dict[str, str]:
    endpoint = f"{fqdn}/api/management/connectors"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_get(endpoint, headers=headers)
    assert response.status_code == 200

    return response.json()


async def create_connector(fqdn: str, api_key: str, connector: dict[str, str]) -> None:
    endpoint = f"{fqdn}/api/management/connectors"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_post(endpoint, headers=headers, json=connector)
    assert response.status_code == 201

    print(f"[INFO] Succeeded to create the connector: {connector}\n")


async def delete_connector(fqdn: str, api_key: str, connector_id: str) -> None:
    endpoint = f"{fqdn}/api/management/connectors/{connector_id}"
    headers = {"X-Management-Api-Key": api_key}

    response = await http_delete(endpoint, headers=headers)
    assert response.status_code == 204

    print(f"[INFO] Succeeded to delete the connector: {connector_id}\n")
