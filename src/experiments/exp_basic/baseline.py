import asyncio

from tqdm import tqdm

from experiments.config import BaseExperimentConfig
from experiments.exp_basic.config import ExperimentConfig
from experiments.retrieve import retrieve_from_qdrant, save_retrieve_result
from load_beir import BeirRepository


async def retrieve(exp_config: BaseExperimentConfig, n_queries: int = -1) -> dict[str, dict[str, float]]:
    repository = BeirRepository(exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    if n_queries < 0:
        queries = repository.queries()
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    else:
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(n_queries))

    run: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve_from_qdrant(embedding=embedding, exp_config=exp_config)

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run


async def main(exp_config: BaseExperimentConfig):
    n_queries = int(input("# of queries? (default: -1): "))

    run = await retrieve(exp_config, n_queries=n_queries)

    if exp_config.EXACT_SEARCH:
        out_filename = f"exp1_{exp_config.DATASET_NAME}_baseline-exact.json"
    else:
        out_filename = f"exp1_{exp_config.DATASET_NAME}_baseline.json"
    save_retrieve_result(run, out_filename)

    print(f"[INFO] Completed to save retrieval run to [{out_filename}]")


if __name__ == "__main__":
    exact_search = input("Retrieve exactly? (Disable ANN?) [y/n]: ")
    if exact_search in {"y", "Y"}:
        exp_config = ExperimentConfig(exact_search=True)
    else:
        exp_config = ExperimentConfig()

    asyncio.run(main(exp_config))
