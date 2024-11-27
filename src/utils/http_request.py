import httpx
from httpx import Response


async def http_get(endpoint, headers) -> Response:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            print(f"[ERROR] GET {error=}")
            print(error.response.json())
            raise error
    return response


async def http_post(endpoint, headers, json) -> Response:
    timeout = httpx.Timeout(None)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(endpoint, headers=headers, json=json)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            print(f"[ERROR] POST {error=}")
            print(error.response.json())
            raise error
    return response


async def http_delete(endpoint, headers) -> Response:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(endpoint, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            print(f"[ERROR] DELETE {error=}")
            print(error.response.json())
            raise error
    return response
