import asyncio
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import CollectionInfo, InitFrom, PointIdsList, QueryResponse, ScoredPoint, SearchParams


class QdrantQueryService:
    def __init__(self, qdrant_url: str, collection_name: str):
        self.collection_name = collection_name

        self.client = AsyncQdrantClient(url=qdrant_url)

    async def get_collection_info(self) -> CollectionInfo:
        return await self.client.get_collection(self.collection_name)

    async def copy_collection(self, new_collection_name: str) -> bool:
        collection_info = await self.get_collection_info()
        vectors_config = collection_info.config.params.vectors

        is_copied = await self.client.create_collection(
            collection_name=new_collection_name,
            vectors_config=vectors_config,
            init_from=InitFrom(collection=self.collection_name),
        )
        return is_copied

    async def delete_collection(self, collection_name: str) -> bool:
        if await self.client.collection_exists(collection_name):
            return await self.client.delete_collection(collection_name)
        return True

    async def fetch_embeddings(self, id_list: list[int]) -> dict[int, list[float]]:
        records = await self.client.retrieve(
            collection_name=self.collection_name, ids=id_list, with_payload=False, with_vectors=True
        )
        return {record.id: record.vector for record in records}

    async def delete_embeddings(self, id_list: list[int]):
        update_result = await self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=id_list),
            wait=False,
        )
        return update_result

    async def search_nearest(
        self, embedding: list[float], return_num_knowledges: int, exact_search: bool = False
    ) -> list[dict[str, Any]]:
        response: QueryResponse = await self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            limit=return_num_knowledges,
            with_vectors=True,
            with_payload=True,
            search_params=SearchParams(exact=exact_search),
        )
        scored_points: list[ScoredPoint] = response.points

        knowledges = [
            {
                "id": point.id,
                "score": point.score,
                "embedding": point.vector,
                "metadata": point.payload,
                "text": point.payload["text"],
            }
            for point in scored_points
        ]
        return knowledges


async def test_copy_collection():
    service = QdrantQueryService("nq-test")
    new_collection_name = "nq-2-2"

    result = await service.copy_collection(new_collection_name)
    print(result)


async def test_fetch():
    service = QdrantQueryService("trec-covid-query-test")
    embeddings = await service.fetch_embeddings(id_list=[0, 1, 2])
    print(embeddings)


async def test_delete_embeddings():
    collection_name = "nq-2-1"

    service = QdrantQueryService(collection_name)

    n_points = 2681468
    delete_id_list = range(n_points // 2, n_points)

    update_result = await service.delete_embeddings(id_list=delete_id_list)
    print(update_result)


if __name__ == "__main__":
    asyncio.run(test_copy_collection())
