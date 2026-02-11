import logging
import os
from typing import override

from src.managers.interfaces.manager_interface import Manager_I
from src.services.other_services import scraper_storage_services as webScraper
from src.services.embedder_services.interfaces.embedder_interfaces import Embedder_I

from src.models.config_models import Embedder_config
from src.common.constants import Featured_embedding_models_enum as embed_models

from src.services.embedder_services import embedder_operators
from src.services.other_services import (raw_data_services as rawOperator)

from src.models.data_models import RAG_DTModel



class Embedding_manager(Manager_I):
    """
    Generalized embedding manager to handle text embeddings.
    """
    def __init__(self, config: Embedder_config):        
        self.embedder: Embedder_I
        
        self.connect(config)


    @override
    def get_configuration_info(self) -> str:
        return self.embedder.get_configuration_info()
        

    #TODO(UPDATE): If possible, find a way so that the webScraper can gather authors from the file
    def generate_embeddings_from_URL(self, file_URL: str, file_authors = None) -> list[RAG_DTModel]:
        """
        Generates a vector from a file by using the embedder.
        Parameters:
            file_URL (str): The URL leading to the file to embed.
            file_name (str): The expected name of the file to embed (file name detection not implemented, sorry...)
            file_authors (str): The expected authors of the file to embed (file name detection not implemented, sorry...)
        Returns:
            list[RAG_DTModel]: The list of resulting embeddings obtained from the file.
        """
        if((file_URL is None) or (file_URL.strip() == "") ):
            raise ValueError("The file URL cannot be None or empty.")

        file_path: str = webScraper.download_file(file_URL)
        file_name = os.path.basename(file_path)
        logging.info(f"[INFO]: Embedding file '{file_name} from {file_URL}...'")

        partition_result: dict[str,any] = rawOperator.extract_partition_text_and_metadata_from_file(file_path, pop_file=True)
        textChunkList: list[str] = partition_result["text_chunks"]

        minimal_embeddings: dict[str, list[float]] = self.embedder.generate_vectors_from_textChunks(textChunkList)

        DTModel_list: list[RAG_DTModel] = []
        for (text, vector) in minimal_embeddings.items():
            DTModel_list.append(
                            RAG_DTModel(vector=vector, embedder_name=self.embedder.get_embedder_name(), url=file_URL, 
                                        title=file_name, pages=partition_result["pages_count"], 
                                        text=text, authors=file_authors, id=None)
                        )
        logging.info(f"[INFO]: File '{file_name}' correctly embedded.")
        return DTModel_list
    

    def generate_vector_query_from_text(self, text_query: str) -> list[float]:
        """
        Returns the vector query generated from a natural language query.
        Parameters:
            text_query (str): Basically, a question in natural language to ask the RAG system and the chatbot to answer.
        Returns:
            list[float]: The vector query generated from the natural language query.
        """
        if((text_query is None) or (text_query.strip() == "") ):
            raise ValueError("The text query cannot be None or empty.")
        
        vector_query: list[float] = self.embedder.generate_vector_from_text(text_query)
        return vector_query
    

    def get_embedder_name(self) -> str:
        """
        Gets the name of the embedder used by the RAG_manager.
        Returns:
            str: The name of the embedder.
        """
        return self.embedder.get_embedder_name()
    
    
    @override
    def connect(self, connection_config: Embedder_config) -> bool:
        """
        Connects the manager to outer providers or other kind of sources using the given configurations.
            NOTE: There's not actually a connection being opened, but just a class state set for API requests.
        """
        try:
            self.embedder: Embedder_I = self._embedder_operator_factory(connection_config.embedder_model_name, connection_config.embedder_api_key)
        except Exception as e:
            logging.info(f"[ERROR]: Failed to connect with the embedder service: {e}") #TODO(polishing): consider another logging method
            return False
        return True
        


    @override
    def disconnect(self) -> None:
        """
        Deletes sensible information used for queries.
        """
        self.embedder.delete_sensitive_info()
    


    def _embedder_operator_factory(self, embedder_model_name: embed_models, embedder_api_key: str) -> Embedder_I:
        # Iterating every featured constructor for an embedder
        if(embedder_model_name == embed_models.PINECONE_LLAMA_TEXT_EMBED_V2):
            return embedder_operators.Pinecone_embedder(embedder_model_name=embedder_model_name, embedder_api_key=embedder_api_key)
        elif(embedder_model_name == embed_models.OPEN_AI_TEXT_EMBED_3_SMALL):
            return embedder_operators.OpenAI_embedder(embedder_model_name=embedder_model_name, embedder_api_key=embedder_api_key)
        
        raise NotImplementedError(
            f"Dead code activation: No factory case for embedding model named '{embedder_model_name}'. "
            "Did you update 'Featured_embedding_models_enum' but forget to extend the factory method?"
        )