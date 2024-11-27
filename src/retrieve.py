import asyncio
import json
import os
import pathlib
from typing import Any

from tqdm import tqdm

from apis.dataspace import retrieve_knowledge
from config import API_KEYS, LOCATIONS
from load_beir import BeirRepository

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


async def retrieve_beir(
    dataset_name: str, consumer_connector_name: str, top_k: int, rerank_method: str
) -> dict[str, dict[str, float]]:
    repository = BeirRepository(dataset_name)

    corpus = repository.corpus()
    queries = repository.queries()
    print(f"{dataset_name} | # of Documents: {len(corpus)} | # of Query: {len(queries)}")

    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))

    qrel_run: dict[str, dict[str, float]] = {}
    # try:
    #     tasks: list[asyncio.Task] = []
    #     async with asyncio.TaskGroup() as tg:
    #         for query_id, embedding in query_embeddings_dict.items():
    #             task = tg.create_task(
    #                 retrieve_from_dataspace(
    #                     connector_name=consumer_connector_name,
    #                     embedding=embedding,
    #                     top_k=top_k,
    #                     rerank_method=rerank_method,
    #                     show_result=False,
    #                 )
    #             )
    #             tasks.append(task)
    # except* Exception as err:
    #     print(f"{err.exceptions=}")

    # for idx, query_id in enumerate(query_embeddings_dict.keys()):
    #     knowledges = tasks[idx].result()

    #     qrel_run[query_id] = {
    #         repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
    #     }

    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="retrieve"):
        knowledges = await retrieve_from_dataspace(
            connector_name=consumer_connector_name,
            embedding=embedding,
            top_k=top_k,
            rerank_method=rerank_method,
            show_result=False,
        )

        qrel_run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return qrel_run


def save_run(run: dict[str, dict[str, float]], filename: str) -> None:
    src_dir = pathlib.Path(__file__).parent.absolute()
    output_file = os.path.join(src_dir, "outputs", filename)

    with open(output_file, "w") as file:
        json.dump(run, file, indent=2)


async def main():
    connector_name = "frag-connector-03"
    char = input(f"Request retrieval to [{connector_name}]? [y/n] ")

    if char not in {"y", "Y"}:
        print("Exit")
        return

    # embedding = [10, 12]
    # top_k = 10
    # await retrieve_from_dataspace(connector_name=connector_name, embedding=embedding, top_k=top_k)

    dataset_name = "trec-covid"
    top_k = 10
    rerank_method = "cosine"

    run = await retrieve_beir(
        dataset_name=dataset_name, consumer_connector_name=connector_name, top_k=top_k, rerank_method=rerank_method
    )
    print(json.dumps(run, indent=2, ensure_ascii=False))

    output_filename = f"{dataset_name}_run@{top_k}.json"
    save_run(run, output_filename)


if __name__ == "__main__":
    asyncio.run(main())
