from src.models.config_models import (Chatbot_config, Storage_DB_config, RAG_DB_config, Embedder_config)
from src.models.data_models import (RAG_DTModel, Storage_DTModel)

from src.managers.DB_managers import (Storage_DB_manager, RAG_DB_manager)
from src.managers.embedding_managers import Embedding_manager
from src.managers.chatBot_managers import ChatBot_manager



#TODO(FIX): Implement a check to make sure that new embeddings ain't going to create incongruence
#               (mixed vector types in the same collection)
class Manager_coordinator:
    """
    General manager orchestrating other managers in order to permit strict collaboration between managers
        while avoiding horizontal and cyclic dependencies.
    It also permits to check incongruent configurations between managers.
    """
    def __init__(self, storage_db_manager: Storage_DB_manager, rag_db_manager: RAG_DB_manager,
                 embedding_manger: Embedding_manager, chatbot_manager: ChatBot_manager,
                 default_RAG_DB_index_name: str, default_Storage_DB_collection_name: str):
            
            if(storage_db_manager == None or rag_db_manager == None or 
               embedding_manger == None or chatbot_manager == None or 
               default_Storage_DB_collection_name == None or default_RAG_DB_index_name == None):
                raise ValueError("No parameter may be 'None'")
            
            self.storage_DB_manager = storage_db_manager
            self.rag_DB_manager= rag_db_manager
            self.embedding_manager= embedding_manger
            self.chatbot_manager= chatbot_manager

            self.default_RAG_DB_index_name = default_RAG_DB_index_name
            self.default_Storage_DB_collection_name = default_Storage_DB_collection_name


    #TODO(REFACTOR FIX): manage 'over maximum batch size' cases (recommended to begin working with 'batch_size', in DB configuration models)
    def ingest_all_documents_from_storage(self, target_storage_collection_name: str = None, 
                                          target_RAG_index_name: str = None) -> tuple[bool, list[str]]:
        """
        Ingest all documents from a storage collection and stores the resulting embeddings 
        into a RAG index.
        Parameters:
            target_storage_collection_name (str, optional):
                The name of the storage collection from which to retrieve documents. 
                If None, uses a default collection name.
            target_RAG_index_name (str, optional):
                The name of the RAG index where embeddings will be stored. 
                If None, uses a default index name.
        Returns:
            tuple[bool,list[str]]:
                A tuple containing:
                - bool: True if the overall ingestion was successful, False otherwise.
                - list[str]: A list of document identifiers whose ingestion failed (partial failure is not distinguished)
        """
        storage_DTModel_list: list[Storage_DTModel] = self.storage_DB_manager.get_all_records(target_storage_collection_name)
        urls_list: list[str] = [ model.url for model in storage_DTModel_list]

        return self.ingest_documents_from_urls(urls_list, target_RAG_index_name)


    def ingest_documents_from_urls(self, file_URLs: list[str], 
                                   target_RAG_index_name: str = None) -> tuple[bool, list[str]]:
        """
        Generates embeddings from a list of file URLs and stores them in the RAG database.
        Parameters:
            file_URLs (list[str]): A list of URLs leading to the files to embed and store.
            target_RAG_index_name (str): The name of the target index in the RAG database where to store the embeddings.
                                     If not provided, the default index name is used.
        Returns:
            tuple[bool,list[str]]: A tuple where the first element is the overall success status,
                                        and the second element is a list of failed URLs (if any).
                                    NOTE: If the first element is True, the second element will be an empty list.
        """
        if target_RAG_index_name is None:
            target_RAG_index_name = self.default_RAG_DB_index_name

        failed_URLs: list[str] = []
        for file_URL in file_URLs:
            try:
                embeddings: list[RAG_DTModel] = self.embedding_manager.generate_embeddings_from_URL(file_URL)
                self.rag_DB_manager.insert_records(target_collection_name=target_RAG_index_name, data_models=embeddings)
            except Exception as e:
                print(f"Failed to process URL {file_URL}: {str(e)}") #TODO(polishing): consider another logging method
                failed_URLs.append(file_URL)

        overall_success: bool = len(failed_URLs) == 0
        return (overall_success, failed_URLs)
    

    def reply_to_question(self, question: str) -> str:
        """
        Retrieves an answer to a question using the RAG database and the chatbot manager.
        Parameters:
            question (str): The question to be answered.
        Returns:
            str: The answer generated by the chatbot manager.
        """
        retrieved_texts: list[str] = [ dataModel.text for dataModel in self.reply_to_question_raw_response(question) ]
        return self.chatbot_manager.send_message_with_responseInfo(question, retrieved_texts)
    

    def reply_to_question_raw_response(self, question: str) -> list[RAG_DTModel]:
        """
        Retrieves raw results from the RAG database based on a question.
        Parameters:
            question (str): The question to query the RAG database with.
        Returns:
            any: The raw results retrieved from the RAG database.
        """
        vector_query = self.embedding_manager.generate_vector_query_from_text(question)
        return self.rag_DB_manager.retrieve_vectors_using_vectorQuery(vector_query)
    

    def disconnect_all_managers(self) -> None:
        """
        Disconnects all managed database connections.
        """
        self.storage_DB_manager.disconnect()
        self.rag_DB_manager.disconnect()
        self.embedding_manager.disconnect()
        self.chatbot_manager.disconnect()