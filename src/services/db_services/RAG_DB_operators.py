import asyncio
import logging
import math
import numpy
from typing import Any, override
from urllib.parse import urlparse

from pinecone import (Pinecone as PineconeClient, SearchQuery, UpsertResponse)
from pinecone.db_data import Index
from pinecone.core.openapi.db_data.model.search_records_response import SearchRecordsResponse
from pinecone.core.openapi.db_data.model.search_records_response_result import SearchRecordsResponseResult
from pinecone.core.openapi.db_data.model.hit import Hit

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.cursor import Cursor

from src.common.constants import Featured_RAG_DB_engines_enum as RAG_engines_enum

from src.services.db_services.interfaces.DB_operator_interfaces import RAG_DB_operator_I

from src.models.data_models import RAG_DTModel


#region custom types
TOLERANCE = 0.85
json = dict[str, Any]
floatVector = list[float]
class _VectorModel:
    """
    Container class for vector nodes used in the retrieval process.
    More precisely, it is used to assign similarity scores to text chunks 
    without worsening access to raw data vectors for intra-top_k similarity checks.
    """
    def __init__(self, similarity_to_query: float, json_RAGDTModel: json, vectorList: list[floatVector]):
        self.similarity_to_query: float = similarity_to_query
        self.json_RAGDTModel: json = json_RAGDTModel
        self.vectorList: list[floatVector] = vectorList
#endregion custom types

"""
 Service module to manage the connection and operations on a database meant to store embedded data for argument retrieval.
 Selected DBs are Pinecone and MongoDB
"""



