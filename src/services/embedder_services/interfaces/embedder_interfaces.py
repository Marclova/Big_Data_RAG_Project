from abc import ABC, abstractmethod

from src.common.constants import Featured_embedding_models_enum as embed_models


floatVector = list[float]


class Embedder_I(ABC):
    """
    Interface for embedders API services which embed text files (ex. TXT, PDF) into vector representations, 
    returning them as RAG_DTModels for DB interactions.
    """
    @abstractmethod
    def __init__(self, embedder_model_name: str, embedder_api_key: str):
        pass

    @abstractmethod
    def generate_vectors_from_textChunks(self, textChunkList: list[str]) -> dict[str,floatVector]:
        """
        Method to calculate and return the embedded vectors from the given texts.
        Each vector is represented by a list of float values.
        Parameters:
            textChunkList (list[str]): The list of texts to embed.
        Returns:
            dict[str,list[float]]: The dict mapping each text (str) with the respective vector (list[float]).
        """
        pass

    @abstractmethod
    def generate_vector_from_text(self, text: str) -> floatVector:
        """
        Method to calculate and return the embedded vector from the given text.
        The vector is represented by a list of float values.
        Parameters:
            text (str): The text to embed.
        Returns:
            list[float]: The resulting embedded vector.
        """
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
    def delete_sensitive_info(self):
        """
        Method to delete any sensitive information stored in the embedder instance.
        """
        pass


# class Embedder_with_retrieval_I(Embedder_I):
#     """
#     Extending another interface, this one is for embedders which embed text files (ex. TXT, PDF) 
#     and also implement argument retrieval for DBs that don't have such functionality natively.
#     This interface is supposed to be implemented/extended only by sub-classes of 'RAG_DB_operator_I'.
#     """
#     @abstractmethod
#     def retrieve_vectors_using_query(self, target_collection_name: str, query: str, top_k: int) -> list[RAG_DTModel]:
#         """
#         Retrieves the top_k most similar vectors to the input query from the given collection/table/index.

#         Parameters:
#             target_collection_name (str): The name of the collection/table/index to retrieve the vectors from.
#             query (str): The input query string to search for similar vectors.
#             top_k (int): The number of top similar vectors to retrieve.
#         Returns:
#             list[DTModel]: A list of the top_k most similar vectors as data models.
#         """
#         pass