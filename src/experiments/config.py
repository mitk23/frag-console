import os
import pathlib
from typing import Any, Iterable, Literal


class BaseExperimentConfig:
    ENV_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "envs")

    def __init__(self):
        # Experiment Conditions
        ## number of parties
        self.N_CONSUMERS: int = 3
        self.N_PROVIDERS: int = 4

        self.CONSUMER_INDEX_LOW: int = 1
        self.CONSUMER_INDEX_MEDIUM: int = 2
        self.CONSUMER_INDEX_HIGH: int = 3

        ## retrieval conditions
        self.N_REQUEST_DOCS: int = 10
        self.N_RETURN_DOCS: int = 10
        self.RERANK_METHOD: Literal["cosine", "naive"] = "naive"
        self.EXACT_SEARCH: bool = False

        ## evaluation dataset
        self.DATASET_NAME: Literal["fiqa", "nq", "trec-covid"] = "fiqa"

        # Experiment Enviroment Config
        self.CONNECTOR_IMAGE: str = "frag-connector:0.1.1"
        self.CONNECTOR_NAME_PREFIX: str = "exp-"
        self.CONNECTOR_BASE_PORT: int = 8000

        self.CONNECTOR_HOST: str = "172.26.16.10"
        self.CONNECTOR_API_KEY: str = "DefaultApiKey"

        self.OAUTH_SERVER_URL: str = "http://172.26.16.10:5000"

        self.VECTOR_DB_SERVICE: Literal["pinecone", "qdrant"] = "qdrant"

    def n_connectors(self) -> int:
        return self.N_CONSUMERS + self.N_PROVIDERS

    def consumer_index_range(self) -> Iterable[int]:
        return range(1, self.N_CONSUMERS + 1)

    def provider_index_range(self) -> Iterable[int]:
        return range(self.N_CONSUMERS + 1, self.n_connectors() + 1)

    def connector_name(self, connector_index: int) -> str:
        return f"{self.CONNECTOR_NAME_PREFIX}{connector_index}"

    def connector_port(self, connector_index: int) -> int:
        return self.CONNECTOR_BASE_PORT + connector_index

    def connector_location(self, connector_index: int) -> str:
        port = self.connector_port(connector_index)
        return f"http://{self.CONNECTOR_HOST}:{port}"

    def vector_db_url(self) -> str:
        if self.DATASET_NAME == "nq":
            return "http://172.26.16.20:6333"
        return "http://172.26.16.10:6333"

    def vector_db_index_name(self, connector_index: int) -> str:
        prefix = f"{self.DATASET_NAME}-{self.N_PROVIDERS}-"
        provider_index = connector_index - self.N_CONSUMERS
        return f"{prefix}{provider_index}"

    def __initial_file_assets(self) -> list[dict[str, Any]]:
        return [
            {
                "title": "c-asset",
                "description": "confidential dataset",
                "usage_policy": {"security_level": "confidential"},
                "distributions": [
                    {
                        "title": "confidential.txt",
                        "description": "document file",
                        "media_type": "text/plain",
                        "url": "http://172.26.16.10:1080/confidential.txt",
                    }
                ],
            },
            {
                "title": "r-asset",
                "description": "restricted dataset",
                "usage_policy": {"security_level": "restricted"},
                "distributions": [
                    {
                        "title": "restricted.txt",
                        "description": "document file",
                        "media_type": "text/plain",
                        "url": "http://172.26.16.10:1080/restricted.txt",
                    }
                ],
            },
            {
                "title": "p-asset",
                "description": "public dataset",
                "usage_policy": {"security_level": "public"},
                "distributions": [
                    {
                        "title": "public.txt",
                        "description": "document file",
                        "media_type": "text/plain",
                        "url": "http://172.26.16.10:1080/public.txt",
                    }
                ],
            },
        ]

    def initial_assets(self, connector_index: int) -> list[dict[str, Any]]:
        vector_db_index_name = self.vector_db_index_name(connector_index)
        initial_file_assets = self.__initial_file_assets()

        vectors_asset = {
            "title": f"qdrant-{vector_db_index_name}",
            "description": f"{vector_db_index_name} [all]",
            "usage_policy": {"security_level": "public"},
            "vectors": {"has_metadata": {}, "has_id": ["*"]},
        }
        initial_assets = initial_file_assets + [vectors_asset]
        return initial_assets

    def initial_connectors(self, connector_type: Literal["consumer", "provider"]) -> list[dict[str, str]]:
        if connector_type == "consumer":
            return [
                {
                    "id": self.connector_name(index),
                    "url": self.connector_location(index),
                    "trust": "low",
                }
                for index in self.provider_index_range()
            ]
        elif connector_type == "provider":
            return [
                # low trust consumer connector
                {
                    "id": self.connector_name(self.CONSUMER_INDEX_LOW),
                    "url": self.connector_location(self.CONSUMER_INDEX_LOW),
                    "trust": "low",
                },
                # medium trust consumer connector
                {
                    "id": self.connector_name(self.CONSUMER_INDEX_MEDIUM),
                    "url": self.connector_location(self.CONSUMER_INDEX_MEDIUM),
                    "trust": "medium",
                },
                # high trust consumer connector
                {
                    "id": self.connector_name(self.CONSUMER_INDEX_HIGH),
                    "url": self.connector_location(self.CONSUMER_INDEX_HIGH),
                    "trust": "high",
                },
            ]
        else:
            raise ValueError("invalid connector type")


