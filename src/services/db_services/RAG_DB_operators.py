from typing import override
from pinecone import (IndexModel, Pinecone as PineconeClient, QueryResponse, ScoredVector, SearchQuery, UpsertResponse)
from pinecone.db_data import Index
from pinecone.core.openapi.db_data.model.search_records_response import SearchRecordsResponse
from pinecone.core.openapi.db_data.model.search_records_response_result import SearchRecordsResponseResult
from pinecone.core.openapi.db_data.model.hit import Hit

from src.common.constants import Featured_RAG_DB_engines_enum as RAG_DB_enum

from src.services.db_services.interfaces.DB_operator_interfaces import RAG_DB_operator_I

from models.data_models import RAG_DTModel


"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""
#TODO(testing): The whole module needs testings; it may not work
#TODO(improvement): use an enum for embedder names

def create_new_RAG_index(DB_engine: RAG_DB_enum, embedder_name: str, 
                         api_key: str, host: str, new_index_name: str) -> bool:
    """
    Utility class method used to create a new index even before the initialization of a DB operator,
        which can't be initialized without a valid index ready.
    
    Parameters:
        DB_engine (RAG_DB_enum): The DB engine featured by the new index to create.
        embedder_name (str): The embedder used for text content conversion into search vectors.
        api_key (str): The api key for authentication and permission for the provider's API services.
        host (str): The host url from where it is possible to interact with the indexes.
        new_index_name (str): The identifying and immutable name to assign to the new index.
    Returns:
        bool: The overall operation outcome.    
    """
    try:
        if DB_engine == RAG_DB_enum.PINECONE:
            PineconeClient(api_key=api_key, host=host).create_index_for_model(
                                                            name = new_index_name,
                                                            embed={
                                                                "model":embedder_name, # es. "pinecone-sparse-english-v0"
                                                                "field_map":{"text": "chunk_text"}
                                                            }
                                                        )
        else:
            raise ValueError(f"RAG index creation for {DB_engine} is not supported")
    except Exception as e:
        print(f"Error while trying to create index: {e}")  #TODO(polishing): consider another logging method



