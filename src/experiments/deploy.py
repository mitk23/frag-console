import subprocess
import time

from experiments.config import BaseExperimentConfig
from experiments.setup import generate_clients, generate_compose, generate_envs, initialize


async def main(exp_config: BaseExperimentConfig):
    print("Removing old enviroments...\n")
    subprocess.run(["docker", "compose", "-f", "compose.experiment.yaml", "down"], check=True)
    print("-" * 30)

    print("Generating Enviroments...\n")

    generate_clients.main(exp_config)
    generate_envs.main(exp_config)
    generate_compose.main(exp_config)

    print("-" * 30)

    print("Creating new enviroments...\n")
    subprocess.run(["docker", "compose", "-f", "compose.experiment.yaml", "up", "-d"], check=True)
    print("-" * 30)

    time.sleep(10.0)

    await initialize.main(exp_config)
