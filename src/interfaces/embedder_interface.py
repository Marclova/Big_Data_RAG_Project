from abc import ABC, abstractmethod

class Embedder(ABC):
    @abstractmethod
    def generate_vectorList_as_floatLists_from_URL(self, file_URL: str) -> list[list[float]]:
        """
        Embedder interface function to calculate and return the list of embedded vectors from the given file url. 
        Afterwards the embedding must be converted into a list of float lists; fit for being uploaded into the DB.
        Parameters:
            file_URL (Any): The url of the file to convert.
        Returns:
            list[list[float]]: The list of converted vectors, which may be interpreted as a list[Vectors];\n
            One vector corresponds to a cluster text and the whole vector list should correspond to a document.
        """
        ...