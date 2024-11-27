from experiments.setup.generate_clients import generate_clients
from experiments.setup.generate_compose import generate_compose
from experiments.setup.generate_envs import generate_envs


def setup() -> None:
    print("Generating Enviroments...\n")

    generate_clients()
    generate_envs()
    generate_compose()

    output = """\

Finished to set up experiment environment.
Please run connectors in docker container by the command below.

❯ docker compose -f compose.experiment.yaml up -d

"""
    print(output)


def main():
    setup()


if __name__ == "__main__":
    main()
