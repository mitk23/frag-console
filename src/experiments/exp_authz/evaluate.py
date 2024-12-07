import os
import pathlib

from ranx import Qrels, Run

from experiments.common import evaluate, params, save
from experiments.exp_authz.config import AuthzExperimentConfig
from load_beir import BeirRepository


def load_run(dataset_name: str, n_request_docs: int, confidential_rate: float, consumer_trust: str) -> Run:
    fname = f"exp2_{dataset_name}_nreq{n_request_docs}_rate{int(confidential_rate * 100)}_{consumer_trust}.json"

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_fname = os.path.join(src_dir, "outputs", fname)

    return Run.from_file(run_fname)


def evaluate_score(
    qrels: Qrels, exp_config: AuthzExperimentConfig, confidential_rate: float, consumer_trust: str
) -> dict[str, float]:
    run = load_run(
        dataset_name=exp_config.DATASET_NAME,
        n_request_docs=exp_config.N_REQUEST_DOCS,
        confidential_rate=confidential_rate,
        consumer_trust=consumer_trust,
    )

    scores = evaluate.evaluate(qrels, run, exp_config=exp_config)
    return scores


def main(exp_config: AuthzExperimentConfig, output_filename: str):
    repository = BeirRepository(exp_config.DATASET_NAME, exp_config.vector_db_url())
    qrels = Qrels.from_dict(repository.qrels())

    confidential_rate_list = [0.4, 0.2, 0.1, 0.05, 0.025]
    consumer_trust_list = ["low", "high"]

    evaluation_result: dict[str, dict[str, float]] = {}
    for rate in confidential_rate_list:
        score_dict: dict[str, float] = {}

        for trust in consumer_trust_list:
            score_dict[trust] = evaluate_score(
                qrels, exp_config=exp_config, confidential_rate=rate, consumer_trust=trust
            )

        evaluation_result[f"{int(rate * 100)}%"] = score_dict

    save.save_output(evaluation_result, output_filename)
    print(f"[INFO] Completed to save result to [{output_filename}]")


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    n_request_docs = params.input_num_request_documents()

    exp_config = AuthzExperimentConfig(dataset_name=dataset_name, n_request_docs=n_request_docs)

    output_filename = f"exp2_{dataset_name}_nreq{n_request_docs}_scores.json"

    main(exp_config, output_filename)
