import asyncio
import datetime
import json
import os
import pathlib
from typing import Literal

from tqdm import tqdm

from experiments import config
from experiments.config import ExperimentConfig
from experiments.retrieve import retrieve_from_dataspace
from load_beir import BeirRepository


async def retrieve(
    consumer_index: Literal[1, 2, 3] = 1, n_queries: int = -1, providers: list[str] | None = None
) -> dict[str, dict[str, float]]:
    repository = BeirRepository(config.EXPERIMENT_DATASET_NAME)

    if n_queries < 0:
        queries = repository.queries()
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    else:
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(n_queries))

    if providers is None:
        providers = [
            ExperimentConfig.get_connector_name(connector_index=idx)
            for idx in range(config.EXPERIMENT_NUM_CONSUMERS + 1, config.EXPERIMENT_NUM_CONNECTORS + 1)
        ]

    run_trec: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve_from_dataspace(
            consumer_index=consumer_index, providers=providers, embedding=embedding
        )

        run_trec[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run_trec


def save_run_trec(run: dict[str, dict[str, float]], trec_filename: str) -> None:
    src_dir = pathlib.Path(__file__).parent.parent.absolute()
    output_file = os.path.join(src_dir, "outputs", trec_filename)

    with open(output_file, "w") as file:
        json.dump(run, file, indent=2)


async def main():
    consumer_index = int(input("Which consumer to request retrieval? (low: 1, medium: 2, high: 3): "))

    if consumer_index not in {1, 2, 3}:
        print("Exit")
        return

    n_queries = -1
    providers = None

    run_trec = await retrieve(consumer_index, n_queries=n_queries, providers=providers)

    trec_filename = f"exp1_{config.EXPERIMENT_DATASET_NAME}_{datetime.date.today()}.json"
    save_run_trec(run_trec, trec_filename)

    print(f"[INFO] Completed to save retrieval run to [{trec_filename}]")


if __name__ == "__main__":
    asyncio.run(main())
