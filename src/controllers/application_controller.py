from src.models.interfaces.config_interfaces import DB_config_I
from src.models.config_models import (Chatbot_config, Embedder_config, RAG_DB_config, Storage_DB_config)

from src.models.interfaces.data_model_interface import DTModel_I
from src.models.data_models import RAG_DTModel, Storage_DTModel

from src.managers.DB_managers import Abstract_DB_manager
from src.managers.DB_managers import (RAG_DB_manager, Storage_DB_manager)
from src.managers.chatBot_managers import ChatBot_manager
from src.managers.embedding_managers import Embedding_manager

from src.coordinators.manager_coordinator import Manager_coordinator



class Application_controller:

    def __init__(self, storage_config: Storage_DB_config, rag_config: RAG_DB_config, 
                 embedder_config: Embedder_config, chatbot_config: Chatbot_config, 
                 default_RAG_DB_index_name: str, default_Storage_DB_collection_name: str):
        
        #parameters checks are performed in classes constructors
        self.storage_DB_manager = Storage_DB_manager(storage_config)
        self.rag_DB_manager = RAG_DB_manager(rag_config)
        self.embedding_manager = Embedding_manager(embedder_config)
        self.chatbot_manager = ChatBot_manager(chatbot_config)

        self.storage_DB_name: str = self.storage_DB_manager.get_selected_DB_name()
        self.rag_DB_name: str = self.rag_DB_manager.get_selected_DB_name()
        self.default_RAG_DB_index_name = default_RAG_DB_index_name
        self.default_Storage_DB_collection_name = default_Storage_DB_collection_name

        self.manager_coordinator = Manager_coordinator(self.storage_DB_manager, self.rag_DB_manager,
                                                       self.embedding_manager, self.chatbot_manager, 
                                                       self.default_Storage_DB_collection_name, 
                                                       self.default_RAG_DB_index_name)


    #region Manager_coordinator methods

    def get_configuration_info(self) -> str:
        return self.manager_coordinator.get_configuration_info()

    
    def ingest_all_documents_from_storage(self, target_storage_collection_name: str = None, 
                                          target_RAG_index_name: str = None) -> tuple[bool, list[str]]:
        return self.manager_coordinator.ingest_all_documents_from_storage(target_storage_collection_name, 
                                                                          target_RAG_index_name)


    def ingest_documents_from_urls(self, file_URLs: list[str], 
                                   target_RAG_index_name: str = None) -> tuple[bool, list[str]]:
        return self.ingest_documents_from_urls(file_URLs, target_RAG_index_name)


    def reply_to_question(self, question: str, source_vector_index_name: str = "", top_k: int = 12) -> str:
        return self.manager_coordinator.reply_to_question(question, source_vector_index_name, top_k)


    def reply_to_question_raw_response(self, question: str, source_vector_index_name: str = "", top_k: int = 12) -> list[RAG_DTModel]:
        return  self.manager_coordinator.reply_to_question_raw_response(question, source_vector_index_name, top_k)


    #TODO(FIX): consider to make this method returning a 'dict[str, bool]' in order to represent the outcome on display
    def reconnect_all_managers(self) -> None:
        self.manager_coordinator.reconnect_all_managers()


    def disconnect_all_managers(self) -> None:
        self.manager_coordinator.disconnect_all_managers()
    
    #endregion Manager_coordinator methods


    #region Abstract_DB_manager methods

    def static_insert_record(operating_DB_manager: Abstract_DB_manager, 
                             target_collection_name: str, data_model: DTModel_I) -> bool:
        return operating_DB_manager.insert_record(target_collection_name, data_model)


    def static_update_record(operating_DB_manager: Abstract_DB_manager, 
                             target_collection_name: str, data_model: DTModel_I) -> bool:
        return operating_DB_manager.update_record(target_collection_name, data_model)
    

    def static_reconnect_to_DB(operating_DB_manager: Abstract_DB_manager, 
                               db_config: DB_config_I) -> bool:
        return operating_DB_manager.connect(db_config)


    def static_disconnect_from_DB(operating_DB_manager: Abstract_DB_manager) -> None:
        return operating_DB_manager.disconnect()

    #endregion Abstract_DB_manager methods


    #region Storage_DB_manager methods

    def get_all_storage_records(self, target_collection_name: str) -> list[Storage_DTModel]:
        return self.storage_DB_manager.get_all_records(target_collection_name)


    def get_storage_record_using_title(self, input_collection_name: str, title: str) -> Storage_DTModel:
        return self.storage_DB_manager.get_record_using_title(input_collection_name, title)


    def remove_storage_record_using_title(self, target_collection_name: str, title: str) -> bool:
        return self.storage_DB_manager.remove_record_using_title(target_collection_name, title)

    #endregion Storage_DB_manager methods


    #region RAG_DB_manager methods

    def insert_multiple_RAG_records(self, target_collection_name: str, data_models: list[RAG_DTModel]) -> bool:
        return self.rag_DB_manager.insert_records(target_collection_name, data_models)


    def retrieve_vectors_using_vectorQuery(self, target_collection_name: str, 
                                           vector_query: list[float], top_k: int) -> list[RAG_DTModel]:
        return self.rag_DB_manager.retrieve_vectors_using_vectorQuery(target_collection_name, vector_query, 
                                                                      top_k)
    
    #endregion RAG_DB_manager methods

    
    #region Embedding_manager methods

    def generate_embeddings_from_URL(self, file_URL: str, file_authors = None) -> list[RAG_DTModel]:
        return self.embedding_manager.generate_embeddings_from_URL(file_URL, file_authors)


    def generate_vector_query_from_text(self, text_query: str) -> list[float]:
        return self.embedding_manager.generate_vector_query_from_text(text_query)
    

    def reset_embedder_API_setup(self, connection_config: Embedder_config) -> bool:
        return self.embedding_manager.connect(connection_config)


    def delete_embedder_API_info(self) -> None:
        self.embedding_manager.disconnect()
    
    #endregion Embedding_manager methods


    #region Chatbot_manager methods

    def send_message_with_responseInfo(self, message: str, responseInfo: set[str]) -> str:
        return self.chatbot_manager.send_message_with_responseInfo(message, responseInfo)


    def reset_chatbot_API_setup(self, connection_config: Chatbot_config) -> bool:
        return self.chatbot_manager.connect(connection_config)


    def delete_chatbot_API_info(self) -> None:
        return self.chatbot_manager.disconnect()
    

    def get_configured_storage_DB_name(self) -> str:
        return self.storage_DB_name
    

    def get_configured_RAG_DB_name(self) -> str:
        return self.rag_DB_name
    
    #endregion Chatbot_manager methods