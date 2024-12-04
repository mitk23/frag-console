from typing import Literal

from experiments.config import BaseExperimentConfig


class ScalabilityExperimentConfig(BaseExperimentConfig):
    def __init__(
        self,
        dataset_name: Literal["fiqa", "nq", "trec-covid"] = "fiqa",
        n_providers: int = 4,
        n_request_docs: int = 10,
        n_return_docs: int = 10,
    ):
        super().__init__()

        self.DATASET_NAME = dataset_name
        self.N_PROVIDERS = n_providers
        self.N_REQUEST_DOCS = n_request_docs
        self.N_RETURN_DOCS = n_return_docs
