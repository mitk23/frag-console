import os
import pathlib

from ranx import Qrels, Run

from experiments import config
from experiments.evaluate import compare_retrieval
from load_beir import BeirRepository


def main():
    dataset_name = config.EXPERIMENT_DATASET_NAME

    repository = BeirRepository(dataset_name)
    qrels_dict = repository.qrels()
    qrels = Qrels(qrels_dict)

    src_dir = pathlib.Path(__file__).parent.parent.absolute()
    run_filename_dict = {
        "baseline": f"exp1_{dataset_name}_baseline.json",
        "baseline-exact": f"exp1_{dataset_name}_baseline-exact.json",
        "frag": f"exp1_{config.EXPERIMENT_DATASET_NAME}_2024-11-29.json",
    }
    run_list = []
    for run_name, run_filename in run_filename_dict.items():
        filename = os.path.join(src_dir, "outputs", run_filename)
        run = Run.from_file(filename, name=run_name)
        run_list.append(run)

    report = compare_retrieval(qrels, run_list)
    print(report)

    report_k5 = compare_retrieval(qrels, run_list, k=5)
    print(report_k5)

    report_k3 = compare_retrieval(qrels, run_list, k=3)
    print(report_k3)


if __name__ == "__main__":
    main()
