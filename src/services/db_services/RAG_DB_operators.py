from typing import override
from pinecone import (Pinecone as PineconeClient, SearchQuery, UpsertResponse, Vector)
from pinecone.db_data import IndexAsyncio
from pinecone.core.openapi.db_data.model.search_records_response import SearchRecordsResponse
from pinecone.core.openapi.db_data.model.search_records_response_result import SearchRecordsResponseResult
from pinecone.core.openapi.db_data.model.hit import Hit

from src.common.constants import Featured_RAG_DB_engines_enum as RAG_DB

from src.services.db_services.interfaces.DB_operator_interfaces import RAG_DB_operator_I

from src.models.data_models import RAG_DTModel


"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""


class RAG_PineconeDB_operator(RAG_DB_operator_I):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """
    def __init__(self, api_key: str, host: str):
        # self.database: PineconeClient
        self.database: IndexAsyncio
        # self.host: str

        self.open_connection(api_key, host)


    # @override
    # async def get_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> RAG_DTModel:
    #     # index: IndexAsyncio = PineconeClient.IndexAsyncio(host=self.host)
    #     response: SearchRecordsResponse = await self.database.search(namespace=target_index_name, 
    #                                                                  query=SearchQuery(inputs={"text": embedded_text_to_find}, 
    #                                                                                    top_k=1)
    #                                                                 )
    #     retrieved_record: dict[str, any] = self._from_SearchRecordsResponse_to_dict(response, {"text": embedded_text_to_find})

    #     if retrieved_record == None:
    #         return None
    #     else:
            # return RAG_DTModel(vector=retrieved_record["vector"], 
            #                    embedder_name=retrieved_record["metadata"]["embedder"], 
            #                    url=retrieved_record["metadata"]["url"], 
            #                    title=retrieved_record["metadata"]["title"], 
            #                    text=retrieved_record["metadata"]["text"], 
            #                    pages=retrieved_record["metadata"]["pages"], 
            #                    authors=retrieved_record["metadata"]["author"]
            #                   )


    @override
    async def insert_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        #There must be no match
        if self._is_ID_already_in_use(target_index_name, data_model.id):
            return False
        
        return self._upsert_record(target_index_name, data_model)


    @override
    async def update_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        #There must be a match
        if not (self._is_ID_already_in_use(target_index_name, data_model.id)):
            return False
        
        return self._upsert_record(target_index_name, data_model)


    # @override
    # def remove_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> bool:
    #     pass


    @override
    async def retrieve_vectors(self, target_index_name: str, query_vector: list[float], top_k: int) -> list[RAG_DTModel]:
        response: SearchRecordsResponse = await self.database.query(namespace=target_index_name, 
                                                                    vector=query_vector, top_k=top_k)
        return self._from_SearchRecordsResponse_to_RAGDTModelList(response)


    @override
    def open_connection(self, api_key: str, host: str):
        client = PineconeClient(api_key)
        self.database = client.IndexAsyncio(host=host)
        # self.host = host


    @override
    def close_connection(self):
        self.database.close()


    @override
    def get_engine_name(self) -> str:
        return RAG_DB.PINECONE
    


    async def _upsert_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        """
        Private method actually performing the insert/update operation through the 'upsert' Pinecone method.
        Parameters:
           target_index_name (str): The index to perform the operation into
           data_model (RAG_DTModel): The data to upsert
        Parameters:
            bool: True if the a new record has been inserted or if an old one has been updated. 
                    False if the DB has not been changed.
        """
        # vector: Vector = self._from_RAGDTModel_to_Vector(data_model)
        response: UpsertResponse = await self.database.upsert(namespace=target_index_name, vectors=[data_model.generate_JSON_data()])
        
        insertion_count: int = getattr(response, "upserted_count", -1)

        if insertion_count == -1:
            raise RuntimeError("Attribute 'upserted_count' not found in UpsertResponse wrapper.")
        return (insertion_count > 0)


    async def _is_ID_already_in_use(self, target_index_name: str, id_to_check: str) -> bool:
        """
        Private method doing a search query in order to check if the given string is assigned to an existing record.
        Parameters:
            id_to_check (str): The ID to find
        Returns:
            bool: True if the given ID is used. False otherwise.
        """
        retrieved_data: list[RAG_DTModel] = (
                self._from_SearchRecordsResponse_to_RAGDTModelList(
                        await self.database.search(
                                namespace=target_index_name, query = SearchQuery(inputs={"id": id_to_check}, top_k=1)
                        )
                )
        )
        return (retrieved_data.__len__() > 0)


    def _from_SearchRecordsResponse_to_RAGDTModelList(self, response: SearchRecordsResponse) -> list[RAG_DTModel]:
        """
        Private method to unwrap a SearchRecordsResponse response into a raw dataset.
        Parameters:
            response (SearchRecordsResponse): The response to unwrap.
            searched_value (dict[str, any]): The exact match to check.
                                                The first element of the tuple is the name of parameter to check, 
                                                while the second one is the parameter's value.
        Returns:
            list[RAG_DTModel]: The data models list retrieved records. 
                                Empty list if the retrieved_record does not contains an exact match with the searched value.
        """
        result: SearchRecordsResponseResult = response.result
        hit_list: list[Hit] = result.hits

        data_list: list[RAG_DTModel] = []

        for hit in hit_list:
            retrieved_record: dict[str, any] = hit.fields
            
            data_list.append(RAG_DTModel(id=retrieved_record["id"],
                                         vector=retrieved_record["vector"], 
                                         embedder_name=retrieved_record["metadata"]["embedder"], 
                                         url=retrieved_record["metadata"]["url"], 
                                         title=retrieved_record["metadata"]["title"], 
                                         text=retrieved_record["text"], 
                                         pages=retrieved_record["metadata"]["pages"], 
                                         authors=retrieved_record["metadata"]["author"]
                                        )
                            )
        return data_list
    

    # def _from_RAGDTModel_to_Vector(self, data_model: RAG_DTModel) -> Vector:
    #     """
    #     Private method to convert a RAG_DTModel data model into a Vector for Pinecone RAG storage.
    #     Parameters:
    #         data_model (RAG_DTModel): The data model to convert.
    #     Returns:
    #         Vector: The Pinecone vector created from the data.
    #     """
    #     return Vector(id=data_model.id, values=data_model.vector, 
    #                   metadata={
    #                       "url" : data_model.url,
    #                       "title" : data_model.title,
    #                       "text" : data_model.text,
    #                       "pages" : data_model.pages,
    #                       "author" : data_model.authors,
    #                       "embedder" : data_model.embedder_name
    #                   })



#TODO: implement class
class RAG_MongoDB_operator(RAG_DB_operator_I):
    pass
