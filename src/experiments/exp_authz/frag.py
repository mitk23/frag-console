import asyncio
from typing import Literal

from tqdm import tqdm

from experiments import deploy
from experiments.config import BaseExperimentConfig
from experiments.exp_authz.config import AuthzExperimentConfig
from experiments.retrieve import retrieve_from_dataspace, save_retrieve_result
from load_beir import BeirRepository


async def retrieve(consumer_index: Literal[1, 2, 3], exp_config: BaseExperimentConfig) -> dict[str, dict[str, float]]:
    repository = BeirRepository(dataset_name=exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    # queries = repository.queries()
    # query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(3))

    providers = [exp_config.connector_name(index) for index in exp_config.provider_index_range()]

    run: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve_from_dataspace(
            consumer_index=consumer_index, providers=providers, embedding=embedding, exp_config=exp_config
        )

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run


async def main(consumer_trust: Literal["low", "medium", "high"], exp_config: BaseExperimentConfig):
    if consumer_trust == "low":
        consumer_index = exp_config.CONSUMER_INDEX_LOW
    elif consumer_trust == "medium":
        consumer_index = exp_config.CONSUMER_INDEX_MEDIUM
    elif consumer_trust == "high":
        consumer_index = exp_config.CONSUMER_INDEX_HIGH

    run = await retrieve(consumer_index, exp_config)

    out_filename = f"exp2_{exp_config.DATASET_NAME}_{consumer_trust}.json"
    save_retrieve_result(run, out_filename)

    print(f"[INFO] Completed to save retrieval run to [{out_filename}]")


if __name__ == "__main__":
    dataset_name = "fiqa"
    security_rate = {"public": 0.7, "restricted": 0.25, "confidential": 0.05}

    exp_config = AuthzExperimentConfig(dataset_name, security_rate=security_rate)

    # deploy connectors
    asyncio.run(deploy.main(exp_config))

    for consumer_trust in ["low", "medium", "high"]:
        asyncio.run(main(consumer_trust, exp_config))
