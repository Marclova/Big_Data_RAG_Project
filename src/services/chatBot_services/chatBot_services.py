from src.services.chatBot_services.interfaces.chatBot_service_interfaces import ChatBot_I



#TODO(CREATE): implement class
class BotLibre_chatBot_service(ChatBot_I):
    """
    Simple and free chatbot service providing minimal configuration to provide information to the user.
    The provider requires no subscription nor API Key.
    """
    pass



#TODO(CREATE): implement class
class OpenAI_chatBot_service(ChatBot_I):
    """
    Simple chatBot service using a powerful provider that can access to further information through the internet 
    and complex thinking and problem solving.
    The provider requires both an API Key (obtained with a subscription on https://platform.openai.com/api-keys), 
    and a small payment for API responses.
    """
    pass
