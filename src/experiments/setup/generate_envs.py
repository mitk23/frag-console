import json
import os

from experiments.config import BaseExperimentConfig


def generate_env_file(exp_config: BaseExperimentConfig, connector_index: int) -> None:
    connector_name = exp_config.connector_name(connector_index)

    with open(os.path.join(exp_config.ENV_DIR, "clients.json"), "r") as file:
        client_secret_dict: dict[str, str] = json.load(file)

    MY_CONNECTOR_NAME = connector_name
    MY_CONNECTOR_PORT = exp_config.connector_port(connector_index)
    MY_CONNECTOR_FQDN = exp_config.connector_location(connector_index)
    MY_CONNECTOR_API_KEY = exp_config.CONNECTOR_API_KEY

    OAUTH_SERVER_URL = exp_config.OAUTH_SERVER_URL
    OAUTH_REALM_NAME = "frag"
    OAUTH_CLIENT_ID = connector_name
    OAUTH_CLIENT_SECRET = client_secret_dict[connector_name]

    VECTOR_DB_SERVICE = exp_config.VECTOR_DB_SERVICE
    VECTOR_DB_URL = exp_config.vector_db_url()
    VECTOR_DB_INDEX_NAME = exp_config.vector_db_index_name(connector_index)
    VECTOR_DB_METADATA_TEXT_KEY = "text"

    ASSETS_CONFIG_PATH = "/app/core/configs/assets.json"
    CONNECTORS_CONFIG_PATH = "/app/core/configs/connectors.json"

    env_content = f"""
{MY_CONNECTOR_NAME=}
{MY_CONNECTOR_PORT=}
{MY_CONNECTOR_FQDN=}
{MY_CONNECTOR_API_KEY=}

{OAUTH_SERVER_URL=}
{OAUTH_REALM_NAME=}
{OAUTH_CLIENT_ID=}
{OAUTH_CLIENT_SECRET=}

{VECTOR_DB_SERVICE=}
{VECTOR_DB_URL=}
{VECTOR_DB_INDEX_NAME=}
{VECTOR_DB_METADATA_TEXT_KEY=}

{ASSETS_CONFIG_PATH=}
{CONNECTORS_CONFIG_PATH=}
""".replace("'", "")

    env_filename = os.path.join(exp_config.ENV_DIR, f"{connector_name}.env")
    with open(env_filename, "w") as env_file:
        env_file.write(env_content)


def main(exp_config: BaseExperimentConfig) -> None:
    os.makedirs(exp_config.ENV_DIR, exist_ok=True)

    for connector_index in range(1, exp_config.n_connectors() + 1):
        generate_env_file(exp_config, connector_index)
