from typing import override

from src.common.constants import (Featured_storage_DB_engines_enum as storage_engines, 
                                  Featured_RAG_DB_engines_enum as RAG_engines,
                                  DB_use_types_enum as DB_usage,
                                  Featured_embedding_models_enum as embed_models, 
                                  Featured_chatBot_models_enum as chatBot_models)

from src.models.interfaces.config_interfaces import (Configuration_model_I, DB_config_I)



class Storage_DB_config(DB_config_I):
    """
    Set of configurations for a featured storage database connection.
    Needed by the DB operator factory for class initialization.
    """
    @override
    def __init__(self, db_engine: storage_engines, connection_url: str=None, port: int=None, database_name: str=None,
                 username: str=None, password: str=None):
        if(db_engine is None):
            raise ValueError("the parameter 'db_engine' must be provided.")
        if not storage_engines.has_value(db_engine.value):
            raise ValueError(f"DB engine {db_engine} is not supported as a {DB_usage.STORAGE} DB")
        
        self.usage_type = DB_usage.STORAGE
        self.db_engine = db_engine
        self.connection_url = connection_url
        self.port = port
        self.database_name = database_name
        self.username = username
        self.password = password




class RAG_DB_config(DB_config_I):
    """
    Set of configurations for a featured RAG database connection.
    Needed by the DB operator factory for class initialization.
    """
    @override
    def __init__(self, db_engine: RAG_engines, api_key: str=None, connection_url: str=None, database_name: str=None, 
                 batch_size: int=100000):
        if(db_engine is None):
            raise ValueError("the parameter 'db_engine' must be provided.")
        if not RAG_engines.has_value(db_engine.value):
            raise ValueError(f"DB engine {db_engine} is not supported as a {DB_usage.RAG} DB")
        
        self.usage_type = DB_usage.RAG
        self.db_engine = db_engine
        self.api_key = api_key
        self.connection_url = connection_url
        self.database_name = database_name
        self.batch_size = batch_size




class Embedder_config(Configuration_model_I):
    """
    Set of configurations for an embedder model.
    Needed by the embedder factory for class initialization.
    """
    def __init__(self, embedder_model_name: embed_models, embedder_api_key: str):
        if((embedder_model_name is None) or 
           (embedder_api_key is None) or (embedder_api_key.strip() == "") ):
            raise ValueError("The embedder model name and API key cannot be None or empty.")
        if(not embed_models.has_value(value=embedder_model_name.value)):
            raise ValueError(f"Embedding model '{embedder_model_name.value}' not featured")
        
        self.embedder_model_name = embedder_model_name
        self.embedder_api_key = embedder_api_key
        
        


class Chatbot_config:
    def __init__(self, chatbot_model_name: chatBot_models, api_key: str, other_params: dict[str, any] = None):
        if(chatbot_model_name is None or api_key is None or api_key.strip() == ""):
            raise ValueError("The chatBot model name and API key cannot be None or empty.")
        
        self.chatbot_model_name: chatBot_models = chatbot_model_name
        self.api_key: str = api_key
        self.other_params: dict[str, any] = other_params