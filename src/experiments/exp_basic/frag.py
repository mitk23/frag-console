import asyncio

from tqdm import tqdm

from experiments import deploy
from experiments.config import BaseExperimentConfig
from experiments.exp_basic.config import ExperimentConfig
from experiments.retrieve import retrieve_from_dataspace, save_retrieve_result
from load_beir import BeirRepository


async def retrieve(exp_config: BaseExperimentConfig, n_queries: int = -1) -> dict[str, dict[str, float]]:
    repository = BeirRepository(dataset_name=exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    if n_queries < 0:
        queries = repository.queries()
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    else:
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(n_queries))

    providers = [exp_config.connector_name(index) for index in exp_config.provider_index_range()]

    run: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve_from_dataspace(
            consumer_index=1, providers=providers, embedding=embedding, exp_config=exp_config
        )

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run


async def main(exp_config: BaseExperimentConfig):
    n_queries = int(input("# of queries? (default: -1): "))

    run = await retrieve(exp_config, n_queries=n_queries)

    out_filename = f"exp1_{exp_config.DATASET_NAME}_frag.json"
    save_retrieve_result(run, out_filename)

    print(f"[INFO] Completed to save retrieval run to [{out_filename}]")


if __name__ == "__main__":
    exp_config = ExperimentConfig()

    rebuild_env = input("Rebuild experiment environment? (y/n): ")
    if rebuild_env in {"y", "Y"}:
        asyncio.run(deploy.main(exp_config))

    asyncio.run(main(exp_config))
