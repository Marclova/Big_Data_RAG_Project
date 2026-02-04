from abc import ABC, abstractmethod


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

#TODO(UPDATE): see how much specific parameters can be added to this interface (evaluation post OpenAI integration)
class ChatBot_config_I(Configuration_model_I):
    """
    Marker interface for chatBot configurations.
    Needed by the chatBot factory for class initialization.
    """
    @abstractmethod
    def __init__(self, *args):
        pass