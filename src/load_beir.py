import os
import pathlib
import pickle

beir_dir = os.path.join(pathlib.Path(__file__).parent, "beir")

with open(os.path.join(beir_dir, "corpus.pkl"), "rb") as file:
    corpus = pickle.load(file)

print(len(corpus))

with open(os.path.join(beir_dir, "queries.pkl"), "rb") as file:
    queries = pickle.load(file)
with open(os.path.join(beir_dir, "qrels.pkl"), "rb") as file:
    qrels = pickle.load(file)

nq_dict = {"corpus": corpus, "queries": queries, "qrels": qrels}

with open(os.path.join(beir_dir, "nq.pkl"), "wb") as file:
    pickle.dump(nq_dict, file)


# class BeirDataset:
#     def __init__(self, dataset_name: Literal["msmarco", "nq", "trec-covid"] = "nq"):
#         self.dataset_name = dataset_name

#         self.__corpus, self.__queries, self.__qrels = self.load(self.dataset_name)

#         self.__document_id_list = list(self.__corpus.keys())
#         self.__document_entities: dict[str, Document] = {}
#         for idx in range(len(self.__corpus)):
#             document_id = self.__document_id_list[idx]
#             document = self.__corpus[document_id]
#             self.__document_entities[document_id] = Document(
#                 id=idx, title=document.get("title"), text=document.get("text")
#             )

#         self.__query_id_list = list(self.__queries.keys())
#         self.__query_entities: dict[str, Query] = {}
#         for idx in range(len(self.__queries)):
#             query_id = self.__query_id_list[idx]
#             query = self.__queries[query_id]
#             self.__query_entities[query_id] = Query(id=idx, text=query)

#     @classmethod
#     def __load_text(
#         cls, dataset_dir: str
#     ) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, dict[str, int]]]:
#         loader = GenericDataLoader(data_folder=dataset_dir)
#         corpus, queries, qrels = loader.load()

#         # save in pickle
#         pickle_file_objects = {"corpus.pkl": corpus, "queries.pkl": queries, "qrels.pkl": qrels}
#         for fname, obj in pickle_file_objects.items():
#             with open(os.path.join(dataset_dir, fname), "wb") as file:
#                 pickle.dump(obj, file)

#         return corpus, queries, qrels

#     @classmethod
#     def __load_binary(
#         cls, dataset_dir: str
#     ) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, dict[str, int]]]:
#         with open(os.path.join(dataset_dir, "corpus.pkl"), "rb") as file:
#             corpus = pickle.load(file)
#         with open(os.path.join(dataset_dir, "queries.pkl"), "rb") as file:
#             queries = pickle.load(file)
#         with open(os.path.join(dataset_dir, "qrels.pkl"), "rb") as file:
#             qrels = pickle.load(file)

#         return corpus, queries, qrels

#     @classmethod
#     def load(cls, dataset_name: str) -> tuple[dict[str, dict[str, str]], dict[str, str], dict[str, dict[str, int]]]:
#         src_dir = pathlib.Path(__file__).parent.parent.absolute()
#         dataset_dir = os.path.join(src_dir, "datasets", dataset_name)

#         print(f"[INFO] Loading dataset [{dataset_name}] ...")

#         if os.path.isfile(os.path.join(dataset_dir, "corpus.pkl")):
#             corpus, queries, qrels = cls.__load_binary(dataset_dir)
#         else:
#             corpus, queries, qrels = cls.__load_text(dataset_dir)

#         print(f"[INFO] Succeeded to load dataset [{dataset_name}]")

#         return corpus, queries, qrels

#     def corpus(self) -> dict[str, dict[str, str]]:
#         # corpus: dict[doc ID, dict[doc key, doc value]]
#         return self.__corpus

#     def document_entities(self) -> dict[str, Document]:
#         return self.__document_entities

#     def queries(self) -> dict[str, str]:
#         # queries: dict[query ID, query text]
#         return self.__queries

#     def query_entities(self) -> dict[str, Query]:
#         return self.__query_entities

#     def qrels(self) -> dict[str, dict[str, str]]:
#         # qrels: dict[query ID, dict[doc ID, relation]]
#         return self.__qrels

#     def find_document_id_by_index(self, index: int) -> str:
#         return self.__document_id_list[index]

#     def find_document_by_id(self, document_id: str) -> Document:
#         return self.__document_entities[document_id]

#     def find_document_by_index(self, index: int) -> Document:
#         return self.find_document_by_id(self.find_document_id_by_index(index))

#     def find_query_id_by_index(self, index: int) -> str:
#         return self.__query_id_list[index]

#     def find_query_by_id(self, query_id: str) -> Query:
#         return self.__query_entities[query_id]

#     def find_query_by_index(self, index: int) -> Query:
#         return self.find_query_by_id(self.find_query_id_by_index(index))
