import asyncio

from tqdm import tqdm

from experiments.common import params, retrieve, save
from experiments.exp_basic.config import BasicExperimentConfig
from load_beir import BeirRepository


async def execute(exp_config: BasicExperimentConfig, n_queries: int = -1) -> dict[str, dict[str, float]]:
    repository = BeirRepository(exp_config.DATASET_NAME, db_url=exp_config.vector_db_url())

    if n_queries < 0:
        queries = repository.queries()
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))
    else:
        query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(n_queries))

    run: dict[str, dict[str, float]] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        knowledges = await retrieve.retrieve_from_qdrant(embedding=embedding, exp_config=exp_config)

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
    return run


async def main(exp_config: BasicExperimentConfig, output_filename: str):
    run = await execute(exp_config, n_queries=-1)

    save.save_output(run, output_filename)
    print(f"[INFO] Completed to save retrieval run to [{output_filename}]")


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    exact_search = params.input_exact_search()

    dataset_index = 1
    n_request_docs = 20

    exp_config = BasicExperimentConfig(
        dataset_name=dataset_name,
        dataset_index=dataset_index,
        n_request_docs=n_request_docs,
        exact_search=exact_search,
    )

    if exact_search:
        output_filename = f"exp1_{dataset_name}_baseline-exact.json"
    else:
        output_filename = f"exp1_{dataset_name}_baseline.json"

    asyncio.run(main(exp_config, output_filename))
