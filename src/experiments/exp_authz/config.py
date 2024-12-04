import json
import os
import random
from typing import Any, Literal

from experiments.config import BaseExperimentConfig


class AuthzExperimentConfig(BaseExperimentConfig):
    def __init__(
        self,
        dataset_name: Literal["fiqa", "nq", "trec-covid"] = "fiqa",
        n_request_docs: int = 10,
        n_return_docs: int = 10,
        security_rate: dict[str, float] = {"public": 0.6, "restricted": 0.3, "confidential": 0.1},
        split_seed: int = 42,
    ):
        super().__init__()

        self.DATASET_NAME = dataset_name
        self.N_REQUEST_DOCS = n_request_docs
        self.N_RETURN_DOCS = n_return_docs

        self.security_rate = security_rate
        self.split_seed = split_seed

    def vector_id_list(self, connector_index: int) -> list[str]:
        provider_index = connector_index - self.N_CONSUMERS

        each_id_file = os.path.join(self.ENV_DIR, f"{self.DATASET_NAME}-split{self.N_PROVIDERS}_ids.json")
        with open(each_id_file, "r") as file:
            each_id_dict: dict[str, list[int]] = json.load(file)

        vector_id_list = each_id_dict[f"{self.N_PROVIDERS}-{provider_index}"]
        vector_id_list = list(map(str, vector_id_list))
        return vector_id_list

    def split_vector_id_by_security(self, connector_index: int) -> dict[str, list[str]]:
        assert len(self.security_rate) == 3
        assert 0.999 <= sum(self.security_rate.values()) <= 1.001

        random.seed(self.split_seed)

        vector_id_list = self.vector_id_list(connector_index)
        each_security_vector_id_dict = {security: [] for security in self.security_rate.keys()}
        for vec_id in vector_id_list:
            subset_index = random.choices(
                range(len(self.security_rate)), weights=list(self.security_rate.values()), k=1
            )[0]
            if subset_index == 0:
                each_security_vector_id_dict["public"].append(vec_id)
            elif subset_index == 1:
                each_security_vector_id_dict["restricted"].append(vec_id)
            elif subset_index == 2:
                each_security_vector_id_dict["confidential"].append(vec_id)
            else:
                raise ValueError("invalid security rate")

        return each_security_vector_id_dict

    def initial_assets(self, connector_index: int) -> list[dict[str, Any]]:
        vector_db_index_name = self.vector_db_index_name(connector_index)
        initial_file_assets = self.initial_file_assets()

        each_security_vector_id_dict = self.split_vector_id_by_security(connector_index)

        vector_assets = [
            {
                "title": f"qdrant-{vector_db_index_name}-public",
                "description": f"{vector_db_index_name} [public]",
                "usage_policy": {"security_level": "public"},
                "vectors": {"has_metadata": {}, "has_id": each_security_vector_id_dict["public"]},
            },
            {
                "title": f"qdrant-{vector_db_index_name}-restricted",
                "description": f"{vector_db_index_name} [restricted]",
                "usage_policy": {"security_level": "restricted"},
                "vectors": {"has_metadata": {}, "has_id": each_security_vector_id_dict["restricted"]},
            },
            {
                "title": f"qdrant-{vector_db_index_name}-confidential",
                "description": f"{vector_db_index_name} [confidential]",
                "usage_policy": {"security_level": "confidential"},
                "vectors": {"has_metadata": {}, "has_id": each_security_vector_id_dict["confidential"]},
            },
        ]
        initial_assets = initial_file_assets + vector_assets
        return initial_assets
