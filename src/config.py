LOCATIONS = {
    "frag-connector-test": "http://host.docker.internal:8000",
    "frag-connector-01": "http://172.26.16.10:8000",
    "frag-connector-03": "http://172.26.16.20:8000",
}

API_KEYS = {
    "frag-connector-test": "DefaultApiKey",
    "frag-connector-01": "ApiKey01",
    "frag-connector-03": "ApiKey03",
}

QDRANT_URL = "http://172.26.16.10:6333"


def qdrant_corpus_collection_name(dataset_name: str):
    return f"{dataset_name}-test"


def qdrant_query_collection_name(dataset_name: str):
    return f"{dataset_name}-query-test"
