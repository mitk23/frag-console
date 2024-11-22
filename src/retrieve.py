import asyncio
import json
from typing import Any

from apis.dataspace import retrieve_knowledge
from apis.qdrant import QdrantQueryService
from config import API_KEYS, LOCATIONS, qdrant_query_collection_name

RETRIEVAL_PROVIDERS = ["frag-connector-01"]


async def retrieve_from_dataspace(
    connector_name: str, embedding: list[float], top_k: int, rerank_method: str = "cosine", show_result: bool = True
) -> list[dict[str, Any]]:
    fqdn = LOCATIONS[connector_name]
    api_key = API_KEYS[connector_name]

    knowledges = await retrieve_knowledge(
        fqdn,
        api_key,
        providers=RETRIEVAL_PROVIDERS,
        embedding=embedding,
        top_k=top_k,
        rerank_method=rerank_method,
    )

    if show_result:
        print("-" * 10, "Retrieval Result", "-" * 10)
        print(json.dumps(knowledges, indent=2, ensure_ascii=False))
        print("-" * 30)

    return knowledges


async def run_experiment(dataset_name: str, consumer_connector_name: str, top_k: int, rerank_method: str):
    query_collection_name = qdrant_query_collection_name(dataset_name)
    qdrant_query_service = QdrantQueryService(collection_name=query_collection_name)

    query_idx_list = range(5)
    query_embeddings = await qdrant_query_service.fetch_embeddings(query_idx_list)

    for idx, embedding in query_embeddings.items():
        await retrieve_from_dataspace(
            connector_name=consumer_connector_name, embedding=embedding, top_k=top_k, rerank_method=rerank_method
        )


async def main():
    connector_name = "frag-connector-03"
    char = input(f"Request retrieval to [{connector_name}]? [y/n] ")

    if char not in {"y", "Y"}:
        print("Exit")
        return

    embedding = [10, 12]
    top_k = 10
    await retrieve_from_dataspace(connector_name=connector_name, embedding=embedding, top_k=top_k)


if __name__ == "__main__":
    asyncio.run(main())
