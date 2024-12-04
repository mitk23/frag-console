import os

import yaml

from experiments.config import BaseExperimentConfig


def main(exp_config: BaseExperimentConfig) -> None:
    services = {}
    for connector_index in range(1, exp_config.n_connectors() + 1):
        connector_name = exp_config.connector_name(connector_index)

        services[connector_name] = {
            "image": exp_config.CONNECTOR_IMAGE,
            "container_name": f"frag-{connector_name}",
            "env_file": os.path.join("src/experiments/envs", f"{connector_name}.env"),
            "restart": "unless-stopped",
            "ports": [f"{exp_config.connector_port(connector_index)}:8000"],
        }

    compose = {"services": services}

    with open("compose.experiment.yaml", "w") as file:
        yaml.safe_dump(compose, file)
