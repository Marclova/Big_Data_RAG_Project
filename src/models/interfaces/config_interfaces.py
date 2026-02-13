from abc import ABC, abstractmethod

from src.common.constants import (Featured_chatBot_models_enum as chatBot_models)


class Configuration_model_I(ABC):
    """
    Marker interface for any sort of configuration model.
    """



class DB_config_I(Configuration_model_I):
    """
    Marker interface for DB configurations.
    DB_config don't have a more structured common interface because 
        the various DB engines are very various, requiring different parameters.
    """
    @abstractmethod
    def __init__(self, db_engine: str, connection_url: str, *args):
        pass



class Chatbot_config_I(Configuration_model_I):
    """
    Marker interface for chatBot configurations.
    Needed by the chatBot factory for class initialization.
    """
    def __init__(self, chatbot_model_name: chatBot_models, api_key: str):
        if(chatbot_model_name is None or api_key is None or api_key.strip() == ""):
            raise ValueError("The chatBot model name and API key cannot be None or empty.")
        
        self.chatbot_model_name: chatBot_models = chatbot_model_name
        self.api_key: str = api_key