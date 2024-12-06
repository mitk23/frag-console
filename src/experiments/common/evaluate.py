import ranx
from ranx import Qrels, Run

from experiments.config import BaseExperimentConfig


def evaluation_metrics(cutoff: int):
    return [
        "hits",
        f"hit_rate@{cutoff}",
        f"precision@{cutoff}",
        f"recall@{cutoff}",
        f"f1@{cutoff}",
        f"mrr@{cutoff}",
        f"ndcg@{cutoff}",
    ]


def evaluate(
    qrels: Qrels,
    run: Run,
    exp_config: BaseExperimentConfig = BaseExperimentConfig(),
    eval_cutoff: int | None = None,
) -> dict[str, float]:
    if eval_cutoff is None:
        eval_cutoff = exp_config.N_RETURN_DOCS

    metrics = evaluation_metrics(eval_cutoff)
    result = ranx.evaluate(qrels, run, metrics)
    return result


def compare(
    qrels: Qrels,
    run_list: list[Run],
    exp_config: BaseExperimentConfig = BaseExperimentConfig(),
    k: int | None = None,
) -> ranx.data_structures.Report:
    if k is None:
        k = exp_config.N_RETURN_DOCS

    metrics = evaluation_metrics(k)
    report = ranx.compare(qrels, runs=run_list, metrics=metrics)
    return report
