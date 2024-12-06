from typing import Literal

from experiments.config import BaseExperimentConfig


class BasicExperimentConfig(BaseExperimentConfig):
    def __init__(
        self,
        dataset_name: Literal["fiqa", "nq", "trec-covid"] = "fiqa",
        dataset_index: Literal[1, 2, 3, 4, 5] = 1,
        n_request_docs: int = 20,
        exact_search: bool = False,
    ):
        super().__init__()

        self.DATASET_NAME = dataset_name
        self.DATASET_INDEX = dataset_index
        self.N_REQUEST_DOCS = n_request_docs
        self.EXACT_SEARCH = exact_search

        self.N_PROVIDERS = 4
        self.N_RETURN_DOCS = 20
        self.RERANK_METHOD = "naive"

    def vector_db_index_name(self, connector_index: int) -> str:
        prefix = f"{self.DATASET_NAME}-{self.N_PROVIDERS}-"
        shuffix = f"-{self.DATASET_INDEX}"
        provider_index = connector_index - self.N_CONSUMERS
        return f"{prefix}{provider_index}{shuffix}"
