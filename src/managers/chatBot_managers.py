from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I



#TODO(CREATE) implement chatBot models enum and add parameter validation
class chatBot_manager:
    """
    Generalized chatBot manager to handle chatbot interactions.
    """    
    def __init__(self, chatBot_model_name: str, chatBot_APIKey: str):
        self.chatBot = ChatBot_I(chatBot_APIKey)
        self.chatBot_model_name = chatBot_model_name

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