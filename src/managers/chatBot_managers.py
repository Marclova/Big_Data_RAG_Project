from src.common.constants import Featured_chatBot_models_enum as chatBot_models

from src.models.config_models import Chatbot_config
from src.models.interfaces.chatBot_service_interfaces import ChatBot_I

from src.services.chatBot_services.chatBot_operators import (BotLibre_chatBot_operator, OpenAI_chatBot_operator)



#TODO(CREATE) implement chatBot models enum and add parameter validation
class ChatBot_manager:
    """
    Generalized chatBot manager to handle chatbot interactions.
    """    
    def __init__(self, bot_config: Chatbot_config):
        self.chatBot: ChatBot_I = self._chatbot_operator_factory(bot_config)
        self.chatBot_model_name = bot_config.chatbot_model_name.value


    def send_message_with_responseInfo(self, message: str, responseInfo: set[str]) -> str:
        """
        Sends a message to the chatBot and returns the response from the chat.
        Parameters:
            message (str): The message to send.
            responseInfo (set[str]): The info for the response to receive.
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


    def clear_chat(self) -> bool:
        """
        Clears the chat history and context. Permitting the start of a new chat.
        Returns:
            bool: True if the chat has been deleted. False cache was already empty.
        """
        self.chatBot.clear_chat()


    def get_chatBot_model_name(self) -> str:
        """
        Gets the name of the chatBot model used by the chatBot_manager.
        Returns:
            str: The name of the chatBot model.
        """
        return self.chatBot_model_name
    


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