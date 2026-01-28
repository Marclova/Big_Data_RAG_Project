from abc import ABC, abstractmethod

from src.models.interfaces.config_interfaces import ChatBot_config_I


class ChatBot_I(ABC):
    """
    Interface for chatbots API services, sending requests and exchanging information with the provider.
    It is also included the functionality of momentary storage of the chat history until the program is running.
    Chat history is saved inside the RAM and only one chat at time can be saved.
    """
    @abstractmethod
    def __init__(self, bot_config: ChatBot_config_I):
        """
        Parameters:
            bot_config (ChatBot_config_I): Configuration object for the chatBot service.
        """
        pass

    @abstractmethod
    def set_chatbot_script(self, script_content: list[str]) -> bool:
        """
        Method to set the bot's script with the provided content.
        Information about the bot and script IDs should be already set up in the object.
        Parameters:
            script_content (list[str]): A list of strings representing the content to set as the bot's script.
        Returns:
            bool: True if the script was set successfully. False otherwise.
        """
        pass

    @abstractmethod
    def send_message_with_responseInfo(self, message: str, responseInfo: set[str]) -> str:
        """
        Method to send a message to the chatBot and receive a response.
        Parameters:
            message (str): The message to send to the bot. 
                            Presumably a question regarding the content of the papers stored in the storage DB.
            responseInfo (set[str]): A list of text chunk to use as information for the chatBot to use as base. 
                                        Presumably retrieved with a RAG search.
        Returns:
            str: The raw string of the content of the bot's response.
        """
        pass

    @abstractmethod
    def get_chat_context_as_JSON(self) -> dict[str,any]:
        """
        Returns all the data saved in the cache.
        Returns:
            dict[str,any]: A JSON containing all the variables' values stored in this object.
        """
        pass

    @abstractmethod
    def clear_chat(self) -> bool:
        """
        Clears the chat history.
        Returns:
            bool: True if the chat has been deleted. False cache was already empty.
        """
        pass
    