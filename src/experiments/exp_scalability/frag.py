import asyncio
import time

from tqdm import tqdm

from experiments import deploy
from experiments.config import BaseExperimentConfig
from experiments.exp_scalability.config import ScalabilityExperimentConfig
from experiments.retrieve import retrieve_from_dataspace, save_retrieve_latency, save_retrieve_result
from load_beir import BeirRepository


async def retrieve(exp_config: BaseExperimentConfig) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    repository = BeirRepository(dataset_name=exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    # queries = repository.queries()
    # query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(10))

    providers = [exp_config.connector_name(index) for index in exp_config.provider_index_range()]

    run: dict[str, dict[str, float]] = {}
    latency_dict: dict[str, float] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        time_start = time.perf_counter()
        knowledges = await retrieve_from_dataspace(
            consumer_index=1, providers=providers, embedding=embedding, exp_config=exp_config
        )
        time_end = time.perf_counter()

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
        latency_dict[query_id] = time_end - time_start

    return run, latency_dict


async def main(exp_config: BaseExperimentConfig):
    run, latency_dict = await retrieve(exp_config)

    run_filename = f"exp4_run_{exp_config.DATASET_NAME}_n{exp_config.N_PROVIDERS}.json"
    save_retrieve_result(run, run_filename)

    n_query = len(latency_dict)
    latency_total = sum(latency_dict.values())
    latency_mean = latency_total / n_query

    latency_result = {"n_query": n_query, "total": latency_total, "mean": latency_mean}

    latency_filename = f"exp4_latency_{exp_config.DATASET_NAME}.json"
    latency_title = f"frag-n{exp_config.N_PROVIDERS}"
    save_retrieve_latency(latency_result, key_title=latency_title, filename=latency_filename)

    print(f"[INFO] Completed to save retrieval latency to [{latency_filename}]")


if __name__ == "__main__":
    n_providers_list = [2, 4, 6, 8, 10, 16, 24, 32]
    dataset_name = "fiqa"

    for n_providers in tqdm(n_providers_list):
        exp_config = ScalabilityExperimentConfig(n_providers=n_providers, dataset_name=dataset_name)

        asyncio.run(deploy.main(exp_config))
        asyncio.run(main(exp_config))
