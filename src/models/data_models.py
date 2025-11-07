from typing import override
import requests
from models.interfaces.data_model_interface import DTModel_I



class Storage_DTModel(DTModel_I):
    """
    Data Transfer model for storing and retrieving data from a vectorial database.
    Each model represents a text chunk and its associated vector.
    Initially the vector and text are empty, they will be filled after the embedding process.
    """

    def __init__(self, url: str, title: str = "untitled", pages: str = "-1", text: str = "", authors: list[str] = ["unknown"]):
        """
        Initializes a data transfer model for storing and retrieving data from a vectorial database.
        """

        if (url == None):
            raise ValueError("URL cannot be None")
        url, title, pages, authors = _init_params_normalization(url, title, pages, authors)

        self.url = url
        self.title = title
        self.pages = pages
        self.text = text
        self.authors = authors


    @override
    def generate_JSON_data(self) -> dict[str, any]:
        """
        Returns a dictionary representation of the object for vectorial database storage.
        """

        return {
            "url": str,
            "title": str,
            "pages": str,
            "author": [str]
        }
    

def _init_params_normalization(self, url: str, title: str, authors: list[str]) -> tuple:
        
        _verify_url(url)

        if (title.strip() == ""):
            title = "untitled"
        if (authors.__len__() == 0):
            authors = ["unknown"]
        
        return url, title, authors


def _verify_url(url: str) -> None:
    """
    Verifies if a given URL is reachable.
        Parameters:
            url (str): The URL to verify.

        Returns:
            bool: True if the URL is reachable, False otherwise.
    """
    try:
        r = requests.head(url, allow_redirects=False, timeout=3)

        if r.status_code == 200:
            return True
        elif r.status_code == 206:
            print(f"Warning: URL '{url}' returned status code 206 (Partial Content).") #TODO consider another logging method
            return True
        elif r.status_code in (301, 302, 303, 307, 308):
            print(f"ERROR: URL '{url}' is a redirect (status code: {r.status_code}).") #TODO consider another logging method
        else:
            print(f"ERROR: URL '{url}' returned unexpected status code {r.status_code}.") #TODO consider another logging method
    except requests.RequestException as e:
        print(f"ERROR: URL '{url}' is not reachable or invalid. Retured the following exception: {e}") #TODO consider another logging method
    return False




class RAG_DTModel(Storage_DTModel):
    """
    Data model class for RAG (Retrieval-Augmented Generation) data.
    This class defines the structure of the records stored in the RAG database.
    It implements Storage_DTModel because it contains a superset of the fields defined in Storage_DTModel.
    """

    def __init__(self, vector: list[float], embedder_name: str, storage_model: Storage_DTModel):
        super().__init__(storage_model.url, storage_model.title, storage_model.pages, storage_model.text, storage_model.authors)

        if (vector is None or vector.__len__() == 0):
            raise ValueError("Vector cannot be None or empty")
        if (embedder_name is None or embedder_name.strip() == ""):
            raise ValueError("Embedder name cannot be None or empty")


    def __init__(self, vector: list[float], embedder_name: str, 
                 url: str, title: str = "untitled", pages: str = "-1", text: str = "", authors: list[str] = ["unknown"]):
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
