import asyncio
import json
import os
import pathlib
import random
import time

from tqdm import tqdm

from apis.qdrant import QdrantQueryService
from experiments.common import params
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


def split_beir_collection_ids(
    qdrant_url: str, dataset_name: str, n_split: int, random: int | None = None
) -> list[list[int]]:
    repository = BeirRepository(dataset_name=dataset_name, db_url=qdrant_url)
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


async def delete_beir_collection(
    qdrant_url: str,
    dataset_name: str,
    n_split: int,
    delete_wait_seconds: int = 10,
):
    service = QdrantQueryService(qdrant_url, dataset_name)

    for i_split in range(n_split):
        collection_name = f"{dataset_name}-{n_split}-{i_split + 1}"
        await service.delete_collection(collection_name)

        time.sleep(delete_wait_seconds)

        print(f"[{i_split + 1}/{n_split}] Deleted collection {collection_name}")


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    qdrant_url = "http://172.26.16.20:6333" if dataset_name == "nq" else "http://172.26.16.10:6333"

    n_split_list = [2, 4, 6, 8, 10, 16, 32]

    delete_wait_seconds = 10

    for n_split in tqdm(n_split_list, desc="delete"):
        asyncio.run(
            delete_beir_collection(
                qdrant_url=qdrant_url,
                dataset_name=dataset_name,
                n_split=n_split,
                delete_wait_seconds=delete_wait_seconds,
            )
        )
