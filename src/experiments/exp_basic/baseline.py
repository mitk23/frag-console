import asyncio
import json
import os
import pathlib

from tqdm import tqdm

from experiments import config
from experiments.retrieve import retrieve_from_qdrant
from load_beir import BeirRepository


async def retrieve_direct(n_queries: int = -1, exact_search: bool = False) -> dict[str, dict[str, float]]:
    repository = BeirRepository(config.EXPERIMENT_DATASET_NAME)

    if n_queries < 0:
        queries = repository.queries()
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    else:
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(n_queries))

    run_trec: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve_from_qdrant(embedding=embedding, exact_search=exact_search)

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
    n_queries = -1

    run_trec = await retrieve_direct(n_queries=n_queries, exact_search=False)

    trec_filename = f"exp1_{config.EXPERIMENT_DATASET_NAME}_baseline.json"
    save_run_trec(run_trec, trec_filename)

    print(f"[INFO] Completed to save retrieval run to [{trec_filename}]")


if __name__ == "__main__":
    asyncio.run(main())
