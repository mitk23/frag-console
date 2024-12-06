import json
import os
import pathlib

from ranx import Qrels, Run

from experiments.common import evaluate, params
from experiments.exp_basic.config import BasicExperimentConfig
from load_beir import BeirRepository


def load_run_baseline(dataset_name: str, exact_search: bool = False) -> Run:
    if exact_search:
        _fname = f"exp1_{dataset_name}_baseline-exact.json"
    else:
        _fname = f"exp1_{dataset_name}_baseline.json"

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_fname = os.path.join(src_dir, "outputs", _fname)

    return Run.from_file(run_fname)


def get_score_baseline(exp_config: BasicExperimentConfig, eval_cutoff: int) -> dict[str, float]:
    repository = BeirRepository(exp_config.DATASET_NAME, exp_config.vector_db_url())

    qrels = Qrels.from_dict(repository.qrels())
    run = load_run_baseline(exp_config.DATASET_NAME, exp_config.EXACT_SEARCH)

    scores = evaluate.evaluate(qrels, run, exp_config=exp_config, eval_cutoff=eval_cutoff)
    return scores


def load_run_frag(
    dataset_name: str, dataset_index: int = 1, n_request_docs: int = 20, exact_search: bool = False
) -> Run:
    if exact_search:
        _fname = f"exp1_{dataset_name}-{dataset_index}_nreq{n_request_docs}_frag-exact.json"
    else:
        _fname = f"exp1_{dataset_name}-{dataset_index}_nreq{n_request_docs}_frag.json"

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_fname = os.path.join(src_dir, "outputs", _fname)

    return Run.from_file(run_fname)


def get_score_frag(exp_config: BasicExperimentConfig, eval_cutoff: int) -> dict[str, float]:
    repository = BeirRepository(exp_config.DATASET_NAME, exp_config.vector_db_url())

    qrels = Qrels.from_dict(repository.qrels())
    run = load_run_frag(
        exp_config.DATASET_NAME, exp_config.DATASET_INDEX, exp_config.N_REQUEST_DOCS, exp_config.EXACT_SEARCH
    )

    scores = evaluate.evaluate(qrels, run, exp_config=exp_config, eval_cutoff=eval_cutoff)
    return scores


def average_score_frag(
    dataset_name: str, n_dataset: int, n_request_docs: int, exact_search: bool, eval_cutoff: int
) -> dict[str, float]:
    metrics = evaluate.evaluation_metrics(eval_cutoff)

    average_result_dict: dict[str, float] = {metric: 0 for metric in metrics}
    for dataset_index in range(1, n_dataset + 1):
        exp_config = BasicExperimentConfig(
            dataset_name=dataset_name,
            dataset_index=dataset_index,
            n_request_docs=n_request_docs,
            exact_search=exact_search,
        )
        scores = get_score_frag(exp_config, eval_cutoff)
        for metric, score in scores.items():
            average_result_dict[metric] += score

    average_result_dict = {_: score / n_dataset for _, score in average_result_dict.items()}
    return average_result_dict


def main(exp_config: BasicExperimentConfig, n_dataset: int, output_filename: str):
    eval_cutoff_list = [20, 10, 5, 3]

    evaluation_result: dict[str, dict[str, float]] = {}
    for eval_cutoff in eval_cutoff_list:
        if eval_cutoff > exp_config.N_REQUEST_DOCS:
            continue

        score_dict: dict[str, float] = {}
        # ANN
        exp_config.EXACT_SEARCH = False

        score_dict["baseline"] = get_score_baseline(exp_config, eval_cutoff=eval_cutoff)
        score_dict["frag"] = average_score_frag(
            dataset_name=exp_config.DATASET_NAME,
            n_dataset=n_dataset,
            n_request_docs=exp_config.N_REQUEST_DOCS,
            exact_search=exp_config.EXACT_SEARCH,
            eval_cutoff=eval_cutoff,
        )

        # exact
        exp_config.EXACT_SEARCH = True

        score_dict["baseline-exact"] = get_score_baseline(exp_config, eval_cutoff=eval_cutoff)
        score_dict["frag-exact"] = average_score_frag(
            dataset_name=exp_config.DATASET_NAME,
            n_dataset=n_dataset,
            n_request_docs=exp_config.N_REQUEST_DOCS,
            exact_search=exp_config.EXACT_SEARCH,
            eval_cutoff=eval_cutoff,
        )

        evaluation_result[f"@{eval_cutoff}"] = score_dict

    print(json.dumps(evaluation_result, indent=2))

    with open(output_filename, "w") as file:
        json.dump(evaluation_result, file, indent=2)


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    n_dataset = params.input_num_dataset()
    n_request_docs = params.input_num_request_documents()

    exp_config = BasicExperimentConfig(dataset_name=dataset_name, n_request_docs=n_request_docs)

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    output_filename = os.path.join(src_dir, "outputs", f"exp1_{dataset_name}_nreq{n_request_docs}_result.json")

    main(exp_config, n_dataset, output_filename)
