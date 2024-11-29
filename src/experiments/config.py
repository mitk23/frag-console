import os
import pathlib


class ExperimentSettings:
    CONNECTOR_HOST = "172.26.16.10"

    @staticmethod
    def get_connector_name(connector_index: int) -> str:
        return f"{EXPERIMENT_CONNECTOR_NAME_PREFIX}{connector_index}"

    @staticmethod
    def get_connector_port(connector_index: int) -> int:
        return EXPERIMENT_CONNECTOR_BASE_PORT + connector_index

    @staticmethod
    def get_connector_location(connector_index: int) -> str:
        port = ExperimentSettings.get_connector_port(connector_index)
        return f"http://{ExperimentSettings.CONNECTOR_HOST}:{port}"

    @staticmethod
    def get_vector_db_index_name(connector_index: int) -> str:
        provider_index = connector_index - EXPERIMENT_NUM_CONSUMERS
        return f"{VECTOR_DB_INDEX_NAME_PREFIX}{provider_index}"


######################
# Number of connectors
######################
EXPERIMENT_NUM_CONSUMERS = 3
EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX = 1
EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX = 2
EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX = 3

EXPERIMENT_NUM_PROVIDERS = 4

EXPERIMENT_NUM_CONNECTORS = EXPERIMENT_NUM_CONSUMERS + EXPERIMENT_NUM_PROVIDERS


#####################
# Experiment settings
#####################
EXPERIMENT_CONNECTOR_IMAGE = "frag-connector:0.1.1"
EXPERIMENT_CONNECTOR_NAME_PREFIX = "exp-"
EXPERIMENT_CONNECTOR_BASE_PORT = 8000
EXPERIMENT_ENV_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "envs")

EXPERIMENT_TOP_K = 10
EXPERIMENT_NUM_RETURN_KNOWLEDGES = 10
EXPERIMENT_RERANK_METHOD = "naive"

EXPERIMENT_DATASET_NAME = "nq"


###########################
# Connector common settings
###########################
CONNECTOR_API_KEY = "DefaultApiKey"

OAUTH_SERVER_URL = "http://172.26.16.10:5000"

VECTOR_DB_SERVICE = "qdrant"
VECTOR_DB_URL = "http://172.26.16.20:6333"
VECTOR_DB_INDEX_NAME_PREFIX = f"{EXPERIMENT_DATASET_NAME}-{EXPERIMENT_NUM_PROVIDERS}-"


################
# Initial Assets
################
INITIAL_FILE_ASSETS = [
    # files
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

####################
# Initial Connectors
####################
INITIAL_CONNECTORS_FOR_CONSUMER = [
    {
        "id": ExperimentSettings.get_connector_name(connector_index=idx),
        "url": ExperimentSettings.get_connector_location(connector_index=idx),
        "trust": "low",
    }
    for idx in range(EXPERIMENT_NUM_CONSUMERS + 1, EXPERIMENT_NUM_CONNECTORS + 1)
]
INITIAL_CONNECTORS_FOR_PROVIDER = [
    # low trust consumer connector
    {
        "id": ExperimentSettings.get_connector_name(EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX),
        "url": ExperimentSettings.get_connector_location(EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX),
        "trust": "low",
    },
    # medium trust consumer connector
    {
        "id": ExperimentSettings.get_connector_name(EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX),
        "url": ExperimentSettings.get_connector_location(EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX),
        "trust": "medium",
    },
    # high trust consumer connector
    {
        "id": ExperimentSettings.get_connector_name(EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX),
        "url": ExperimentSettings.get_connector_location(EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX),
        "trust": "high",
    },
]
