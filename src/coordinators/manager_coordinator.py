from src.models.config_models import (Chatbot_config, Storage_DB_config, RAG_DB_config, Embedder_config)
from src.models.data_models import (RAG_DTModel, Storage_DTModel)

from src.managers.DB_managers import (Storage_DB_manager, RAG_DB_manager)
from src.managers.embedding_managers import Embedding_manager
from src.managers.chatBot_managers import ChatBot_manager


#TODO(CREATE): finish implementing class
#TODO(FIX): Implement a check to make sure that new embeddings ain't going to create incongruence
#               (mixed vector types in the same collection)
#TODO(MINOR REFACTOR): create a 'generic_manager_I' interface for all managers to implement (method 'disconnect' at least)
class Manager_coordinator:
    """
    General manager orchestrating other managers in order to permit strict collaboration between managers
        while avoiding horizontal and cyclic dependencies.
    It also permits to check incongruent configurations between managers.
    """
    def __init__(self, storage_conf: Storage_DB_config, rag_conf: RAG_DB_config,
                 embedder_config: Embedder_config, chatbot_config: Chatbot_config):
        self.storage_DB_manager = Storage_DB_manager(storage_conf)
        self.rag_DB_manager= RAG_DB_manager(rag_conf)
        self.embedding_manager= Embedding_manager(embedder_config)
        self.chatbot_manager= ChatBot_manager(chatbot_config)


    def embed_files_from_URLs_and_store_embeddings_into_RAG_DB(self, file_URLs: list[str]) -> tuple[bool, list[str]]:
        """
        Generates embeddings from a list of file URLs and stores them in the RAG database.
        Parameters:
            file_URLs (list[str]): A list of URLs leading to the files to embed and store.
        Returns:
            tuple[bool,list[str]]: A tuple where the first element is the overall success status,
                                        and the second element is a list of failed URLs (if any).
                                    NOTE: If the first element is True, the second element will be an empty list.
        """
        failed_URLs: list[str] = []

        for file_URL in file_URLs:
            try:
                embeddings: list[RAG_DTModel] = self.embedding_manager.generate_embeddings_from_URL(file_URL)
                self.rag_DB_manager.insert_records(embeddings)
            except Exception as e:
                print(f"Failed to process URL {file_URL}: {str(e)}") #TODO(polishing): consider another logging method
                failed_URLs.append(file_URL)

        overall_success: bool = len(failed_URLs) == 0
        return (overall_success, failed_URLs)
    

    def disconnect_all_managers(self) -> None:
        """
        Disconnects all managed database connections.
        """
        self.storage_DB_manager.disconnect()
        self.rag_DB_manager.disconnect()
        self.embedding_manager.disconnect()
        self.chatbot_manager.disconnect()