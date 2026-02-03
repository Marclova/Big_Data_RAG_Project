from typing import cast, override
from abc import ABC, abstractmethod

from managers.interfaces.manager_interface import Manager_I

from src.common.constants import (DB_use_types_enum as DB_usage, 
                                  Featured_storage_DB_engines_enum as storage_DB_engine, 
                                  Featured_RAG_DB_engines_enum as RAG_DB_engine)

from src.models.interfaces.config_interfaces import DB_config_I
from src.models.interfaces.data_model_interface import DTModel_I
from src.models.config_models import Storage_DB_config, RAG_DB_config
from src.models.data_models import Storage_DTModel, RAG_DTModel

from src.services.db_services.interfaces.DB_operator_interfaces import DB_operator_I, RAG_DB_operator_I, Storage_DB_operator_I
from src.services.db_services import storage_DB_operators, rag_DB_operators


class generic_DB_manager(Manager_I):
    """
    Generic class not meant to be initialized nor to be used for an abstract design pattern.
    It contains the methods common between all the DB managers.
    """
    DB_operator: DB_operator_I


    @abstractmethod
    def __init__(self, db_config: DB_config_I):
        pass

    @abstractmethod
    def insert_record(self, target_collection_name: str, data_model: DTModel_I) -> bool:
        """
        Insert a record into the given DB collection/table/index.
        Parameters:
            target_collection_name (str): The collection to insert the record into.
            data_model: The data model describing the record to update.
        Returns:
            bool: The operation outcome.
        """
        pass

    @abstractmethod
    def update_record(self, target_collection_name: str, data_model: DTModel_I) -> bool:
        """
        Updates a record into the given collection/table/index.
        Parameters:
            target_collection_name (str): The name of the existing DB collection/table/index where to insert the record into.
            data_model: The data model describing the record to update.
        Returns:
            bool: the operation outcome.
        """
        pass

    @override
    def disconnect(self):
        self.DB_operator.close_connection()

    
    def _parameters_validation(self, target_collection_name: str, **kwargs) -> None:
        """
        Internal method to validate common parameters for DB manager methods. 
        In case of invalid parameters, raises ValueError.
        parameters:
            target_collection_name (str): The name of the target collection/table/index.
            **kwargs: Additional parameters to validate (only 'None' check is performed)
        """
        if(target_collection_name is None):
            raise ValueError("The target collection name cannot be None.")
        for param_name, param_value in kwargs.items():
            if(param_value is None):
                raise ValueError(f"The parameter '{param_name}' cannot be None.")
        if(self.DB_operator.check_collection_existence(target_collection_name) is False):
            raise ValueError(f"The target collection/table/index '{target_collection_name}' does not exist in the DB.")




class Storage_DB_manager(generic_DB_manager):
    """
    Manager for DB operations to store papers destined to be embedded.
    """
    def __init__(self, DB_config: Storage_DB_config):
        if(DB_config is None):
            raise ValueError("The DB configuration cannot be None.")

        self.DB_operator: Storage_DB_operator_I = _DB_operator_factory.initialize_storage_db_operator(DB_config)

    
    @override
    def insert_record(self, target_collection_name: str, data_model: Storage_DTModel) -> bool:
        self._parameters_validation(target_collection_name=target_collection_name, data_model=data_model)
        
        return self.DB_operator.insert_record(target_collection_name, data_model)
    

    @override
    def update_record(self, target_collection_name: str, data_model: Storage_DTModel) -> bool:
        self._parameters_validation(target_collection_name=target_collection_name, data_model=data_model)
        
        return self.DB_operator.update_record(target_collection_name, data_model)


    def get_record_using_title(self, input_collection_name: str, title: str) -> Storage_DTModel:
        """
        Retrieves a record in the given collection/table/index using its title.
        Parameters:
            input_collection_name (str): The name of the collection/table/index to retrieve the file from.
            title (str): The title of the record to retrieve.
        Returns:
            DTModel: The record with the given title. None if not found.
        """
        self._parameters_validation(target_collection_name=input_collection_name, title=title)

        return self.DB_operator.get_record_using_title(input_collection_name, title)

    
    def get_all_records(self, target_collection_name: str) -> list[Storage_DTModel]:
        """
        Retrieves all the records in the given collection/table.
        Parameters:
            target_collection_name (str): The name of the collection/table to retrieve the files from.
        Returns:
            list[DTModel]: A list of all records in the collection/table.
        """
        self._parameters_validation(target_collection_name=target_collection_name)

        return self.DB_operator.get_all_records(target_collection_name)

    
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        """
        Retrieves and delete from the collection/table a record having the corresponding title
        Parameters:
            target_collection_name (str): The name of the existing DB collection/table where to insert the record into.
            title (str): The name of the article to remove.
        Returns:
            bool: the operation outcome.
        """
        self._parameters_validation(target_collection_name=target_collection_name, title=title)

        return self.DB_operator.remove_record_using_title(target_collection_name, title)



