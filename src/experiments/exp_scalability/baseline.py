import asyncio
import time

from tqdm import tqdm

from experiments.config import BaseExperimentConfig
from experiments.exp_scalability.config import ScalabilityExperimentConfig
from experiments.retrieve import retrieve_from_qdrant, save_retrieve_latency
from load_beir import BeirRepository


async def retrieve(exp_config: BaseExperimentConfig) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    repository = BeirRepository(exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    queries = repository.queries()
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))

    run: dict[str, dict[str, float]] = {}
    latencies: dict[str, float] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        time_start = time.perf_counter()
        knowledges = await retrieve_from_qdrant(embedding=embedding, exp_config=exp_config)
        time_end = time.perf_counter()

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
        latencies[query_id] = time_end - time_start

    return run, latencies


async def main(exp_config: BaseExperimentConfig):
    _, latencies = await retrieve(exp_config)

    n_query = len(latencies)
    latency_total = sum(latencies.values())
    latency_mean = latency_total / n_query

    latency_result = {"n_query": n_query, "total": latency_total, "mean": latency_mean}

    latency_filename = f"exp4_latency_{exp_config.DATASET_NAME}.json"
    save_retrieve_latency(latency_result, key_title="baseline", filename=latency_filename)

    print(f"[INFO] Completed to save retrieval latency to [{latency_filename}]")


if __name__ == "__main__":
    dataset_names = ["fiqa", "nq", "trec-covid"]

    for dataset_name in dataset_names:
        exp_config = ScalabilityExperimentConfig(dataset_name=dataset_name)
        asyncio.run(main(exp_config))
