import json
import pathlib

SOURCE_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()


def save_env(env_dict: dict, env_fname: str) -> None:
    env_dir = SOURCE_DIR.joinpath("experiments/envs")
    env_path = env_dir.joinpath(env_fname)

    with open(env_path, "w") as file:
        json.dump(env_dict, file, indent=2)


def save_output(output: dict, out_fname: str) -> None:
    outputs_dir = SOURCE_DIR.joinpath("outputs")
    out_path = outputs_dir.joinpath(out_fname)

    with open(out_path, "w") as file:
        json.dump(output, file, indent=2)


def save_and_update_output(output: dict, key: str, out_fname: str) -> None:
    outputs_dir = SOURCE_DIR.joinpath("outputs")
    out_path = outputs_dir.joinpath(out_fname)

    if not out_path.exists():
        out_path.write_text(data="{}")

    with open(out_path, "r") as file:
        old_output = json.load(file)
    new_output = old_output | {key: output}

    with open(out_path, "w") as file:
        json.dump(new_output, file, indent=2)
