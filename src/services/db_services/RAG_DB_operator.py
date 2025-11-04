from typing import override
from src.services.db_services.interfaces.DB_operator_interfaces import RAG_DB_operator_I
from src.models.RAG_data_model import RAG_DTModel

#TODO(before push): rename file into "RAG_DB_operators.py"

"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""
#TODO(before push): implement
class RAG_PineconeDB_operator(RAG_DB_operator_I):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """

    def __init__(self, api_key: str, environment: str, index_name: str):
        pass

    @override
    def get_record_using_embedded_text(self, target_collection_name: str, embedded_text_to_find: str) -> RAG_DTModel:
        pass

    @override
    def insert_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        pass

    @override
    def update_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        pass

    @override
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        pass

    @override
    def retrieve_vectors_using_query(self, target_collection_name: str, query: str, top_k: int) -> list[RAG_DTModel]:
        pass

    @override
    def open_connection(self, *args, **kwargs):
        pass

    @override
    def close_connection(self):
        pass

    @override
    def get_engine_name(self) -> str:
        return "Pinecone"


#TODO(before push): implement
class RAG_MongoDB_operator(RAG_DB_operator_I):
    pass