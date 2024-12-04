import json
import os
import pathlib
from typing import Any

from apis.dataspace import retrieve_knowledge
from apis.qdrant import QdrantQueryService

from .config import BaseExperimentConfig


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


def save_retrieve_result(run: dict[str, dict[str, float]], out_filename: str) -> None:
    src_dir = pathlib.Path(__file__).parent.parent.absolute()
    output_file = os.path.join(src_dir, "outputs", out_filename)

    with open(output_file, "w") as file:
        json.dump(run, file, indent=2)
