from abc import ABC, abstractmethod

from src.models.interfaces.config_interfaces import DB_config_I
from src.models.interfaces.data_model_interface import DTModel_I
from src.models.data_models import Storage_DTModel, RAG_DTModel

floatVector = list[float]

class DB_operator_I(ABC):
    """
    This is an abstract class that defines the interface for database operators.
    """
    @abstractmethod
    def insert_record(self, target_collection_name: str, data_model: DTModel_I) -> bool:
        """
        Insert a new record into the given collection/table/index.

        Parameters:
            output_collection_name (str): The name of the existing DB collection/table/index where to insert the record into.
            data_model (DTModel): The data model describing the record to insert.
         
        Returns:
           bool: the operation outcome.
        """
        pass

    @abstractmethod
    def update_record(self, target_collection_name: str, data_model: DTModel_I) -> bool:
        """
        Updates a record in the given collection/table/index having the corresponding key value 
            ('title' for storage DBs and 'text' for RAG DBs).
        The actual implementation is done by the update_record_using_JSON function.
        Parameters:
            target_collection_name (str): The name of the existing DB collection/table/index where to insert the record into.
            data_model (DTModel): The data model describing the record to update.
        Returns:
            bool: the operation outcome.
        """
        pass

    @abstractmethod
    def check_collection_existence(self, collection_to_check: str) -> bool:
        """
        Checks if the collection/table/index in the given list exists in the connected DB.
        Parameters:
            collection_to_check (str): The name of the collection/table/index to check for existence.
        Returns:
            bool: True the collection/table/index exist, False otherwise.
        """
        pass

    @abstractmethod
    def open_connection(self, connection_config: DB_config_I) -> bool:
        """
        Opens the DB connection using the provided configuration. 
        It also updates the needed instance variables to match the new connection.
        Parameters:
            db_config (DB_config): The configuration to use to open the DB connection.
        Returns:
            bool: 'True' if the connection was successful. Raise exception otherwise.
        """
        pass

    @abstractmethod
    def close_connection(self):
        """
        Closes the DB connection.
        """

    @abstractmethod
    def get_engine_name(self) -> str:
        """
        Gets the name of the DB engine.

        Returns:
            str: The name of the DB engine.
        """
        pass


class Storage_DB_operator_I(DB_operator_I):
    """
    This is an abstract class that defines the interface for storage database operations.
    It extends the DB_operator interface.
    """
    @abstractmethod
    def get_record_using_title(self, target_collection_name: str, title: str) -> Storage_DTModel:
        """
        Retrieves a record in the given collection/table using its title.

        Parameters:
            target_collection_name (str): The name of the collection/table to retrieve the file from.
            title (str): The title of the record to retrieve.
        Returns:
            DTModel: The record with the given title. None if not found.
        """
        pass

    @abstractmethod
    def get_all_records(self, target_collection_name: str) -> list[Storage_DTModel]:
        """
        Retrieves all the records in the given collection/table.

        Parameters:
            target_collection_name (str): The name of the collection/table to retrieve the files from.

        Returns:
            list[DTModel]: A list of all records in the collection/table.
        """
        pass

    @abstractmethod
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        """
        Retrieves and delete from the collection/table a record having the corresponding title

        Parameters:
            target_collection_name (str): The name of the existing DB collection/table where to insert the record into.
            title (str): The name of the article to remove.
        
        Returns:
            bool: the operation outcome.
        """
        pass

#TODO(improvement): Implement methods for exact subtext search ('get_record_using_embedded_text' and 'remove_record_using_embedded_text')
class RAG_DB_operator_I(DB_operator_I):
    """
    This is an abstract class that defines the interface for RAG database operations and semantic search.
    It extends the DB_operator interface.
    """
    # @abstractmethod
    # def get_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> RAG_DTModel:
    #     """
    #     Retrieves a record in the given index using its embedded text.
    #     The retrieval may be done using vector similarity search instead of an exact match, 
    #         but in this case only the most similar record is returned and then checked for exactness by the DB operator.

    #     Parameters:
    #         target_index_name (str): The name of the index to retrieve the file from.
    #         embedded_text_to_find (str): The embedded text of the record to retrieve.
    #     Returns:
    #         DTModel: The record with the given embedded text. None if not found.
    #     """
    #     pass

    # @abstractmethod
    # def remove_record_using_embedded_text(self, target_index_name: str, embedded_text_to_find: str) -> bool:
    #     """
    #     Retrieves and delete from the index a record having the corresponding embedded text.
    #     The retrieval may be done using vector similarity search instead of an exact match, 
    #         but in this case only the most similar record is returned and then checked for exactness by the DB operator.

    #     Parameters:
    #         target_index_name (str): The name of the existing DB index where to insert the record into.
    #         title (str): The name of the article to remove.
        
    #     Returns:
    #         bool: the operation outcome.
    #     """
    #     pass

    @abstractmethod
    def retrieve_embeddings_from_vector(self, target_index_name: str, query_vector: floatVector, top_k: int) -> list[RAG_DTModel]:
        """
        Retrieves the top_k most similar vectors to the input query from the given index.

        Parameters:
            target_index_name (str): The name of the index to retrieve the vectors from.
            query_vector (floatVector): The vector representing the query for argument retrieval.
                                    This value is supposed to be obtained by embedding a natural language question or text to retrieve.
            top_k (int): The number of top similar vectors to retrieve.
        Returns:
            list[DTModel]: A list of the top_k most similar vectors as data models.
        """
        pass
