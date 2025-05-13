from abc import ABC, abstractmethod


class Embedder(ABC):
    """
    This is an abstract class that defines the interface for embedding text files into vector representations.
    """
    @abstractmethod
    def get_embedder_name(self) -> str:
        """
        Embedder interface function to get the name of the embedder.
        Returns:
            str: The name of the embedder.
        """
        pass


    @abstractmethod
    def generate_vectorDict_from_URL(self, file_URL: str) -> dict[str, list[float]]:
        """
        Embedder interface function to calculate and return the embedded vectors from the given file url. 
        Afterwards the embeddings must be converted into a dict relating clustered texts with each vector.
        Parameters:
            file_URL (str): The url of the file to convert.
        Returns:
            dict[str,list[float]]: The dict of clustered texts associated with their respective vectors, 
                expressed as a list of floats.
                The whole dict represents the given document's vector set.
        """
        pass


    @abstractmethod
    def convert_vectorDict_into_vectorStore(self, vectorList: dict[str, list[float]]) -> any:
        """
        Embedder interface function to convert the given vector list into a vectorStore.
        Parameters:
            dict[str,list[float]]: The dict of clustered texts associated with their respective vectors, 
                expressed as a list of floats.
                The whole dict represents the given document's vector set.
        Returns:
            any: The converted vectorStore.
        """
        pass