######################
# Number of connectors
######################
# EXPERIMENT_NUM_CONSUMERS = 3
# EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX = 1
# EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX = 2
# EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX = 3

# EXPERIMENT_NUM_PROVIDERS = 4

# EXPERIMENT_NUM_CONNECTORS = EXPERIMENT_NUM_CONSUMERS + EXPERIMENT_NUM_PROVIDERS


#####################
# Experiment settings
#####################
# EXPERIMENT_CONNECTOR_IMAGE = "frag-connector:0.1.1"
# EXPERIMENT_CONNECTOR_NAME_PREFIX = "exp-"
# EXPERIMENT_CONNECTOR_BASE_PORT = 8000
# EXPERIMENT_ENV_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "envs")

# EXPERIMENT_TOP_K = 10
# EXPERIMENT_NUM_RETURN_KNOWLEDGES = 10
# EXPERIMENT_RERANK_METHOD = "naive"

# EXPERIMENT_DATASET_NAME = "fiqa"


###########################
# Connector common settings
###########################
# CONNECTOR_API_KEY = "DefaultApiKey"

# OAUTH_SERVER_URL = "http://172.26.16.10:5000"

# VECTOR_DB_SERVICE = "qdrant"
# VECTOR_DB_URL = "http://172.26.16.20:6333" if EXPERIMENT_DATASET_NAME == "nq" else "http://172.26.16.10:6333"
# VECTOR_DB_INDEX_NAME_PREFIX = f"{EXPERIMENT_DATASET_NAME}-{EXPERIMENT_NUM_PROVIDERS}-"


################
# Initial Assets
################
# INITIAL_FILE_ASSETS = [
#     # files
#     {
#         "title": "c-asset",
#         "description": "confidential dataset",
#         "usage_policy": {"security_level": "confidential"},
#         "distributions": [
#             {
#                 "title": "confidential.txt",
#                 "description": "document file",
#                 "media_type": "text/plain",
#                 "url": "http://172.26.16.10:1080/confidential.txt",
#             }
#         ],
#     },
#     {
#         "title": "r-asset",
#         "description": "restricted dataset",
#         "usage_policy": {"security_level": "restricted"},
#         "distributions": [
#             {
#                 "title": "restricted.txt",
#                 "description": "document file",
#                 "media_type": "text/plain",
#                 "url": "http://172.26.16.10:1080/restricted.txt",
#             }
#         ],
#     },
#     {
#         "title": "p-asset",
#         "description": "public dataset",
#         "usage_policy": {"security_level": "public"},
#         "distributions": [
#             {
#                 "title": "public.txt",
#                 "description": "document file",
#                 "media_type": "text/plain",
#                 "url": "http://172.26.16.10:1080/public.txt",
#             }
#         ],
#     },
# ]

####################
# Initial Connectors
####################
# INITIAL_CONNECTORS_FOR_CONSUMER = [
#     {
#         "id": ExperimentConfig.get_connector_name(connector_index=idx),
#         "url": ExperimentConfig.get_connector_location(connector_index=idx),
#         "trust": "low",
#     }
#     for idx in range(EXPERIMENT_NUM_CONSUMERS + 1, EXPERIMENT_NUM_CONNECTORS + 1)
# ]
# INITIAL_CONNECTORS_FOR_PROVIDER = [
#     # low trust consumer connector
#     {
#         "id": ExperimentConfig.get_connector_name(EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX),
#         "url": ExperimentConfig.get_connector_location(EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX),
#         "trust": "low",
#     },
#     # medium trust consumer connector
#     {
#         "id": ExperimentConfig.get_connector_name(EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX),
#         "url": ExperimentConfig.get_connector_location(EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX),
#         "trust": "medium",
#     },
#     # high trust consumer connector
#     {
#         "id": ExperimentConfig.get_connector_name(EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX),
#         "url": ExperimentConfig.get_connector_location(EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX),
#         "trust": "high",
#     },
# ]
