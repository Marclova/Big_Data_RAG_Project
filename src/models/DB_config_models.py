from src.common.constants import (Featured_storage_DB_engines_enum as storage_engines, 
                                  Featured_RAG_DB_engines_enum as RAG_engines,
                                  DB_use_types_enum as DB_usage)

from src.models.interfaces.DB_config_interface import DB_config_I



class Storage_DB_config(DB_config_I):
    """
    Set of configurations for a featured storage database connection.
    Needed by the DB operator factory for class initialization.
    """
    def __init__(self, db_engine: str, connection_url: str, database_name: str):
        if not storage_engines.has_value(db_engine):
            raise ValueError(f"DB engine {db_engine} is not supported as a {DB_usage.STORAGE} DB")
        
        self.usage_type = DB_usage.STORAGE
        self.db_engine = db_engine  # ex. "MongoDB"
        self.connection_url = connection_url
        self.database_name = database_name



class RAG_DB_config(DB_config_I):
    """
    Set of configurations for a featured RAG database connection.
    Needed by the DB operator factory for class initialization.
    """
    def __init__(self, db_engine: str, api_key: str, environment: str, index_name: str):
        if not RAG_engines.has_value(db_engine):
            raise ValueError(f"DB engine {db_engine} is not supported as a {DB_usage.RAG} DB")
        
        self.usage_type = DB_usage.RAG
        self.db_engine = db_engine  # ex. "Pinecone"
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
