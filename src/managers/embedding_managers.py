from src.common.constants import Featured_embedding_models as embed_models

from src.services.embedder_services.interfaces.embedder_interfaces import Embedder_I
from src.services.other_services import scraper_storage_service as webScraper

from models.data_models import RAG_DTModel



class Embedding_manager:
    """
    Generalized embedding manager to handle text embeddings.
    """

    def __init__(self, embedder_model_name: str, embedder_api_key: str):
        if((embedder_model_name is None) or (embedder_model_name.strip() == "") or 
           (embedder_api_key is None) or (embedder_api_key.strip() == "") ):
            raise ValueError("The embedder model name and API key cannot be None or empty.")
        if(not embed_models.has_value(value=embedder_model_name)):
            raise ValueError(f"Embedding model '{embedder_model_name}' not featured")
        
        self.embedder = Embedder_I(embedder_model_name, embedder_api_key)
        

    #TODO(improvement): If possible, find a way so that the webScraper can gather name, pages and authors from the file
    def generate_embeddings_from_URL(self, file_URL: str, 
                                     file_name: str = None, file_pages: str = None, file_authors = None) -> list[RAG_DTModel]:
        """
        Generates a vector from a file by using the embedder.
        Parameters:
            file_URL (str): The URL leading to the file to embed.
            file_name (str): The expected name of the file to embed (file name detection not implemented, sorry...)
            file_pages (str): The expected pages count of the file to embed (file name detection not implemented, sorry...)
            file_authors (str): The expected authors of the file to embed (file name detection not implemented, sorry...)
        Returns:
            list[RAG_DTModel]: The list of resulting embeddings obtained from the file.
        """
        if((file_URL is None) or (file_URL.strip() == "") ):
            raise ValueError("The file URL cannot be None or empty.")

        textChunkList = webScraper.extract_and_partition_text_from_url(file_URL)
        minimal_embeddings: dict[str, list[float]] = self.embedder.generate_vectors_from_textChunks(textChunkList)

        DTModel_list: list[RAG_DTModel] = []
        for (text, vector) in minimal_embeddings.items():
            DTModel_list.append(
                            RAG_DTModel(vector=vector, embedder_name=self.embedder.get_embedder_name(), url=file_URL, 
                                        title=file_name, pages=file_pages, text=text, authors=file_authors, id=None)
                        )
        return DTModel_list
    

    def get_embedder_name(self) -> str:
        """
        Gets the name of the embedder used by the RAG_manager.
        Returns:
            str: The name of the embedder.
        """
        return self.embedder.get_embedder_name()
