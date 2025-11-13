from abc import ABC, abstractmethod

from models.data_models import RAG_DTModel


class Embedder_I(ABC):
    """
    Interface for embedders API services which embed text files (ex. TXT, PDF) into vector representations, 
    returning them as RAG_DTModels for DB interactions.
    """
    @abstractmethod
    def __init__(self, embedder_model_name: str, embedder_api_key: str):
        pass
    
    @abstractmethod
    def get_embedder_name(self) -> str:
        """
        Method to get the name of the embedder.
        Returns:
            str: The name of the embedder.
        """
        pass

    @abstractmethod
    def generate_vector_from_URL(self, file_URL: str) -> list[RAG_DTModel]:
        """
        Method to calculate and return the embedded vectors from the given file url as a list of RAG_DTModel.
        Each RAG_DTModel represents a vector containing the embedding for a chunk of text.
        Parameters:
            file_URL (str): The url of the file to convert.
        Returns:
            list[RAG_DTModel]: The list of embeddings, expressed as a list of RAG_DTModel. 
                                Each RAG_DTModel represents the embedding of a text chunk. 
                                The whole list represents all the embeddings generated from the file.
        """
        pass


class Embedder_with_retrieval_I(Embedder_I):
    """
    Extending another interface, this one is for embedders which embed text files (ex. TXT, PDF) 
    and also implement argument retrieval for DBs that don't have such functionality natively.
    This interface is supposed to be implemented/extended only by sub-classes of 'RAG_DB_operator_I'.
    """
    @abstractmethod
    def retrieve_vectors_using_query(self, target_collection_name: str, query: str, top_k: int) -> list[RAG_DTModel]:
        """
        Retrieves the top_k most similar vectors to the input query from the given collection/table/index.

        Parameters:
            target_collection_name (str): The name of the collection/table/index to retrieve the vectors from.
            query (str): The input query string to search for similar vectors.
            top_k (int): The number of top similar vectors to retrieve.
        Returns:
            list[DTModel]: A list of the top_k most similar vectors as data models.
        """
        pass
