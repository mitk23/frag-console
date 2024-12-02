import json
import os
import pathlib

import ranx
from ranx import Qrels, Run

from experiments import config


def load_run_trec(run_filename: str) -> dict[str, dict[str, float]]:
    src_dir = pathlib.Path(__file__).parent.parent.absolute()
    filename = os.path.join(src_dir, "outputs", run_filename)

    with open(filename, "r") as file:
        run_dict: dict[str, dict[str, float]] = json.load(file)
    return run_dict


def evaluate_retrieval(
    qrels_dict: dict[str, dict[str, float]],
    run_dict: dict[str, dict[str, float]],
    k: int = config.EXPERIMENT_NUM_RETURN_KNOWLEDGES,
) -> dict[str, float]:
    qrels = Qrels(qrels_dict)
    run = Run(run_dict)

    metrics = ["hits", f"hit_rate@{k}", f"precision@{k}", f"recall@{k}", f"f1@{k}", f"mrr@{k}", f"ndcg@{k}"]

    result = ranx.evaluate(qrels, run, metrics)
    return result


def compare_retrieval(
    qrels: Qrels,
    run_list: list[Run],
    k: int = config.EXPERIMENT_NUM_RETURN_KNOWLEDGES,
) -> ranx.data_structures.Report:
    metrics = ["hits", f"hit_rate@{k}", f"precision@{k}", f"recall@{k}", f"f1@{k}", f"mrr@{k}", f"ndcg@{k}"]

    report = ranx.compare(qrels, runs=run_list, metrics=metrics)
    return report
