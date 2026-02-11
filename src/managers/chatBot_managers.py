import logging
from typing import override

from src.managers.interfaces.manager_interface import Manager_I
from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I

from src.common.constants import Featured_chatBot_models_enum as chatBot_models

from src.models.config_models import Chatbot_config

from src.services.chatBot_services.chatBot_operators import (BotLibre_chatBot_operator, OpenAI_chatBot_operator)



class ChatBot_manager(Manager_I):
    """
    Generalized chatBot manager to handle chatbot interactions.
    """    
    def __init__(self, bot_config: Chatbot_config):
        self.chatBot: ChatBot_I
        self.chatBot_model_name: str

        self.connect(bot_config)

    
    @override
    def get_configuration_info(self) -> str:
        return self.chatBot.get_configuration_info()


    def send_message_with_responseInfo(self, message: str, responseInfo: set[str]) -> str:
        """
        Sends a message to the chatBot and returns the response from the chat.
        Parameters:
            message (str): The message to send.
            responseInfo (set[str]): The information that the chatBot can use to formulate its response.
        Returns:
            str: The reply from the chatBot
        """
        if( (message is None) or (message.strip() == "") ):
            raise ValueError("The message cannot be empty or None.")
        if((responseInfo is None) or (len(responseInfo) == 0) ):
            raise ValueError("The responseInfo cannot be empty or None.")
        
        return self.chatBot.send_message(message, responseInfo)


    def get_chat_context_as_JSON(self) -> dict[str,any]:
        """
        Gets a JSON containing the chat context.
        Returns:
            dict[str,any]: The JSON containing all the chat history and used context.
        """
        return self.chatBot.get_script_as_JSON()


    def get_chatBot_model_name(self) -> str:
        """
        Gets the name of the chatBot model used by the chatBot_manager.
        Returns:
            str: The name of the chatBot model.
        """
        return self.chatBot_model_name
    

    @override
    def connect(self, connection_config: Chatbot_config) -> bool:
        """
        Connects the manager to outer providers or other kind of sources using the given configurations.
            NOTE: There's not actually a connection being opened, but just a class state set for API requests.
        """
        try:
            self.chatBot = self._chatbot_operator_factory(connection_config)
            self.chatBot_model_name = connection_config.chatbot_model_name.value
        except Exception as e:
            logging.info(f"[ERROR]: Failed to connect with the chatbot service: {e}")

        #TODO(refinement): implement a connection check by performing a get (this operator's API doesn't work)
        return True
    

    @override
    def disconnect(self) -> None:
        """
        Deletes sensible information used for queries.
        """
        self.chatBot.delete_sensitive_info()
    


    def _chatbot_operator_factory(self, bot_config: Chatbot_config) -> ChatBot_I:
        """
        Factory method to create the chatBot operator based on the provided configuration.
        Parameters:
            config (Chatbot_config): The configuration for the chatBot.
        Returns:
            ChatBot_I: The instantiated chatBot operator.
        """
        if(bot_config is None):
            raise ValueError("The chatBot configuration cannot be None.")
        elif(bot_config.chatbot_model_name == chatBot_models.BOTLIBRE):
            return BotLibre_chatBot_operator(bot_config)
        elif(bot_config.chatbot_model_name == chatBot_models.OPENAI):
            return OpenAI_chatBot_operator(bot_config)
        
        raise NotImplementedError(
            f"Dead code activation: No factory case for chatBot model named '{bot_config.chatbot_model_name}'. "
            "Did you update 'Featured_chatBot_models_enum' but forget to extend the factory method?"
        )