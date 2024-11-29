import os
import pathlib
import pickle
from typing import Literal

from apis.qdrant import QdrantQueryService


def qdrant_corpus_collection_name(dataset_name: str):
    return f"{dataset_name}-test"


def qdrant_query_collection_name(dataset_name: str):
    return f"{dataset_name}-query-test"


class BeirRepository:
    def __init__(self, dataset_name: Literal["nq", "trec-covid"] = "nq"):
        self.dataset_name = dataset_name

        self.__corpus, self.__queries, self.__qrels = self.load(self.dataset_name)
        self.__document_id_list = list(self.__corpus.keys())
        self.__query_id_list = list(self.__queries.keys())

        self.__qdrant_service_corpus = QdrantQueryService(
            collection_name=qdrant_corpus_collection_name(self.dataset_name)
        )
        self.__qdrant_service_queries = QdrantQueryService(
            collection_name=qdrant_query_collection_name(self.dataset_name)
        )

    @staticmethod
    def load(dataset_name: str) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, dict[str, int]]]:
        beir_dir = os.path.join(pathlib.Path(__file__).parent, "beir")

        print(f"[INFO] Loading dataset [{dataset_name}] ...")
        with open(os.path.join(beir_dir, f"{dataset_name}.pkl"), "rb") as file:
            beir_dict = pickle.load(file)
        print(f"[INFO] Succeeded to load dataset [{dataset_name}]")

        corpus = beir_dict["corpus"]
        queries = beir_dict["queries"]
        qrels = beir_dict["qrels"]

        return corpus, queries, qrels

    def corpus(self) -> dict[str, dict[str, str]]:
        # corpus: dict[doc ID, dict[doc key, doc value]]
        return self.__corpus

    def queries(self) -> dict[str, str]:
        # queries: dict[query ID, query text]
        return self.__queries

    def qrels(self) -> dict[str, dict[str, float]]:
        # qrels: dict[query ID, dict[doc ID, relation]]
        return self.__qrels

    def find_document_id_by_index(self, index: int) -> str:
        return self.__document_id_list[index]

    def find_document_by_id(self, document_id: str) -> dict[str, str]:
        corpus = self.corpus()
        return corpus[document_id]

    async def find_document_embeddings_by_index(self, document_indices: list[int]) -> dict[str, list[float]]:
        embeddings_dict = await self.__qdrant_service_corpus.fetch_embeddings(id_list=document_indices)
        return {self.__document_id_list[idx]: embedding for idx, embedding in embeddings_dict}

    def find_query_id_by_index(self, index: int) -> str:
        return self.__query_id_list[index]

    def find_query_by_id(self, query_id: str) -> str:
        queries = self.queries()
        return queries[query_id]

    async def find_query_embeddings_by_index(self, query_indices: list[int]) -> dict[str, list[float]]:
        embeddings_dict = await self.__qdrant_service_queries.fetch_embeddings(id_list=query_indices)
        return {self.__query_id_list[idx]: embedding for idx, embedding in embeddings_dict.items()}