class RAG_PineconeDB_operator(RAG_DB_operator_I):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """
    def __init__(self, api_key: str, host: str):
        self.database: PineconeClient

        self.open_connection(api_key, host)


    #region aborted 'get_record_using_embedded_text' method
    # @override
    # def get_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> RAG_DTModel:
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
    #endregion aborted 'get_record_using_embedded_text' method


    @override
    def insert_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        if(not self.database.has_index(target_index_name)):
            print(f"ERROR: There's no index named '{target_index_name}'") #TODO(polishing): consider another logging method
            return False
        if(self._is_ID_already_in_use(target_index_name, data_model.id)): #False if record already exists
            return False
        
        return self._insert_or_update_RAGDTModel(target_index_name, data_model)


    @override
    def update_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        if(not self.database.has_index(target_index_name)):
            print(f"ERROR: There's no index named '{target_index_name}'") #TODO(polishing): consider another logging method
            return False
        if(not self._is_ID_already_in_use(target_index_name, data_model.id)): #False if record doesn't exist
            return False
        
        return self._insert_or_update_RAGDTModel(target_index_name, data_model)


    # @override
    # def remove_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> bool:
    #     pass


    @override
    def retrieve_embeddings_from_vectors(self, target_index_name: str, query_vector: list[float], top_k: int) -> list[RAG_DTModel]:
        if(not self.database.has_index(target_index_name)):
            print(f"ERROR: There's no index named '{target_index_name}'") #TODO(polishing): consider another logging method
            return []

        index: Index = self.database.Index(target_index_name)
        response: QueryResponse = index.query(namespace=target_index_name, 
                                                      vector=query_vector, top_k=top_k)
        return self._from_QueryResponse_to_RAGDTModel(response)


    @override
    def open_connection(self, api_key: str, host: str):
        self.database = PineconeClient(api_key=api_key, host=host)


    @override
    def close_connection(self):
        self.database = None


    @override
    def get_engine_name(self) -> str:
        return RAG_DB_enum.PINECONE
    

    @override
    def get_embedder_name(self, target_index_name: str) -> str | None:
        if(not self.database.has_index(target_index_name)):
            print(f"ERROR: No such index named '{target_index_name}'") #TODO(polishing): consider another logging method
            return None

        index_model: IndexModel = self.database.describe_index(target_index_name)
        index_dict: dict[str,any] = index_model.to_dict()
        spec: dict[str,any] = index_dict.get("spec")
        embedder_name: str

        if(spec is None):
            print(f"ERROR: The index '{target_index_name}' has NO model-backed configuration. "
                  "This implementation only supports indexes with an integrated embedder. "
                  "Please select an index configured to use one of the featured embedders.")
            return None
        try:
            embedder_name = spec["model"]["embed"]["model"]
        except Exception as e:
            print("ERROR: Could not extract embedder name from index config. "
                  "The index may not be model-backed or has an unexpected structure. "
                  f"Raised error content: {e}")
            return None
        return embedder_name
    


    def _insert_or_update_RAGDTModel(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        """
        Private method actually performing the insert/update operation through the 'upsert' Pinecone method.
        Parameters:
           target_index_name (str): The index to perform the operation into
           data_model (RAG_DTModel): The data to upsert
        Parameters:
            bool: True if the a new record has been inserted or if an old one has been updated. 
                    False if the DB has not been changed.
        """
        index: Index = self.database.Index(target_index_name)
        # response = self.database.upsert(namespace=target_index_name, vectors=[data_model.generate_JSON_data()])
        response: UpsertResponse = index.upsert_records(target_index_name, [data_model.generate_JSON_data()])
        
        insertion_count: int = getattr(response, "upserted_count", -1)

        if insertion_count == -1:
            raise RuntimeError("Attribute 'upserted_count' not found in UpsertResponse wrapper.")
        return (insertion_count > 0)


    def _is_ID_already_in_use(self, target_index_name: str, id_to_check: str) -> bool:
        """
        Private method doing a search query in order to check if the given string is assigned to an existing record.
        Parameters:
            target_index_name (str): The index wherein to perform the search.
            id_to_check (str): The record ID to find
        Returns:
            bool: True if the given ID is used. False otherwise.
        """
        index: Index = self.database.Index(target_index_name)
        retrieved_data: list[RAG_DTModel] = (
                self._from_SearchRecordsResponse_to_RAGDTModelList(
                        index.search(namespace=target_index_name, 
                                     query = SearchQuery(inputs={"id": id_to_check}, top_k=1)
                        )
                )
        )
        return (retrieved_data.__len__() > 0)
    
    #TODO(testing): The 'ScoredVector' data may be not as expected. Can't implement not knowing the data structure.
    def _from_QueryResponse_to_RAGDTModel(self, response: QueryResponse) -> list[RAG_DTModel]:
        """
        Private method to unwrap a QueryResponse response into a raw dataset.
        Parameters:
            response (QueryResponse): The response to unwrap.
        Returns:
            list[RAG_DTModel]: The data models list retrieved records.
        """
        result_list: list[ScoredVector] = getattr(response, "matches")
        dataModel_list: list[RAG_DTModel] = []

        for result in result_list:
            metadata: dict[str,any] = result.__getattr__("metadata")

            # dataModel_list.append(RAG_DTModel(vector=result.__getattr__("vector"))
            #                 )
        pass
            


    #TODO(testing): The 'hit.fields' data structure may not be as expected
    def _from_SearchRecordsResponse_to_RAGDTModelList(self, response: SearchRecordsResponse) -> list[RAG_DTModel]:
        """
        Private method to unwrap a SearchRecordsResponse response into a raw dataset.
        Parameters:
            response (SearchRecordsResponse): The response to unwrap.
        Returns:
            list[RAG_DTModel]: The data models list retrieved records.
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



#TODO: implement
class RAG_MongoDB_operator(RAG_DB_operator_I):
    pass
