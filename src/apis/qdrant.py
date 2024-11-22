import asyncio

from qdrant_client import AsyncQdrantClient

import config


class QdrantQueryService:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

        self.client = AsyncQdrantClient(url=config.QDRANT_URL)

    async def fetch_embeddings(self, id_list: list[int]) -> dict[int, list[float]]:
        records = await self.client.retrieve(
            collection_name=self.collection_name, ids=id_list, with_payload=False, with_vectors=True
        )
        return {record.id: record.vector for record in records}


async def test_fetch():
    service = QdrantQueryService("trec-covid-query-test")
    embeddings = asyncio.run(service.fetch_embeddings(id_list=[0, 1, 2]))
    print(embeddings)
