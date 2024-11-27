import json
import os
import sys

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

from experiments import config

connection = KeycloakOpenIDConnection(
    server_url=config.OAUTH_SERVER_URL,
    realm_name="frag",
    username="frag-admin",
    password="frag-admin",
    client_id="admin-cli",
)
admin = KeycloakAdmin(connection=connection)


def generate_client_id(index: int) -> str:
    return f"{config.EXPERIMENT_CONNCTOR_NAME_PREFIX}{index}"


def get_client(client_uuid: str) -> dict[str, str]:
    return admin.get_client(client_uuid)


def create_client(client_id: str) -> str:
    new_client = {
        "clientId": client_id,
        "enabled": True,
        "protocol": "openid-connect",
        "publicClient": False,
        "authorizationServicesEnabled": True,
        "standardFlowEnabled": True,
        "directAccessGrantsEnabled": True,
        "serviceAccountsEnabled": True,
    }

    try:
        created_client_uuid = admin.create_client(new_client, skip_exists=True)
    except Exception as error:
        print(f"[ERROR] Failed to create keycloak client [{client_id}]")
        print(f"{error=}")
        sys.exit(1)

    print(f"[INFO] Succeeded to create new client [{client_id}]")
    return created_client_uuid


def delete_client(client_id: str):
    client_uuid = admin.get_client_id(client_id)
    if client_uuid is None:
        return

    try:
        _ = admin.delete_client(client_uuid)
    except Exception as error:
        print(f"[ERROR] Failed to delete keycloak client [{client_id}]")
        print(f"{error=}")
        sys.exit(1)

    print(f"[INFO] Succeeded to delete client [{client_id}]")


def create_experiment_clients(n_clients: int = 10):
    client_secret_dict: dict[str, str] = {}

    for idx in range(1, n_clients + 1):
        client_id = generate_client_id(index=idx)

        new_client_uuid = create_client(client_id)
        new_client = get_client(new_client_uuid)

        client_secret_dict[client_id] = new_client["secret"]

    return client_secret_dict


def delete_experiment_clients(n_clients: int = 10):
    for idx in range(1, n_clients + 1):
        client_id = generate_client_id(index=idx)

        delete_client(client_id)


def generate_clients(n_clients: int = config.EXPERIMENT_NUM_CONNECTORS):
    delete_experiment_clients(n_clients=n_clients)

    client_secret_dict = create_experiment_clients(n_clients)

    clients_filename = os.path.join(config.EXPERIMENT_ENV_DIR, "clients.json")
    with open(clients_filename, "w") as file:
        json.dump(client_secret_dict, file, indent=2)

    print(f"[INFO] Generated {n_clients} clients. Client secrets are saved to [{clients_filename}].")


def main():
    n_clients = int(input("# of Connectors: "))

    generate_clients(n_clients=n_clients)


if __name__ == "__main__":
    main()
