import time
from typing import Any

from tqdm import tqdm

from apis.dataspace import retrieve_knowledge
from apis.qdrant import QdrantQueryService
from experiments.config import BaseExperimentConfig
from load_beir import BeirRepository


async def retrieve_from_dataspace(
    consumer_index: int,
    providers: list[str],
    embedding: list[float],
    exp_config: BaseExperimentConfig | None = BaseExperimentConfig(),
) -> list[dict[str, Any]]:
    fqdn = exp_config.connector_location(consumer_index)

    knowledges = await retrieve_knowledge(
        fqdn,
        embedding=embedding,
        api_key=exp_config.CONNECTOR_API_KEY,
        providers=providers,
        top_k=exp_config.N_REQUEST_DOCS,
        return_num_knowledges=exp_config.N_RETURN_DOCS,
        rerank_method=exp_config.RERANK_METHOD,
        exact_search=exp_config.EXACT_SEARCH,
    )
    return knowledges


async def retrieve_from_qdrant(
    embedding: list[float], exp_config: BaseExperimentConfig | None = BaseExperimentConfig()
) -> list[dict[str, Any]]:
    qdrant_query_service = QdrantQueryService(
        qdrant_url=exp_config.vector_db_url(), collection_name=exp_config.DATASET_NAME
    )

    knowledges = await qdrant_query_service.search_nearest(
        embedding=embedding,
        return_num_knowledges=exp_config.N_RETURN_DOCS,
        exact_search=exp_config.EXACT_SEARCH,
    )
    return knowledges


async def retrieve_beir_from_dataspace(
    consumer_index: int, exp_config: BaseExperimentConfig | None = BaseExperimentConfig(), return_latency: bool = False
) -> dict[str, dict[str, float]] | tuple[dict[str, dict[str, float]], dict[str, float]]:
    dataset_name = exp_config.DATASET_NAME
    qdrant_url = exp_config.vector_db_url()

    repository = BeirRepository(dataset_name=dataset_name, db_url=qdrant_url)

    queries = repository.queries()
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))

    consumer_fqdn = exp_config.connector_location(consumer_index)
    providers = [exp_config.connector_name(index) for index in exp_config.provider_index_range()]

    run: dict[str, dict[str, float]] = {}
    latency_dict: dict[str, float] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        time_start = time.perf_counter()
        knowledges = await retrieve_knowledge(
            consumer_fqdn,
            embedding=embedding,
            api_key=exp_config.CONNECTOR_API_KEY,
            providers=providers,
            top_k=exp_config.N_REQUEST_DOCS,
            return_num_knowledges=exp_config.N_RETURN_DOCS,
            rerank_method=exp_config.RERANK_METHOD,
            exact_search=exp_config.EXACT_SEARCH,
        )
        time_end = time.perf_counter()

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
        latency_dict[query_id] = time_end - time_start

    if return_latency:
        return run, latency_dict
    return run


async def retrieve_beir_from_qdrant(
    exp_config: BaseExperimentConfig | None = BaseExperimentConfig(), return_latency: bool = False
) -> dict[str, dict[str, float]] | tuple[dict[str, dict[str, float]], dict[str, float]]:
    dataset_name = exp_config.DATASET_NAME
    qdrant_url = exp_config.vector_db_url()

    qdrant_query_service = QdrantQueryService(qdrant_url=qdrant_url, collection_name=dataset_name)

    repository = BeirRepository(dataset_name=dataset_name, db_url=qdrant_url)

    queries = repository.queries()
    query_embeddings_dict = await repository.find_query_embeddings_by_index(query_indices=range(len(queries)))

    run: dict[str, dict[str, float]] = {}
    latency_dict: dict[str, float] = {}
    for query_id, embedding in tqdm(query_embeddings_dict.items(), desc="query"):
        time_start = time.perf_counter()
        knowledges = await qdrant_query_service.search_nearest(
            embedding=embedding,
            return_num_knowledges=exp_config.N_RETURN_DOCS,
            exact_search=exp_config.EXACT_SEARCH,
        )
        time_end = time.perf_counter()

        run[query_id] = {
            repository.find_document_id_by_index(int(knowledge["id"])): knowledge["score"] for knowledge in knowledges
        }
        latency_dict[query_id] = time_end - time_start

    if return_latency:
        return run, latency_dict
    return run
