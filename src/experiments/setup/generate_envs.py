import json
import os

from experiments import config


def read_client_secret(client_name: str) -> str:
    with open(os.path.join(config.EXPERIMENT_ENV_DIR, "clients.json"), "r") as file:
        clients = json.load(file)
    return clients[client_name]


def generate_env_file(filename: str, connector_name: str, port: int) -> None:
    MY_CONNECTOR_NAME = connector_name
    MY_CONNECTOR_PORT = port
    MY_CONNECTOR_FQDN = f"http://localhost:{MY_CONNECTOR_PORT}"
    MY_CONNECTOR_API_KEY = config.CONNECTOR_API_KEY

    OAUTH_SERVER_URL = config.OAUTH_SERVER_URL
    OAUTH_REALM_NAME = "frag"
    OAUTH_CLIENT_ID = MY_CONNECTOR_NAME
    OAUTH_CLIENT_SECRET = read_client_secret(client_name=OAUTH_CLIENT_ID)

    VECTOR_DB_SERVICE = config.VECTOR_DB_SERVICE
    VECTOR_DB_URL = config.VECTOR_DB_URL
    VECTOR_DB_INDEX_NAME = config.VECTOR_DB_INDEX_NAME
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

    with open(filename, "w") as env_file:
        env_file.write(env_content)


def generate_envs(n_containers: int = config.EXPERIMENT_NUM_CONNECTORS) -> None:
    os.makedirs(config.EXPERIMENT_ENV_DIR, exist_ok=True)

    for idx in range(1, n_containers + 1):
        connector_name = f"{config.EXPERIMENT_CONNCTOR_NAME_PREFIX}{idx}"
        env_file = os.path.join(config.EXPERIMENT_ENV_DIR, f"{connector_name}.env")

        generate_env_file(
            filename=env_file, connector_name=connector_name, port=config.EXPERIMENT_CONNECTOR_BASE_PORT + idx
        )


def main():
    n_containers = int(input("# of Connectors: "))

    generate_envs(n_containers=n_containers)


if __name__ == "__main__":
    main()
