import asyncio
import itertools
import json
import os
import pathlib
import random
import time

from tqdm import tqdm
from tqdm.contrib import tenumerate

from apis.qdrant import QdrantQueryService
from load_beir import BeirRepository


def split_ids(N: int, k: int) -> list[list[int]]:
    """
    0からN-1のID列を均等にk分割する
    """
    id_list = list(range(N))
    result = []
    base_size = N // k
    remainder = N % k

    start = 0
    for i in range(k):
        chunk_size = base_size + (1 if i < remainder else 0)
        result.append(id_list[start : start + chunk_size])
        start += chunk_size
    return result


def split_ids_random(N: int, k: int, seed: int = 42) -> list[list[int]]:
    """
    0からN-1のID列を均等にランダムにk分割する
    """
    id_list = list(range(N))

    random.seed(seed)
    random.shuffle(id_list)

    result = []
    base_size = N // k
    remainder = N % k

    start = 0
    for i in range(k):
        chunk_size = base_size + (1 if i < remainder else 0)
        result.append(id_list[start : start + chunk_size])
        start += chunk_size
    return result


def split_beir_collection_ids(dataset_name: str, n_split: int, random: int | None = None) -> list[list[int]]:
    repository = BeirRepository(dataset_name)
    n_points = len(repository.corpus())

    if random is None:
        return split_ids(N=n_points, k=n_split)
    return split_ids_random(N=n_points, k=n_split, seed=random)


def save_each_collection_ids(each_collection_id_list: list[list[int]], filename: str):
    k = len(each_collection_id_list)

    env_dir = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "envs")
    output_file = os.path.join(env_dir, filename)

    json_out = {f"{k}-{idx + 1}": id_list for idx, id_list in enumerate(each_collection_id_list)}
    with open(output_file, "w") as file:
        json.dump(json_out, file)


async def split_beir_collection(
    dataset_name: str,
    n_split: int,
    split_seed: int | None = 42,
    copy_wait_seconds: int = 60,
    delete_wait_seconds: int = 10,
):
    service = QdrantQueryService(f"{dataset_name}-test")

    each_collection_id_list = split_beir_collection_ids(dataset_name, n_split, random=split_seed)
    all_id_list = list(itertools.chain.from_iterable(each_collection_id_list))
    all_id_set = set(all_id_list)
    assert len(all_id_list) == len(all_id_set)

    id_list_filename = f"{dataset_name}-split{n_split}_ids.json"
    save_each_collection_ids(each_collection_id_list, id_list_filename)

    for i_split, new_collection_id_list in tenumerate(each_collection_id_list, desc="split collection"):
        new_collection_name = f"{dataset_name}-{n_split}-{i_split + 1}"
        await service.copy_collection(new_collection_name)
        time.sleep(copy_wait_seconds)

        print(f"[{i_split + 1}/{n_split}] Copied collection")

        new_service = QdrantQueryService(new_collection_name)

        delete_id_list = list(all_id_set - set(new_collection_id_list))
        update_result = await new_service.delete_embeddings(delete_id_list)
        time.sleep(delete_wait_seconds)

        print(f"[{i_split + 1}/{n_split}] Deleted collection | {update_result=}")


if __name__ == "__main__":
    dataset_name = "nq"
    # n_split_list = [10, 8, 6, 4, 2]
    n_split_list = [32, 16]

    split_seed = 42

    copy_wait_seconds = 480
    delete_wait_seconds = 120

    for n_split in tqdm(n_split_list, desc="split"):
        asyncio.run(
            split_beir_collection(
                dataset_name,
                n_split,
                split_seed=split_seed,
                copy_wait_seconds=copy_wait_seconds,
                delete_wait_seconds=delete_wait_seconds,
            )
        )
