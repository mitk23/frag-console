import pathlib

from ranx import Qrels, Run

from experiments.common import evaluate, params, save
from experiments.exp_basic.config import BasicExperimentConfig
from load_beir import BeirRepository


def load_run_baseline(dataset_name: str, exact_search: bool = False) -> Run | None:
    if exact_search:
        run_fname = f"exp1_{dataset_name}_baseline-exact.json"
    else:
        run_fname = f"exp1_{dataset_name}_baseline.json"

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_path = src_dir.joinpath("outputs", run_fname)

    if run_path.exists():
        return Run.from_file(run_path)
    return None


def evaluate_baseline(qrels: Qrels, exp_config: BasicExperimentConfig, eval_cutoff: int) -> dict[str, float] | None:
    run = load_run_baseline(exp_config.DATASET_NAME, exp_config.EXACT_SEARCH)
    if run is None:
        return None

    scores = evaluate.evaluate(qrels, run, exp_config=exp_config, eval_cutoff=eval_cutoff)
    return scores


def load_run_frag(
    dataset_name: str, dataset_index: int = 1, n_request_docs: int = 20, exact_search: bool = False
) -> Run | None:
    if exact_search:
        run_fname = f"exp1_{dataset_name}-{dataset_index}_nreq{n_request_docs}_frag-exact.json"
    else:
        run_fname = f"exp1_{dataset_name}-{dataset_index}_nreq{n_request_docs}_frag.json"

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_path = src_dir.joinpath("outputs", run_fname)

    if run_path.exists():
        return Run.from_file(run_path)
    return None


def evaluate_frag(qrels: Qrels, exp_config: BasicExperimentConfig, eval_cutoff: int) -> dict[str, float] | None:
    run = load_run_frag(
        exp_config.DATASET_NAME, exp_config.DATASET_INDEX, exp_config.N_REQUEST_DOCS, exp_config.EXACT_SEARCH
    )
    if run is None:
        return None

    scores = evaluate.evaluate(qrels, run, exp_config=exp_config, eval_cutoff=eval_cutoff)
    return scores


def evaluate_average_frag(
    qrels: Qrels, exp_config: BasicExperimentConfig, n_dataset: int, eval_cutoff: int
) -> dict[str, float] | None:
    metrics = evaluate.evaluation_metrics(eval_cutoff)

    average_scores: dict[str, float] = {metric: 0 for metric in metrics}
    for dataset_index in range(1, n_dataset + 1):
        exp_config.DATASET_INDEX = dataset_index
        scores = evaluate_frag(qrels, exp_config, eval_cutoff)
        if scores is None:
            continue

        for metric, score in scores.items():
            average_scores[metric] += score

    average_scores = {_: score / n_dataset for _, score in average_scores.items()}
    return average_scores


def main(exp_config: BasicExperimentConfig, n_dataset: int, output_filename: str):
    repository = BeirRepository(exp_config.DATASET_NAME, exp_config.vector_db_url())
    qrels = Qrels.from_dict(repository.qrels())

    eval_cutoff_list = [20, 10, 5, 3]

    evaluation_result: dict[str, dict[str, float]] = {}
    for eval_cutoff in eval_cutoff_list:
        if eval_cutoff > exp_config.N_REQUEST_DOCS:
            continue

        score_dict: dict[str, float] = {}
        # ANN
        exp_config.EXACT_SEARCH = False

        score_dict["baseline"] = evaluate_baseline(qrels, exp_config, eval_cutoff=eval_cutoff)
        score_dict["frag"] = evaluate_average_frag(qrels, exp_config, n_dataset, eval_cutoff=eval_cutoff)

        # exact
        exp_config.EXACT_SEARCH = True

        score_dict["baseline-exact"] = evaluate_baseline(qrels, exp_config, eval_cutoff=eval_cutoff)
        score_dict["frag-exact"] = evaluate_average_frag(qrels, exp_config, n_dataset, eval_cutoff=eval_cutoff)

        evaluation_result[f"@{eval_cutoff}"] = score_dict

    save.save_output(evaluation_result, output_filename)
    print(f"[INFO] Completed to save retrieval scores to [{output_filename}]")


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    n_dataset = params.input_num_dataset()
    n_request_docs = params.input_num_request_documents()

    exp_config = BasicExperimentConfig(dataset_name=dataset_name, n_request_docs=n_request_docs)

    output_filename = f"exp1_{dataset_name}_nreq{n_request_docs}_scores.json"

    main(exp_config, n_dataset, output_filename)
