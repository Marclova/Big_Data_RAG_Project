from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I
from src.services.embedder_services.interfaces.embedder_interfaces import Embedder_I
from src.services.other_services import scraper_storage_service as webScraper

from models.data_models import RAG_DTModel



class Embedding_manager:
    """
    Generalized embedding manager to handle text embeddings.
    """

    def __init__(self, embedder_model_name: str, embedder_api_key: str, chatBot_APIKey: str):
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
        textChunkList = webScraper.extract_and_partition_text_from_url(file_URL)
        minimal_embeddings: dict[str, list[float]] = self.embedder.generate_vectors_from_textChunks(textChunkList)

        DTModel_list: list[RAG_DTModel] = []
        for (text, vector) in minimal_embeddings.items():
            DTModel_list.append(
                            RAG_DTModel(vector,self.embedder.get_embedder_name(), file_URL, 
                                        file_name, file_pages, text, file_authors, id=None)
                        )
        return DTModel_list
    

    def get_embedder_name(self) -> str:
        """
        Gets the name of the embedder used by the RAG_manager.
        Returns:
            str: The name of the embedder.
        """
        return self.embedder.get_embedder_name()
