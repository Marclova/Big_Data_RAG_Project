from typing import override
from models.storage_data_model import Storage_DTModel

class RAG_DTModel(Storage_DTModel):
    """
    Data model class for RAG (Retrieval-Augmented Generation) data.
    This class defines the structure of the records stored in the RAG database.
    It implements Storage_DTModel because it contains a superset of the fields defined in Storage_DTModel.
    """

    def __init__(self, vector: list[float], embedder_name: str, storage_model: Storage_DTModel):
        """
        Initializes a RAG data model for storing and retrieving data from a vectorial database.
        """

        super().__init__(storage_model.url, storage_model.title, storage_model.pages, storage_model.text, storage_model.authors)

        if (vector is None or vector.__len__() == 0):
            raise ValueError("Vector cannot be None or empty")
        if (embedder_name is None or embedder_name.strip() == ""):
            raise ValueError("Embedder name cannot be None or empty")


    def __init__(self, vector: list[float], embedder_name: str, 
                 url: str, title: str = "untitled", pages: str = "-1", text: str = "", authors: list[str] = ["unknown"]):
        """
        Initializes a RAG data model for storing and retrieving data from a vectorial database.
        """

        super().__init__(url, title, pages, text, authors)

        if (vector is None or vector.__len__() == 0):
            raise ValueError("Vector cannot be None or empty")
        if (embedder_name is None or embedder_name.strip() == ""):
            raise ValueError("Embedder name cannot be None or empty")

        
    @override
    def generate_JSON_data(self) -> dict[str, any]:
        """
        Returns a dictionary representation of the object for vectorial database storage.
        """

        return {
            "vector": [float],
            "text": str,
            "metadata": {
                "url": str,
                "title": str,
                "pages": str,
                "author": [str],
                "embedder": str
            }	
        }
        