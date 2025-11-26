from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I
from src.services.embedder_services.interfaces.embedder_interfaces import Embedder_I

from models.data_models import RAG_DTModel



class RAG_manager:
    """
    Generalized RAG manager to handle text embeddings and chatbot interactions.
    """

    def __init__(self, embedder_model_name: str, embedder_api_key: str, chatBot_APIKey: str):
        self.embedder = Embedder_I(embedder_model_name, embedder_api_key)
        self.chatBot = ChatBot_I(chatBot_APIKey)


    #TODO(before commit): implement method so that the embedder has just the embedding responsibility
    def generate_embeddings_from_URL(self, file_URL: str) -> list[RAG_DTModel]:
        """
        Generates a vector from a file by using the embedder.
        Parameters:
            file_URL (str): The URL leading to the file to embed.
        Returns:
            list[RAG_DTModel]: The list of resulting embeddings obtained from the file.
        """
        minimal_embeddings: dict[str, list[float]] = self.embedder.generate_vectors_from_textChunks(file_URL)
    

    def send_message_with_responseInfo(self, message: str, responseInfo: set[str]) -> str:
        """
        Sends a message to the chatBot and returns the response from the chat.
        Parameters:
            message (str): The message to send.
            responseInfo (set[str]): The info for the response to receive.
        Returns:
            str: The reply from the chatBot
        """
        return self.chatBot.send_message_with_responseInfo(message, responseInfo)


    def get_chat_context_as_JSON(self) -> dict[str,any]:
        """
        Gets a JSON containing the chat context.
        Returns:
            dict[str,any]: The JSON containing all the chat history and used context.
        """
        return self.chatBot.get_chat_context_as_JSON()


    def clear_chat(self) -> bool:
        """
        Clears the chat history and context. Permitting the start of a new chat.
        Returns:
            bool: True if the chat has been deleted. False cache was already empty.
        """
        self.chatBot.clear_chat()


    # def __init__(self, DB_connection_url: str, DB_name: str, storage_collection_name: str, RAG_collection_name: str):
    #     # self.inputFiles_DBManager = storage_DB.Storage_MongoDB_service(DB_connection_url, DB_name)
    #     # self.embedding_DBManager = storage_DB.Storage_MongoDB_service(DB_connection_url, DB_name)
    #     # self.input_dbCollection_name = input_dbCollection_name
    #     # self.output_dbCollection_name = output_dbCollection_name
    #     pass


    # def embed_all_PDF_from_DTModel_URL(self, text_embedder: Embedder) -> bool:
    #     """
    #     Uses the embedder to embed each PDF file from the given models list.
    #     The embedding is done using the URL of the PDF file to retrieve the file's content.
    #     The retrieved content and the calculated embedding are then updated both in the data_models list and in the DB.
    #     The embedding is done using the embedder's generate_vectorList_as_floatLists_from_URL method.

    #     Parameters:
    #         text_embedder (Embedder): An embedder able to embed text files
    #         data_models (list[DT_model]): The list of models containing the data from the DB.
    #     Returns:
    #         bool: True if the embedding has been done correctly, False if at least one error occurred.
    #     """
    #     global_result = True
    #     data_models = self._get_all_records_from_DB()
    #     #create a set of vectors for each document (contained in the model)
    #     for model in data_models:
    #         local_result = True
    #         vectorDict = text_embedder.generate_vectorDict_from_URL(model.url) #onerous operation

    #         #create and insert a record in the DB for each cluster-vector couple
    #         for cluster_index, (text, vector) in enumerate(vectorDict.items()):
    #             model.update(vector, text, text_embedder.get_embedder_name())
    #             if self.embedding_DBManager.insert_record(self.output_dbCollection_name, model.generate_JSON_data()) == None:
    #                 print(f"ERROR: cluster text [{cluster_index}] of '{model.title}' has not been inserted into the DB")
    #                 global_result = False
    #                 local_result = False

    #         if local_result:
    #             print("INFO: All vectors from '" + model.title + "' have been inserted correctly into the DB")
    #         else:
    #             print("WARNING: At least one vector from '" + model.title + "' have not been inserted into the DB")

    #     print(f"INFO: All {data_models.__len__()} documents have been processed")
    #     return global_result


    # def _get_all_records_from_DB(self) -> list[Storage_DTModel]:
    #     """
    #     Makes a query to retrieve all PDF from the input DB collection set by the __init__ function.
    #     The used collection is supposed to be a MongoDB collection containing records with the following fields:\n
    #     url: str \n
    #     title: str \n
    #     pages: str \n
    #     author: [str]
    #     Returns:
    #         list[DT_model]: The list of models containing the data from the DB.
    #     """
    #     # return self.inputFiles_DBManager.get_all_titleURL_couples(self.input_dbCollection_name)
    #     record_list = self.inputFiles_DBManager.get_all_records(self.input_dbCollection_name)
    #     model_list = list()

    #     for record in record_list:
    #         # model_list.append(DT_model(None, None, None, record["url"], record["title"], record["authors"]))
    #         model_list.append(Storage_DTModel(record["url"], record["title"], record["author"]))
    #     return model_list
