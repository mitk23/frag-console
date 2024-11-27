import os
import pathlib

######################
# Number of connectors
######################
EXPERIMENT_NUM_CONSUMERS = 3
EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX = 1
EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX = 2
EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX = 3

EXPERIMENT_NUM_PROVIDERS = 10

EXPERIMENT_NUM_CONNECTORS = EXPERIMENT_NUM_CONSUMERS + EXPERIMENT_NUM_PROVIDERS


#####################
# Experiment settings
#####################
EXPERIMENT_CONNECTOR_IMAGE = "frag-connector:0.1.1"
EXPERIMENT_CONNCTOR_NAME_PREFIX = "exp-"
EXPERIMENT_CONNECTOR_BASE_PORT = 8000
EXPERIMENT_ENV_DIR = os.path.join(pathlib.Path(__file__).parent.absolute(), "envs")

EXPERIMENT_CONNECTOR_LOCATIONS = {
    idx: f"http://172.26.16.10:{EXPERIMENT_CONNECTOR_BASE_PORT + idx}"
    for idx in range(1, EXPERIMENT_NUM_CONNECTORS + 1)
}

EXPERIMENT_TOP_K = 10
EXPERIMENT_NUM_RETURN_KNOWLEDGES = 30
EXPERIMENT_RERANK_METHOD = "cosine"

EXPERIMENT_DATASET_NAME = "nq"

###########################
# Connector common settings
###########################
CONNECTOR_API_KEY = "DefaultApiKey"

OAUTH_SERVER_URL = "http://172.26.16.10:5000"

VECTOR_DB_SERVICE = "qdrant"
VECTOR_DB_URL = "http://172.26.16.10:6333"
VECTOR_DB_INDEX_NAME = f"{EXPERIMENT_DATASET_NAME}-test"


################
# Initial Assets
################
INITIAL_ASSETS = [
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
    # vectors
    {
        "title": f"qdrant-{VECTOR_DB_INDEX_NAME}",
        "description": f"{VECTOR_DB_INDEX_NAME} [all]",
        "usage_policy": {"security_level": "public"},
        "vectors": {"has_metadata": {}, "has_id": ["*"]},
    },
]

####################
# Initial Connectors
####################
INITIAL_CONNECTORS_FOR_CONSUMER = [
    {
        "id": f"{EXPERIMENT_CONNCTOR_NAME_PREFIX}{idx}",
        "url": EXPERIMENT_CONNECTOR_LOCATIONS[idx],
        "trust": "low",
    }
    for idx in range(EXPERIMENT_NUM_CONSUMERS + 1, EXPERIMENT_NUM_CONNECTORS + 1)
]
INITIAL_CONNECTORS_FOR_PROVIDER = [
    # low trust consumer connector
    {
        "id": f"{EXPERIMENT_CONNCTOR_NAME_PREFIX}{EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX}",
        "url": EXPERIMENT_CONNECTOR_LOCATIONS[EXPERIMENT_LOW_TRUST_CONNECTOR_INDEX],
        "trust": "low",
    },
    # medium trust consumer connector
    {
        "id": f"{EXPERIMENT_CONNCTOR_NAME_PREFIX}{EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX}",
        "url": EXPERIMENT_CONNECTOR_LOCATIONS[EXPERIMENT_MEDIUM_TRUST_CONNECTOR_INDEX],
        "trust": "medium",
    },
    # high trust consumer connector
    {
        "id": f"{EXPERIMENT_CONNCTOR_NAME_PREFIX}{EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX}",
        "url": EXPERIMENT_CONNECTOR_LOCATIONS[EXPERIMENT_HIGH_TRUST_CONNECTOR_INDEX],
        "trust": "high",
    },
]

assert len(INITIAL_CONNECTORS_FOR_CONSUMER) == EXPERIMENT_NUM_PROVIDERS
assert len(INITIAL_CONNECTORS_FOR_PROVIDER) == EXPERIMENT_NUM_CONSUMERS
