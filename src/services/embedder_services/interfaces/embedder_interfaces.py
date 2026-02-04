from abc import ABC, abstractmethod


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