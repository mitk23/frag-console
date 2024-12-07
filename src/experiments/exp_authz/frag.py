import asyncio
from typing import Literal

from tqdm import tqdm

from experiments import deploy
from experiments.common import params, retrieve, save
from experiments.exp_authz.config import AuthzExperimentConfig
from load_beir import BeirRepository


async def execute(consumer_index: Literal[1, 2, 3], exp_config: AuthzExperimentConfig) -> dict[str, dict[str, float]]:
    repository = BeirRepository(dataset_name=exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    queries = repository.queries()
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))

    providers = [exp_config.connector_name(index) for index in exp_config.provider_index_range()]

    run: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve.retrieve_from_dataspace(
            consumer_index=consumer_index, providers=providers, embedding=embedding, exp_config=exp_config
        )

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run


async def main_task(
    consumer_trust: Literal["low", "medium", "high"], exp_config: AuthzExperimentConfig, output_filename: str
):
    if consumer_trust == "low":
        consumer_index = exp_config.CONSUMER_INDEX_LOW
    elif consumer_trust == "medium":
        consumer_index = exp_config.CONSUMER_INDEX_MEDIUM
    elif consumer_trust == "high":
        consumer_index = exp_config.CONSUMER_INDEX_HIGH

    run = await execute(consumer_index, exp_config)

    save.save_output(run, output_filename)
    print(f"[INFO] Completed to save retrieval run to [{output_filename}]")


async def main(exp_config: AuthzExperimentConfig):
    dataset_name = exp_config.DATASET_NAME
    n_request_docs = exp_config.N_REQUEST_DOCS
    confidential_rate = exp_config.security_rate["confidential"]

    consumer_trust_list = ["low", "high"]
    async with asyncio.TaskGroup() as tg:
        for consumer_trust in consumer_trust_list:
            output_filename = (
                f"exp2_{dataset_name}_nreq{n_request_docs}_rate{int(confidential_rate * 100)}_{consumer_trust}.json"
            )

            tg.create_task(main_task(consumer_trust, exp_config, output_filename))


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    n_request_docs = params.input_num_request_documents()

    split_seed = 42

    confidential_rate_list = [0.4, 0.2, 0.1, 0.05, 0.025]
    for rate in confidential_rate_list:
        security_rate = {"public": 1 - rate, "restricted": 0, "confidential": rate}

        exp_config = AuthzExperimentConfig(
            dataset_name=dataset_name, n_request_docs=n_request_docs, security_rate=security_rate, split_seed=split_seed
        )

        # deploy connectors
        print(f"\n{'=' * 50}\n", f"[{rate=}] Deploying experiment environment...", f"\n{'=' * 50}\n")
        asyncio.run(deploy.main(exp_config))

        print(f"\n{'=' * 50}\n", f"[{rate=}] Running experiment...", f"\n{'=' * 50}\n")
        asyncio.run(main(exp_config))
