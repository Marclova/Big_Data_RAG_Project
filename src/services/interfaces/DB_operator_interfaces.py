from abc import ABC, abstractmethod

from src.models.interfaces.data_model_interface import DTModel


class DB_operator(ABC):
    """
    This is an abstract class that defines the interface for database operators.
    """
    @abstractmethod
    def get_record_using_title(self, input_collection_name: str, title: str) -> DTModel:
        """
        Retrieves a record in the given Mongo collection using its title.

        Parameters:
            input_collection_name (str): The name of the collection to retrieve the file from.
            title (str): The title of the record to retrieve.
        Returns:
            DTModel: The record with the given title.
        """
        pass

    #TODO(before push): modify the function signature to use a storage_data_model instead of raw parameters
    @abstractmethod
    def insert_record(self, target_collection_name: str, data_model: DTModel) -> bool:
        """
        Insert a new record into the DB using a custom JSON to describe the record's content.

        Parameters:
            output_collection_name (str): The name of the existing DB collection where to insert the record into.
            data_model (DTModel): The data model describing the record to insert.
         
        Returns:
           bool: the operation outcome.
        """
        pass

    #TODO(before push): modify the function signature to use a storage_data_model instead of raw parameters
    @abstractmethod
    def update_record(self, target_collection_name: str, data_model: DTModel) -> bool:
        """
        Updates a record in the Mongo DB having the corresponding title.
        The actual implementation is done by the update_record_using_JSON function.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            data_model (DTModel): The data model describing the record to update.
        Returns:
            bool: the operation outcome.
        """
        pass

    @abstractmethod
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        """
        Retrieves and delete from the Mongo DB a record having the corresponding title

        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            title (str): The name of the article to remove.
        
        Returns:
            bool: the operation outcome.
        """
        pass

    @abstractmethod
    def close_connection(self):
        """
        Closes the DB connection.
        """
        pass


class Storage_DB_operator(DB_operator):
    """
    This is an abstract class that defines the interface for storage database operations.
    It extends the DB_operator interface.
    """
    @abstractmethod
    def get_all_records(self, target_collection_name: str) -> list[DTModel]:
        """
        Retrieves all the records in the given Mongo collection.

        Parameters:
            target_collection_name (str): The name of the collection to retrieve the files from.

        Returns:
            list[DTModel]: A list of all records in the collection.
        """
        pass


class RAG_DB_operator(DB_operator):
    """
    This is an abstract class that defines the interface for RAG database operations and semantic search.
    It extends the DB_operator interface.
    """
    @abstractmethod
    def retrieve_vectors_using_query(self, target_collection_name: str, query: str, top_k: int) -> list[DTModel]:
        """
        Retrieves the top_k most similar vectors to the input query from the given collection.

        Parameters:
            target_collection_name (str): The name of the collection to retrieve the vectors from.
            query (str): The input query string to search for similar vectors.
            top_k (int): The number of top similar vectors to retrieve.
        Returns:
            list[DTModel]: A list of the top_k most similar vectors as data models.
        """
        pass