class RAG_PineconeDB_operator(RAG_DB_operator_I):
    """
    Class to manage the Pinecone connection and operations for RAG vector storage.
    """
    def __init__(self, api_key: str, host: str):
        if((api_key is None) or (api_key.strip() == "") or 
           (host is None) or (host.strip() == "")):
            raise ValueError("One or more required parameters for Pinecone RAG DB operator initialization are missing or invalid.")

        self.connection: PineconeClient
        self.database: Index

        self.open_connection(api_key, host)


    @override
    def get_configuration_info(self) -> str:
        return ("RAG_DB: {"
                f"   DB_engine: '{self.get_engine_name()}',\n"
                f"   index_name: {self.get_index_name()},\n"
                f"   access_type: 'apy key',\n"
                f"   DB_url: '{self.database.config.host}',\n"
                f"   API_key: '{self.database.config.api_key}'\n"
                "}")
    

    @override
    def get_DB_name(self):
        """
        Returns the index name instead of the DB name. 
        Because that's not a reachable information through documented methods.
        """
        return self.get_index_name()
    

    @override
    def insert_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (data_model is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self.check_collection_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        
        return self._upsert_record(target_index_name, data_model)


    @override
    def update_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (data_model is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self.check_collection_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        #There must be a match
        if not (self._is_ID_already_in_use(target_index_name, data_model.id)):
            return False
        
        return self._upsert_record(target_index_name, data_model)


    @override
    def retrieve_embeddings_from_vector(self, target_index_name: str, query_vector: list[floatVector], 
                                              top_k: int) -> list[RAG_DTModel]:
        if((target_index_name is None) or (target_index_name.strip() == "") or 
           (query_vector is None) or (top_k is None)):
            raise ValueError("One or more required parameters for 'insert_record' method are missing or invalid.")
        if(self.check_collection_existence(target_index_name) is False):
            raise ValueError(f"The target index '{target_index_name}' does not exist in Pinecone DB.")
        
        response: SearchRecordsResponse = self.database.query(namespace=target_index_name, 
                                                                    vector=query_vector, top_k=top_k)
        return self._from_SearchRecordsResponse_to_RAGDTModelList(response)
    

    @override
    def check_collection_existence(self, index_to_check: str) -> bool:
        indexModel_list = self.connection.list_indexes().indexes
        indexName_list = [index.index.name for index in indexModel_list]
        res = (index_to_check in indexName_list)
        return res


    @override
    def open_connection(self, api_key: str, host: str) -> bool:
        try:
            self.connection = PineconeClient(api_key)
            self.database = self.connection.Index(host=host)
        except Exception as e:
            logging.info(f"[ERROR]: Failed to connect to the RAG DB '{self.get_DB_name()}': {e}")
            return False
        return True


    @override
    def close_connection(self):
        self.database.close()


    @override
    def get_engine_name(self) -> str:
        return RAG_engines_enum.PINECONE
    
    
    def get_index_name(self) -> str:
        url: str = urlparse(self.database.config.host).hostname
        return url.split("-")[0]
    


    def _upsert_record(self, target_index_name: str, data_model: RAG_DTModel) -> bool:
        """
        Private method actually performing the insert/update operation through the 'upsert' Pinecone method.
        Parameters:
           target_index_name (str): The index to perform the operation into
           data_model (RAG_DTModel): The data to upsert
        Parameters:
            bool: True if the a new record has been inserted or if an old one has been updated. 
                    False if the DB has not been changed.
        """
        response: UpsertResponse = self.database.upsert(namespace=target_index_name, vectors=[data_model.generate_JSON_data()])
        
        insertion_count: int = getattr(response, "upserted_count", -1)

        if insertion_count == -1:
            raise RuntimeError("Attribute 'upserted_count' not found in UpsertResponse wrapper.")
        return (insertion_count > 0)


    def _is_ID_already_in_use(self, target_index_name: str, id_to_check: str) -> bool:
        """
        Private method doing a search query in order to check if the given string is assigned to an existing record.
        Parameters:
            id_to_check (str): The ID to find
        Returns:
            bool: True if the given ID is used. False otherwise.
        """
        retrieved_data: list[RAG_DTModel] = (
                self._from_SearchRecordsResponse_to_RAGDTModelList(
                        self.database.search(
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
            data_list.append(RAG_DTModel.create_from_JSONData(JSON_data=hit.fields))
        return data_list




class RAG_MongoDB_operator(RAG_DB_operator_I):
    """
    MongoDB-based backend providing vector storage, embedding support, and 
    argument retrieval capabilities. Designed for full compatibility with
    standard MongoDB deployments, without requiring custom configurations.
    The built-in argument-retrieval implementation is supposed to work with 
    already normalized vectors.

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
    def __init__(self, DB_connection_url: str, DB_name: str, batch_size: int = 100000):
        self.connection: MongoClient
        self.database: Database
        self.batch_size: int = batch_size

        self.open_connection(DB_connection_url, DB_name)


    @override
    def insert_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        if self._check_record_existence_using_embedded_text(target_collection_name, data_model.text):
            logging.info(f"[ERROR]: Failed to insert the record with embedded text '{data_model.text}' into '{target_collection_name}': record already exists.")
            return False
        
        return self._insert_update_record(target_collection_name, data_model)


    @override    
    def update_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        if not self._check_record_existence_using_embedded_text(target_collection_name, data_model.text):
            logging.info(f"[ERROR]: Failed to update the record with embedded text '{data_model.text}' in '{target_collection_name}': record not existing.")
            return False
        
        return self._insert_update_record(target_collection_name, data_model)


    #TODO(UPDATE): Implement normalized vector checking and eventual normalization (using 'raw_data_operator.py')
    @override
    def retrieve_embeddings_from_vector(self, target_collection_name: str, 
                                        normalized_query_vector: list[floatVector], top_k: int) -> list[RAG_DTModel]:
        if( (target_collection_name is None) or (normalized_query_vector is None) or (top_k is None) ):
            raise ValueError("The method 'retrieve_embeddings_from_vector' has been called with one or more required parameters as 'None'")
        if(not self.check_collection_existence(target_collection_name)):
            logging.info(f"[ERROR]: No collection named '{target_collection_name}' in DB '{self.database.name}'")
        if(len(normalized_query_vector) == 0 or top_k <= 0):
            return []

        all_records: Cursor = self.database[target_collection_name].find()
        
        top_m = math.ceil(top_k * (1 + math.log(self.batch_size))) #top_m represents threads' maximum length of the results
        global_results: list[_VectorModel] = list()
        async def __find_k_best_matches(normalized_query_vector: floatVector) -> None:
            while True:
                # get embeddings from cursor
                json_RAGDTModel_list: list[json] = []
                all_records._next_batch(json_RAGDTModel_list, self.batch_size)
                if(len(json_RAGDTModel_list) == 0): #no more elements to process
                    break
                normalized_document_vectors: list[floatVector] = [record["vector"] for record in json_RAGDTModel_list]
                
                #array of floats
                cosine_similarity_array = numpy.dot(
                    numpy.array(normalized_document_vectors, dtype=float), 
                    numpy.array(normalized_query_vector, dtype=float))

                # since no order alteration is guaranteed, we can safely pair results with their corresponding records using the same index
                local_results: list[_VectorModel] = [
                    _VectorModel(similarity_to_query=cosine_similarity_array[i], 
                                 json_RAGDTModel=json_RAGDTModel_list[i], 
                                 vectorList=normalized_document_vectors[i]) 
                            for i in range(len(cosine_similarity_array))
                    ]
                    
                #we are not returning a number of results equal to 'batch_size', but only the 'top_m' best ones among them
                local_results.sort(key=lambda t: t.similarity_to_query, reverse=True)
                local_results = local_results[:top_m]
                global_results.extend(local_results)
        
        # applying 'divide...
        asyncio.run( __find_k_best_matches(normalized_query_vector) ) # after this execution, 'global_results' will contain 'len(all_records)/batch_size * top_m' best matches
        if(len(global_results) == 0):
            logging.info(f"[INFO]: The collection '{target_collection_name}' is empty or not connected.")
            return []
        
        # ...et impera'
        is_fully_ordered: bool = True
        # only the first and last are guaranteed to be ordered
        top_k_semi_ordered_list: list[_VectorModel] = [global_results.pop(0)] #initialize with the first result
        for new_candidate_res in global_results: # insert candidates one by one
            
            #early skip (abilitated after 'top_k' results have been collected)
            if(len(top_k_semi_ordered_list) >= top_k):
                if(new_candidate_res.similarity_to_query < top_k_semi_ordered_list[0].similarity_to_query):
                    continue #candidate too far: discard it

            #detect intra-top_k similarity avoidance here (discard the new candidate or another old candidate if needed)
            discarded_vector: _VectorModel = self._solve_redundance(new_candidate_res, top_k_semi_ordered_list)
            if(discarded_vector is new_candidate_res): #new candidate discarded
                continue

            #insert new candidate result (determining if the list remains ordered)
            if(new_candidate_res.similarity_to_query >= top_k_semi_ordered_list[-1].similarity_to_query):
                top_k_semi_ordered_list.append(new_candidate_res) #most efficient insertion (no later sorting needed)
            else:
                top_k_semi_ordered_list.insert(-1, new_candidate_res) #less efficient insertion (later sorting needed)
                is_fully_ordered = False

            if len(top_k_semi_ordered_list) > top_k: #remove less close one
                if(not is_fully_ordered): #sort only if needed
                    top_k_semi_ordered_list.sort(key=lambda t: t.similarity_to_query) #ascending order
                top_k_semi_ordered_list.pop(0)

        return [ RAG_DTModel.create_from_JSONData(JSON_data=best_res.json_RAGDTModel) for best_res in top_k_semi_ordered_list ]


    @override
    def check_collection_existence(self, collection_to_check: str) -> bool:
        return (self.database.get_collection(collection_to_check) != None)


    @override
    # def open_connection(self, DB_connection_url: str, DB_name: str, openai_api_key: str):
    def open_connection(self, DB_connection_url: str, DB_name: str) -> bool:
        try:
            self.connection = MongoClient(DB_connection_url)
            self.database = self.connection[DB_name]
        except Exception as e:
            logging.info(f"[ERROR]: Failed to connect to the RAG DB '{self.get_engine_name()}': {e}")
            return False
        return True


    @override
    def close_connection(self):
        self.connection.close()
        self.database = None


    @override
    def get_configuration_info(self) -> str:
        return ("RAG_DB: {\n"
                f"   DB_engine: '{self.get_engine_name()} (built-in vectorial ver.)',\n"
                f"   database_name: '{self.get_DB_name()}',\n"
                f"   access_type: 'local host',\n"
                f"   DB_url: '{self.database.client.address}'\n"
                "}")
    

    @override
    def get_DB_name(self):
        return self.database.name


    @override
    def get_engine_name(self) -> str:
        return RAG_engines_enum.MONGODB

    
    #TODO(MINOR REFACTOR): use the data_model's function to generate the json (it will cause a cascade problem because the structure is different now)
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
            logging.info(f"[ERROR]: Failed to insert the record with embedded text '{data_model.text[:30]}' into '{target_collection_name}': {e}")
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
    

    def _solve_redundance(self, new_vector: _VectorModel, vector_list: list[_VectorModel]) -> _VectorModel:
        """
        Private method to resolve redundancy between a given record and a list of already selected records.
        It removes the less similar record to the query between the given record and the redundant one found in the list.
        Parameters:
            vector (_VectorModel): The record to check.
            vector_list (list[_VectorModel]): The list of already selected records.
        Returns:
            _VectorModel: The record that has been discarded due to redundancy (may be the given record or one from the list).
                            None if no redundancy is found.
        """
        redundant_vector: _VectorModel = self._cosine_redundance_check(new_vector, vector_list)
        if(redundant_vector is not None):
            if(redundant_vector.similarity_to_query >= new_vector.similarity_to_query):
                return new_vector #old candidate keeps its place; no discard needed
            else:
                vector_list.remove(redundant_vector) #discard old candidate instead
                return redundant_vector
        return None
    

    def _cosine_redundance_check(self, vector: _VectorModel, vector_list: list[_VectorModel]) -> _VectorModel:
        """
        Private method to check if a given record is redundant with respect to a list of already selected records.
        Parameters:
            vector (_VectorModel): The record to check.
            vector_list (list[_VectorModel]): The list of already selected records.
        Returns:
            _VectorModel: The record in the vector_list that is redundant with respect to the given record.
                            None if no redundancy is found.
        """
        for existing_vector in vector_list:
            if(numpy.dot(existing_vector.vectorList, vector.vectorList) >= TOLERANCE):
                return existing_vector
        return None