import os

import yaml

from experiments import config
from experiments.config import ExperimentSettings


def generate_compose(n_containers: int = config.EXPERIMENT_NUM_CONNECTORS) -> None:
    services = {}
    for idx in range(1, n_containers + 1):
        connector_name = ExperimentSettings.get_connector_name(connector_index=idx)

        services[connector_name] = {
            "image": config.EXPERIMENT_CONNECTOR_IMAGE,
            "container_name": f"frag-{connector_name}",
            "env_file": os.path.join("src/experiments/envs", f"{connector_name}.env"),
            "restart": "unless-stopped",
            "ports": [f"{ExperimentSettings.get_connector_port(connector_index=idx)}:8000"],
        }

    compose = {"services": services}

    with open("compose.experiment.yaml", "w") as file:
        yaml.safe_dump(compose, file)


def main():
    n_containers = int(input("# of Connectors: "))

    generate_compose(n_containers=n_containers)


if __name__ == "__main__":
    main()
