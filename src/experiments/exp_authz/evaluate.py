import os
import pathlib

from ranx import Qrels, Run

from experiments.config import BaseExperimentConfig
from experiments.evaluate import compare_retrieval
from experiments.exp_authz.config import AuthzExperimentConfig
from load_beir import BeirRepository


def main(exp_config: BaseExperimentConfig):
    dataset_name = exp_config.DATASET_NAME

    repository = BeirRepository(dataset_name, exp_config.vector_db_url())
    qrels_dict = repository.qrels()
    qrels = Qrels(qrels_dict)

    src_dir = pathlib.Path(__file__).parent.parent.parent.absolute()
    run_filename_dict = {
        "low": f"exp2_{dataset_name}_low.json",
        "medium": f"exp2_{dataset_name}_medium.json",
        "high": f"exp2_{dataset_name}_high.json",
    }
    run_list = []
    for run_name, run_filename in run_filename_dict.items():
        filename = os.path.join(src_dir, "outputs", run_filename)
        run = Run.from_file(filename, name=run_name)
        run_list.append(run)

    report = compare_retrieval(qrels, run_list, exp_config=exp_config)
    print(report)

    # report_k5 = compare_retrieval(qrels, run_list, k=5)
    # print(report_k5)

    # report_k3 = compare_retrieval(qrels, run_list, k=3)
    # print(report_k3)


if __name__ == "__main__":
    dataset_name = "fiqa"

    exp_config = AuthzExperimentConfig(dataset_name)
    main(exp_config)
