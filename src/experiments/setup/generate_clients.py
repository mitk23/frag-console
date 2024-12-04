import json
import os
import sys

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

from experiments.config import BaseExperimentConfig


def get_client(admin: KeycloakAdmin, client_uuid: str) -> dict[str, str]:
    return admin.get_client(client_uuid)


def create_client(admin: KeycloakAdmin, client_id: str) -> str:
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


def delete_client(admin: KeycloakAdmin, client_id: str):
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


def create_experiment_clients(admin: KeycloakAdmin, exp_config: BaseExperimentConfig):
    client_secret_dict: dict[str, str] = {}

    for index in range(1, exp_config.n_connectors() + 1):
        client_id = exp_config.connector_name(index)

        new_client_uuid = create_client(admin, client_id)
        new_client = get_client(admin, new_client_uuid)

        client_secret_dict[client_id] = new_client["secret"]

    return client_secret_dict


def delete_experiment_clients(admin: KeycloakAdmin, exp_config: BaseExperimentConfig):
    for index in range(1, exp_config.n_connectors() + 1):
        client_id = exp_config.connector_name(index)

        delete_client(admin, client_id)


def main(exp_config: BaseExperimentConfig):
    connection = KeycloakOpenIDConnection(
        server_url=exp_config.OAUTH_SERVER_URL,
        realm_name="frag",
        username="frag-admin",
        password="frag-admin",
        client_id="admin-cli",
    )
    admin = KeycloakAdmin(connection=connection)

    delete_experiment_clients(admin, exp_config)
    client_secret_dict = create_experiment_clients(admin, exp_config)

    clients_filename = os.path.join(exp_config.ENV_DIR, "clients.json")
    with open(clients_filename, "w") as file:
        json.dump(client_secret_dict, file, indent=2)

    print(f"[INFO] Generated {exp_config.n_connectors()} clients. Client secrets are saved to [{clients_filename}].")
