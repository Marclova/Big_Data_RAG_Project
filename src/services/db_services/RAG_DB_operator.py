from typing import override
from abc import ABC
from services.interfaces.DB_operator_interfaces import RAG_DB_operator
from src.models.RAG_data_model import RAG_DTModel

#TODO(before push): define at least two empty classes: one for Pinecone and one for MongoDB

"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""
#TODO(before push): implement
class RAG_PineconeDB_service(RAG_DB_operator):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """

    def __init__(self, api_key: str, environment: str, index_name: str):
        pass

    @override
    def get_record_using_title(self, input_collection_name: str, title: str) -> RAG_DTModel:
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
    def close_connection(self):
        pass


#TODO(before push): implement
class RAG_MongoDB_service(RAG_DB_operator):
    pass