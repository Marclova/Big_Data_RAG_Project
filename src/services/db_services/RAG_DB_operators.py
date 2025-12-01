import asyncio
import heapq
import math
import numpy
from itertools import islice
from typing import override, Tuple

from pinecone import (Pinecone as PineconeClient, SearchQuery, UpsertResponse, Vector)
from pinecone.db_data import IndexAsyncio
from pinecone.core.openapi.db_data.model.search_records_response import SearchRecordsResponse
from pinecone.core.openapi.db_data.model.search_records_response_result import SearchRecordsResponseResult
from pinecone.core.openapi.db_data.model.hit import Hit

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.cursor import Cursor

from openai import OpenAI

from src.common.constants import Featured_RAG_DB_engines_enum as RAG_engines_enum

from src.services.db_services.interfaces.DB_operator_interfaces import RAG_DB_operator_I

from src.models.data_models import RAG_DTModel


"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""

floatVector = list[float]

class RAG_PineconeDB_operator(RAG_DB_operator_I):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """
    def __init__(self, api_key: str, host: str):
        if((api_key is None) or (api_key.strip() == "") or 
           (host is None) or (host.strip() == "")):
            raise ValueError("One or more required parameters for Pinecone RAG DB operator initialization are missing or invalid.")

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
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (data_model is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self._check_index_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        #There must be no match
        if self._is_ID_already_in_use(target_index_name, data_model.id):
            return False
        
        return self._upsert_record(target_index_name, data_model)


    @override
    async def update_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (data_model is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self._check_index_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        #There must be a match
        if not (self._is_ID_already_in_use(target_index_name, data_model.id)):
            return False
        
        return self._upsert_record(target_index_name, data_model)


    # @override
    # def remove_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> bool:
    #     pass


    @override
    async def retrieve_embeddings_from_vector(self, target_index_name: str, query_vector: floatVector, top_k: int) -> list[RAG_DTModel]:
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (query_vector is None) or (top_k is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self._check_index_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        
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
        return RAG_engines_enum.PINECONE
    


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
    


    #TODO implement private method
    def _check_index_existence(self, index_to_check: int) -> bool:
        # if([namespace. for namespace: ListNamespacesResponse in self.database.namespace.list()])
        return True


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
#TODO consider to move include 'record_limit_per_block' in the constructor as a configurable instance variable.
class RAG_MongoDB_operator(RAG_DB_operator_I):
    """
    MongoDB-based backend providing vector storage, embedding support, and
    argument retrieval capabilities. Designed for full compatibility with
    standard MongoDB deployments, without requiring custom configurations.

    DISCLAIMER
    ----------
    MongoDB is not designed for argument retrieval workloads. Performance is
    significantly lower compared to specialized vector databases, and its use is
    discouraged for medium/large-scale RAG systems. This backend is intended
    for lightweight deployments where ease of setup and portability are primary
    requirements.

    IMPLEMENTATION NOTE
    -------------------
    Several methods intentionally duplicate the logic found in
    `Storage_MongoDB_operator`. This is a controlled and exceptional case
    resulting from the reuse of the same provider library to support two
    distinct interfaces defined by the project architecture. The duplication is
    not indicative of an architectural issue and should not be refactored into
    shared abstractions unless a future, stable pattern emerges.
    """
    def __init__(self, DB_connection_url: str, DB_name: str, api_key: str, batch_size: int = 100000):
        self.connection: MongoClient
        self.database: Database
        self.batch_size: int = batch_size
        # self.embedder: OpenAI

        self.open_connection(DB_connection_url, DB_name, api_key)


    @override
    def insert_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        if self._check_record_existence_using_embedded_text(target_collection_name, data_model.text):
            print(f"Error while inserting the record with embedded text '{data_model.text}' into '{target_collection_name}': record already exists.") #TODO(polishing): consider another logging method
            return False
        
        return self._insert_update_record(target_collection_name, data_model)


    @override    
    def update_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        if not self._check_record_existence_using_embedded_text(target_collection_name, data_model.text):
            print(f"Error while updating the record with embedded text '{data_model.text}' in '{target_collection_name}': record not existing.") #TODO(polishing): consider another logging method
            return False
        
        return self._insert_update_record(target_collection_name, data_model)
    

    @override
    def check_collection_existence(self, collection_to_check: str) -> bool:
        return (self.database.get_collection(collection_to_check) != None)


    @override
    def open_connection(self, DB_connection_url: str, DB_name: str, api_key: str):
        self.connection = MongoClient(DB_connection_url)
        self.database = self.connection[DB_name]
        self.embedder = OpenAI(api_key=api_key)


    @override
    def close_connection(self):
        self.connection.close()
        self.database = None
        self.embedder.close()


    @override
    def get_engine_name(self) -> str:
        return RAG_engines_enum.MONGODB


    #TODO implement method
    @override
    def retrieve_embeddings_from_vector(self, target_collection_name: str, normalized_query_vector: floatVector, top_k: int) -> list[RAG_DTModel]:
        if( (target_collection_name is None) or (normalized_query_vector is None) or (top_k is None) ):
            raise ValueError("The method 'retrieve_embeddings_from_vector' has been called with one or more required parameters as 'None'")
        if(not self.check_collection_existence(target_collection_name)):
            print(f"ERROR: No collection named '{target_collection_name}' in DB '{self.database.name}'")
        if(len(normalized_query_vector) == 0 or top_k <= 0):
            return []

        all_records: Cursor = self.database[target_collection_name].find()
        
        global_results: list[tuple[float, dict[str, any]]] = list()
        async def __find_k_best_matches(normalized_query_vector: floatVector, top_k: int) -> None:
            while all_records.alive:
                # get embeddings from cursor
                records_chunk: list[dict[str, any]] = list(islice(all_records, self.batch_size))
                normalized_document_vectors: list[floatVector] = [record["vector"] for record in records_chunk]
                
                # calculate cosine similarity 'ndarray[float]' (a single float value for each 'floatVector' couple)
                # np_products_array = numpy.dot(
                #     numpy.array(normalized_vectors, dtype=float), 
                #     numpy.array(normalized_query_vector, dtype=float))
                # np_cosine_results_array = ( np_products_array / 
                #                            numpy.linalg.norm(normalized_vectors) * numpy.linalg.norm(normalized_query_vector) )
                np_cosine_results_array = numpy.dot(
                    numpy.array(normalized_document_vectors, dtype=float), 
                    numpy.array(normalized_query_vector, dtype=float))

                # since no order alteration is guaranteed, we can safely pair results with their corresponding records using the same index
                local_results: list[tuple[float, dict[str, any]]] = [(np_cosine_results_array[i], records_chunk[i]) 
                                                                     for i in range(len(records_chunk))]
                local_results.sort(key=lambda t: t[0], reverse=True)
                top_m = top_k * (1 + math.log(self.batch_size))
                local_results = local_results[:top_m]
                global_results.extend(local_results)
        
        # applying 'divide...
        asyncio.run( __find_k_best_matches(normalized_query_vector, top_k) ) # after this execution, 'global_results' will contain 'len(all_records)/record_limit_per_block * top_k' best matches
        # ...et impera'
        # global_results.sort(key=lambda t: t[0], reverse=True)
        # global_results = global_results[:top_k]
        # return [ RAG_DTModel(result[1]) for result in global_results ]
        heap_id: int = 0
        top_k_heap: heapq = []
        for global_res in global_results:
            if len(top_k_heap) < top_k: # add one result into the heap
                heapq.heappush(top_k_heap, (global_res[0], heap_id, global_res[1]))
            else: # add one result and remove the less close one ('head_id' is used in case of equality)
                heapq.heappushpop(top_k_heap, (global_res[0], heap_id, global_res[1]))
            heap_id += 1
        return [ RAG_DTModel(heap_res[2]) for heap_res in list(top_k_heap) ]

    

    def _insert_update_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        """
        Private method actually implementing the insertion/update of records.
        Parameters:
            target_collection_name (str): The collection to perform the operation into.
            data_model (RAG_DTModel): The data model to insert/update.
        Returns:
            bool: True if the operation is successful. False otherwise.
        """
        try:
            return ( self.database[target_collection_name].insert_one({
                "id": data_model.id,
                "text": data_model.text,
                "vector": data_model.vector,
                "metadata": {
                    "url": data_model.url,
                    "title": data_model.title,
                    "pages": data_model.pages,
                    "author": data_model.authors,
                    "embedder": data_model.embedder_name
                }
            }) is not None )
        except Exception as e:
            print(f"Error while inserting the record with embedded text '{data_model.text}' into '{target_collection_name}': {e}") #TODO(polishing): consider another logging method
            return False
        

    def _check_record_existence_using_embedded_text(self, target_collection_name: str, embedded_text_to_find: str) -> bool:
        """
        Private method to check the presence of a record int the target collection using an embedded text as key.
        Parameters:
            target_collection_name (str): The collection to search into.
            embedded_text_to_find (str): The embedded text to find.
        Returns:
            bool: True if a record with the given embedded text is found. False otherwise.
        """
        return self.database[target_collection_name].find_one({"embedded_text": embedded_text_to_find}) is not None
    

    def _textLength_and_wordCount_based_token_estimation(self, text: str) -> int:
        """
        Private method to estimate the number of tokens in a given text using a heuristic based on text length and word count. 
            The result precision is about 70-80% (optimistic estimate).
        Parameters:
            text (str): The text to analyze.
        Returns:
            int: The estimated number of tokens in the text.
        """
        return 0.6 * (len(text) / 3.3) + 0.4 * (len(text.split(" ")) * 2.2)