class RAG_DB_manager(generic_DB_manager):
    """
    Manager for DB operations to embed papers and store embeddings.
    """
    def __init__(self, DB_config: RAG_DB_config):
        if(DB_config is None):
            raise ValueError("The DB configuration cannot be None.")

        self.DB_operator: RAG_DB_operator_I = _DB_operator_factory.initialize_RAG_db_operator(DB_config)

    def insert_records(self, target_collection_name: str, data_models: list[RAG_DTModel]) -> bool:
        """
        Variation of insert_record to insert multiple records at once.
        """
        self._parameters_validation(target_collection_name=target_collection_name, data_models=data_models)
        
        flag = True
        for data_model in data_models:
            if(not self.insert_record(target_collection_name, data_model)):
                flag = False
                print(f"ERROR: insertion of record with embedded_text starting with '{data_model.text[:30]}...' failed.") #TODO(polishing) Consider another logging method
        return flag


    @override
    def insert_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        self._parameters_validation(target_collection_name=target_collection_name, data_model=data_model)
        
        return self.DB_operator.insert_record(target_collection_name, data_model)
    

    @override
    def update_record(self, target_collection_name: str, data_model: RAG_DTModel) -> bool:
        self._parameters_validation(target_collection_name=target_collection_name, data_model=data_model)
        
        return self.DB_operator.update_record(target_collection_name, data_model)


    # def get_record_using_embedded_text(self, target_collection_name: str, embedded_text_to_find: str) -> RAG_DTModel:
    #     """
    #     Retrieves a record in the given collection/table/index using its embedded text for the exact match.
    #     Parameters:
    #         target_collection_name (str): The name of the collection/table/index to retrieve the file from.
    #         embedded_text_to_find (str): The embedded text of the record to retrieve.
    #     Returns:
    #         DTModel: The record with the given embedded text. None if not found.
    #     """
    #     return self.DB_operator.get_record_using_embedded_text(target_collection_name, embedded_text_to_find)

    
    # def remove_record_using_embedded_text(self, target_collection_name: str, embedded_text_to_find: str) -> bool:
    #     """
    #     Retrieves and delete a record from the collection/table/index using its embedded text for the exact match.
    #     Parameters:
    #         target_collection_name (str): The name of the existing DB collection/table/index where to insert the record into.
    #         title (str): The name of the article to remove.
    #     Returns:
    #         bool: the operation outcome.
    #     """
    #     return self.DB_operator.remove_record_using_embedded_text(target_collection_name, embedded_text_to_find)

    
    def retrieve_vectors_using_vectorQuery(self, target_collection_name: str, vector_query: list[float], top_k: int) -> list[RAG_DTModel]:
        """
        Retrieves the top_k most similar vectors to the input query from the given collection/table/index.
        Parameters:
            target_collection_name (str): The name of the collection/table/index to retrieve the vectors from.
            vector_query (list[float]): The vector query to find similar vectors.
            top_k (int): The number of top similar vectors to retrieve.
        Returns:
            list[DTModel]: A list of the top_k most similar vectors as data models.
        """
        self._parameters_validation(target_collection_name=target_collection_name, vector_query=vector_query, top_k=top_k)

        return self.DB_operator.retrieve_embeddings_from_vector(target_collection_name, vector_query, top_k)
        


class _DB_operator_factory:
    """
    Private class defining a factory responsible for the initializations of the DB operators used by the managers.
    """
    def initialize_storage_db_operator(DB_config: Storage_DB_config) -> Storage_DB_operator_I:
        """
        Factory method to get the appropriate Storage DB operator based on the DB configuration and the featured DB types.
        """
        # Define the factory cases; one per supported DB engine.
        if DB_config.db_engine == storage_DB_engine.MONGODB:
            return storage_DB_operators.Storage_MongoDB_operator(
                DB_connection_url=DB_config.connection_url, DB_name=DB_config.database_name
                )
        elif DB_config.db_engine == storage_DB_engine.PYGRESQL:
            return storage_DB_operators.storage_PyGreSQL_operator(
                dbname=DB_config.database_name, host=DB_config.connection_url, port=DB_config.port, 
                user=DB_config.username, passwd=DB_config.password
                )

        raise NotImplementedError(
        f"Dead code activation: No factory case for {DB_config.usage_type} {DB_config.db_engine}. "
        "Did you update the featured DBs but forget to extend the factory method?"
        )
        

    def initialize_RAG_db_operator(DB_config: RAG_DB_config) -> RAG_DB_operator_I:
        """
        Factory method to get the appropriate RAG DB operator based on the DB configuration and the featured DB types.
        """            
        # Define the factory cases; one per supported DB engine.
        if DB_config.db_engine == RAG_DB_engine.PINECONE:
            return rag_DB_operators.RAG_PineconeDB_operator(api_key=DB_config.api_key, host=DB_config.connection_url)
        elif DB_config.db_engine == RAG_DB_engine.MONGODB:
            return rag_DB_operators.RAG_MongoDB_operator(DB_connection_url=DB_config.connection_url, DB_name=DB_config.database_name, 
                                                         batch_size= DB_config.batch_size)
        raise NotImplementedError(
            f"Dead code activation: No factory case for operator named '{DB_config.usage_type}_{DB_config.db_engine}_operator'. "
            "Did you update featured_DB_types but forget to extend the factory method?"
        )
