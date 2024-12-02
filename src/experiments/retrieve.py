from typing import Any

from apis.dataspace import retrieve_knowledge
from apis.qdrant import QdrantQueryService
from experiments import config
from experiments.config import ExperimentSettings


async def retrieve_from_dataspace(
    consumer_index: int,
    providers: list[str],
    embedding: list[float],
) -> list[dict[str, Any]]:
    fqdn = ExperimentSettings.get_connector_location(consumer_index)

    knowledges = await retrieve_knowledge(
        fqdn,
        embedding=embedding,
        api_key=config.CONNECTOR_API_KEY,
        providers=providers,
        top_k=config.EXPERIMENT_TOP_K,
        rerank_method=config.EXPERIMENT_RERANK_METHOD,
        return_num_knowledges=config.EXPERIMENT_NUM_RETURN_KNOWLEDGES,
    )
    return knowledges


async def retrieve_from_qdrant(
    embedding: list[float], collection_name: str = config.EXPERIMENT_DATASET_NAME, exact_search: bool = False
) -> list[dict[str, Any]]:
    qdrant_query_service = QdrantQueryService(collection_name)

    knowledges = await qdrant_query_service.search_nearest(
        embedding=embedding,
        return_num_knowledges=config.EXPERIMENT_NUM_RETURN_KNOWLEDGES,
        exact_search=exact_search,
    )
    return knowledges
