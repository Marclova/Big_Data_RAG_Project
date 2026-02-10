import requests
from typing import override

from src.common.constants import Featured_embedding_models_enum as embed_models

from src.models.interfaces.data_model_interface import DTModel_I


class Storage_DTModel(DTModel_I):
    """
    Data Transfer model for storing and retrieving data from a vectorial database.
    Each model represents a text chunk and its associated vector.
    Initially the vector and text are empty, they will be filled after the embedding process.
    """
    def __init__(self, url: str, title: str = "untitled", pages: str = "-1", authors: list[str] = ["unknown"]):
        """
        Initializes a data transfer model for storing and retrieving data. 
        Parameters normalization and url check are performed.
        """
        if (url is None):
            raise ValueError("URL cannot be None")
        url, title, pages, authors = _init_params_normalization(url=url, title=title, pages=pages, authors=authors)

        self.url = url
        self.title = title
        self.pages = pages
        self.authors = authors

    @classmethod
    def create_from_JSONData(cls, JSON_data: dict[str, any]):
        """
        Initializes a data transfer model for storing and retrieving data. 
        Parameters normalization and url check are performed.
        """
        if(JSON_data is None):
            raise ValueError("The given dict value for model initialization is 'None'")
        
        try:
            url: str = JSON_data["url"]
            title: str = JSON_data["title"]
            pages: str = JSON_data["pages"]
            authors: list[str] = JSON_data["author"]
        except Exception as e:
            raise ValueError(f"Invalid JSON data provided: {e}")

        return cls(url, title, pages, authors)


    @override
    def generate_JSON_data(self) -> dict[str, any]:
        return {
            "url": self.url,
            "title": self.title,
            "pages": self.pages,
            "author": self.authors
        }



class RAG_DTModel(Storage_DTModel):
    """
    Data model class for RAG (Retrieval-Augmented Generation) data.
    This class defines the structure of the records stored in the RAG database.
    It implements Storage_DTModel because it contains a superset of the fields defined in Storage_DTModel.
    """
    def __init__(self, vector: list[float], text: str, embedder_name: str, 
                 url: str, title: str = "untitled", pages: str = "-1", 
                 authors: list[str] = ["unknown"], id: str = "0"):
        super().__init__(url=url, title=title, pages=pages, authors=authors)
        
        self.id = id
        self.vector = vector
        self.text = text
        self.embedder_name = embedder_name

        self._fields_check()


    @classmethod
    def create_from_StorageDTModel(cls, vector: list[float], text: str, embedder_name: str, 
                                   storage_model: Storage_DTModel, id: str = "0"):
        return cls(vector, text, embedder_name, 
                   storage_model.url, storage_model.title, storage_model.pages, storage_model.authors, id)
        
    
    @classmethod
    def create_from_JSONData(cls, JSON_data: dict[str, any]):
        # Can't call super().__init__ because of different JSON structure        
        try:
            id: str = JSON_data["id"]
            text: str = JSON_data["text"]
            vector: list[float] = JSON_data["vector"]
            url: str = JSON_data["metadata"]["url"]
            title: str = JSON_data["metadata"]["title"]
            pages: str = JSON_data["metadata"]["pages"]
            authors: list[str] = JSON_data["metadata"]["author"]
            embedder_name: str = JSON_data["metadata"]["embedder"]
        except Exception as e:
            raise ValueError(f"Invalid JSON data provided for RAG_DTModel initialization: {e}")
        
        return cls(vector, text, embedder_name, 
                   url, title, pages, authors, id)


    @override
    def generate_JSON_data(self) -> dict[str, any]:
        """
        Returns a dictionary representation of the object for vectorial database storage.
        """
        return {
            "id": self.id,
            "text": self.text,
            "vector": self.vector,
            "metadata": {
                "url": self.url,
                "title": self.title,
                "pages": self.pages,
                "author": self.authors,
                "embedder": self.embedder_name
            }	
        }
    
    

    def _fields_check(self) -> None:
        """
        Checks if all fields are correctly initialized.
        Raises ValueError if any field is invalid.
        Not all fields are checked, only those that are not checked or normalized in the parent class.
        """
        if(self.url == None):
            raise ValueError("URL cannot be None")
        if(self.text is None or self.text == ""):
            raise ValueError("'text' cannot be None or empty")
        if(self.vector is None or self.vector.__len__() == 0):
            raise ValueError("Vector cannot be None or empty")
        if(self.embedder_name is None):
            raise ValueError("Embedder name cannot be None.")
        if(not embed_models.has_value(value=self.embedder_name)):
            raise ValueError(f"Embedder '{self.embedder_name}' is not featured.")
        

    @override
    def __str__(self):
        return self.text
        

    @override
    def __repr__(self):
        return "<- "+self.text+" ->\n"
        



def _init_params_normalization(url: str, title: str = None, pages: str = None, authors: list[str] = None) -> tuple:
        """
        module private function to normalize parameters used for data model initialization.
        Parameters:
            url (str): The url whose validity has to be checked.
            title (str): title to normalize
            authors (list[str]): list to modify in case it's empty.
        Returns:
            tuple: The three corrected parameters (url, title, pages, authors).
        """
        if(url is None):
            raise ValueError("The given url is None")
        # if(not _verify_url(url)):
        #     raise ValueError("The given url is not valid.")

        if((title is None) or (title.strip() == "")):
            title = "untitled"
        else:
            title = title.replace(" ","_")

        if(pages is None):
            pages = "-1"
        else:
            pages = _normalize_pages(pages)

        if((authors is None) or (authors.__len__() == 0)):
            authors = ["unknown"]
        
        return url, title, pages, authors


#TODO(improvement): Correct bug where 'false' is returned mistakenly (It's not caused by flow control)
# def _verify_url(url: str) -> bool:
#     """
#     Verifies if a given URL is reachable.
#         Parameters:
#             url (str): The URL to verify.
#         Returns:
#             bool: True if the URL is reachable, False otherwise.
#     """
#     try:
#         r = requests.head(url, allow_redirects=False, timeout=3)

#         if r.status_code == 200:
#             return True
#         elif r.status_code == 206:
#             print(f"Warning: URL '{url}' returned status code 206 (Partial Content).") #TODO(polishing): consider another logging method
#             return True
#         elif r.status_code in (301, 302, 303, 307, 308):
#             print(f"ERROR: URL '{url}' is a redirect (status code: {r.status_code}).") #TODO(polishing): consider another logging method
#         else:
#             print(f"ERROR: URL '{url}' returned unexpected status code {r.status_code}.") #TODO(polishing): consider another logging method
#     except requests.RequestException as e:
#         print(f"ERROR: URL '{url}' is not reachable or invalid. Retured the following exception: {e}") #TODO(polishing): consider another logging method
#     return False


def _normalize_pages(pages: str) -> str:
    """
    Private method to normalize the 'pages' parameter.
    It removes leading zeros and spaces, and checks for invalid characters.
    If the resulting string is empty or contains invalid characters, it returns "-1".
    Parameters:
        pages (str): The pages string to normalize.
    Returns:
        str: The normalized pages string or "-1" if invalid.
    """
    pages = pages.strip()
    if(not pages.isdigit()):
        return "-1"
    normalized = pages.lstrip("0")
    return normalized if (len(normalized) > 0) else "-1"