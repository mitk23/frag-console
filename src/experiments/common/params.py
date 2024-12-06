def input_dataset_name() -> str:
    dataset_name = input("Select dataset [fiqa, nq, trec-covid]: ")

    assert dataset_name in {"fiqa", "nq", "trec-covid"}
    return dataset_name


def input_num_dataset() -> int:
    n_dataset = int(input("Select # of dataset to experiment [1...5]: "))

    assert 1 <= n_dataset <= 5
    return n_dataset


def input_num_request_documents() -> int:
    n_request_docs = int(input("Select # of request documents [5, 10, 20]: "))

    assert n_request_docs in {5, 10, 20}
    return n_request_docs


def input_exact_search() -> bool:
    exact_search = input("Retrieve exactly? (Disable ANN?) [y/n]: ")
    if exact_search in {"y", "Y"}:
        return True
    return False
