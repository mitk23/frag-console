import json
import os
import pathlib
from pprint import pprint

import ranx
from ranx import Qrels, Run

from experiments import config
from load_beir import BeirRepository


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


def evaluate():
    dataset_name = "nq"

    repository = BeirRepository(dataset_name)
    qrels_dict = repository.qrels()
    print(f"{len(qrels_dict)=} | {len(qrels_dict.get('test0', []))=}")

    run_filename = f"{dataset_name}_run@10.json"
    run_dict = load_run_trec(run_filename=run_filename)
    print(f"{len(run_dict)=} | {len(run_dict.get('test0', []))=}")

    result = evaluate_retrieval(qrels_dict, run_dict)
    pprint(result)

    result_k5 = evaluate_retrieval(qrels_dict, run_dict, k=5)
    pprint(result_k5)

    result_k3 = evaluate_retrieval(qrels_dict, run_dict, k=3)
    pprint(result_k3)


if __name__ == "__main__":
    evaluate()
