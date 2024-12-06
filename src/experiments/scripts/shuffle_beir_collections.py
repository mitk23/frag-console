import asyncio
import itertools
import time

from tqdm.contrib import tenumerate

from apis.qdrant import QdrantQueryService
from experiments.common import params
from experiments.scripts.split_beir_collections import (
    save_each_collection_ids,
    split_beir_collection_ids,
)


async def shuffle_beir_collection(
    qdrant_url: str,
    dataset_name: str,
    n_split: int,
    n_shuffle: int,
    shuffle_seed: int | None = 42,
    copy_wait_seconds: int = 60,
    delete_wait_seconds: int = 10,
):
    service = QdrantQueryService(qdrant_url, dataset_name)

    split_seed_list = range(shuffle_seed, shuffle_seed + n_shuffle)
    for i_shuffle, seed in enumerate(split_seed_list):
        each_collection_id_list = split_beir_collection_ids(qdrant_url, dataset_name, n_split, random=seed)
        all_id_list = list(itertools.chain.from_iterable(each_collection_id_list))
        all_id_set = set(all_id_list)
        assert len(all_id_list) == len(all_id_set)

        id_list_filename = f"{dataset_name}-split{n_split}_shuffle{i_shuffle + 1}_ids.json"
        save_each_collection_ids(each_collection_id_list, id_list_filename)

        for i_split, new_collection_id_list in tenumerate(
            each_collection_id_list, desc=f"split collection [{i_shuffle + 1}]"
        ):
            new_collection_name = f"{dataset_name}-{n_split}-{i_split + 1}-{i_shuffle + 1}"
            await service.copy_collection(new_collection_name)
            time.sleep(copy_wait_seconds)

            print(f"[{i_split + 1}/{n_split} - {i_shuffle + 1}] Copied collection")

            new_service = QdrantQueryService(qdrant_url, new_collection_name)

            delete_id_list = list(all_id_set - set(new_collection_id_list))
            update_result = await new_service.delete_embeddings(delete_id_list)
            time.sleep(delete_wait_seconds)

            print(f"[{i_split + 1}/{n_split} - {i_shuffle + 1}] Deleted collection | {update_result=}")


if __name__ == "__main__":
    dataset_name = params.input_dataset_name()
    qdrant_url = "http://172.26.16.20:6333" if dataset_name == "nq" else "http://172.26.16.10:6333"

    n_split = 4
    n_shuffle = 5
    shuffle_seed = 42

    copy_wait_seconds = 60
    delete_wait_seconds = 20

    asyncio.run(
        shuffle_beir_collection(
            qdrant_url=qdrant_url,
            dataset_name=dataset_name,
            n_split=n_split,
            n_shuffle=n_shuffle,
            shuffle_seed=shuffle_seed,
            copy_wait_seconds=copy_wait_seconds,
            delete_wait_seconds=delete_wait_seconds,
        )
    )
