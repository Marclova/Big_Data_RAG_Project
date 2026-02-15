from abc import ABC, abstractmethod

from src.models.config_models import Chatbot_config


class ChatBot_operator_I(ABC):
    """
    Interface for chatbots API services, sending requests and exchanging information with the provider.
    It is also included the functionality of momentary storage of the chat history until the program is running.
    Chat history is saved inside the RAM and only one chat at time can be saved.
    """
    @abstractmethod
    def __init__(self, bot_config: Chatbot_config):
        """
        Parameters:
            bot_config (ChatBot_config): Configuration object for the chatBot service.
        """
        pass

    @abstractmethod
    def get_commercial_model_name(self) -> str:
        """
        Returns the commercial name of the model. 
        May not coincide with the name used by the API.
        """
        pass

    @abstractmethod
    def get_configuration_info(self) -> str:
        """
        Debugging or final-user display method to represent the information 
        used to initialize this operator (except sensible info)
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
    def clear_chat_history(self) -> None:
        """
        Erases the sequence of messages between the user and the chatbot.
        """

    @abstractmethod
    def send_message(self, message: str) -> str:
        """
        Method to send a message to the chatBot and receive a response.
        Parameters:
            message (str): The message to send to the bot. 
                            Presumably a question regarding the content of the papers stored in the storage DB.
        Returns:
            str: The raw string of the content of the bot's response.
        """
        pass

    @abstractmethod
    def get_script_as_JSON(self) -> dict[str,any]:
        """
        Returns all the data saved in the cache.
        Returns:
            dict[str,any]: A JSON containing all the variables' values stored in this object.
        """
        pass

    @abstractmethod
    def clear_script(self) -> bool:
        """
        Clears the chat history.
        Returns:
            bool: True if the chat has been deleted. False cache was already empty.
        """
        pass

    @abstractmethod
    def delete_sensitive_info(self) -> None:
        """
        Deletes all the sensitive information stored in the object, such as API keys, user IDs, etc.
        This method is meant to be used before the deletion of the object or when the chatBot service is not needed anymore.
        """
        pass