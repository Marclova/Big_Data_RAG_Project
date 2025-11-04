from src.services.db_services.interfaces.DB_operator_interfaces import Storage_DB_operator_I, RAG_DB_operator_I
from src.services.db_services import storage_DB_operator, RAG_DB_operator
from src.models.DB_config_model import DB_config

"""
Factory module to create DB operator instances based on the provided DB configuration.
This module contains a code smell (but it's controlled and centralized): 
    every time a new DB type is added, this factory must be updated consequently.
"""

#Supported DB usage types
STORAGE = "storage"
RAG = "RAG"

#Supported DB engines
MONGODB = "MongoDB"
POSTGRESQL = "PostgreSQL"
PINECONE = "Pinecone"

#Featured DB types for each usage type
featured_DB_types = {
    STORAGE: [MONGODB, POSTGRESQL],
    RAG: [PINECONE, PINECONE] #yes, we're implementing MongoDB as vector DB to provide an easy-to-use option
}



def initialize_storage_db_operator(db_config: DB_config) -> Storage_DB_operator_I:
    """
    Factory method to get the appropriate Storage DB operator based on the DB configuration and the featured DB types.
    """
    try:
        if db_config.usage_type != STORAGE:
            raise ValueError(f"ERROR: Unsupported DB usage type: {db_config.usage_type}. "
                             "Supported usage type for the called factory method is '{STORAGE}'")
        if db_config.db_engine not in featured_DB_types[db_config[STORAGE]]:
            raise ValueError(f"ERROR: Unsupported storage DB type: {db_config.db_engine}. "
                             f"Supported {STORAGE} engines for this factory method are: {featured_DB_types[STORAGE]}")
        
        
        # Define the factory cases; one per supported DB engine.
        if db_config.db_engine == MONGODB:
            return storage_DB_operator.Storage_MongoDB_operator(DB_connection_url=db_config.DB_connection_url, DB_name=db_config.DB_name)
        elif db_config.db_engine == POSTGRESQL:
            #TODO(before push): implement PostgreSQL storage DB operator class and return its instance here
            pass

        raise NotImplementedError(
        f"Dead code activation: No factory case for {db_config.usage_type} {db_config.db_engine}. "
        "Did you update featured_DB_types but forget to extend the factory method?"
        )
    
    except Exception as e:
        print(f"ERROR: Failed to initialize storage DB operator: {e}") #TODO(unscheduled): consider another logging method
        raise e

def initialize_RAG_db_operator(db_config: DB_config) -> RAG_DB_operator_I:
    """
    Factory method to get the appropriate RAG DB operator based on the DB configuration and the featured DB types.
    """
    try:
        if db_config.usage_type != RAG:
            raise ValueError(f"ERROR: Unsupported DB usage type: {db_config.usage_type}. "
                             "Supported usage type for the called factory method is '{RAG}'")
        if db_config.db_engine not in featured_DB_types[RAG]:
            raise ValueError(f"ERROR: Unsupported RAG DB type: {db_config.db_engine}. "
                             f"Supported {RAG} engines for this factory method are: {featured_DB_types[RAG]}")
        
        # Define the factory cases; one per supported DB engine.
        if db_config.db_engine == PINECONE:
            #TODO(before push): implement Pinecone RAG DB operator class and return its instance here
            pass
        elif db_config.db_engine == MONGODB:
            #TODO(before push): implement MongoDB RAG DB operator class and return its instance here
            pass

        raise NotImplementedError(
            f"Dead code activation: No factory case for operator named '{db_config.usage_type}_{db_config.db_engine}_operator'. "
            "Did you update featured_DB_types but forget to extend the factory method?"
        )
    
    except Exception as e:
        print(f"ERROR: Failed to initialize RAG DB operator: {e}") #TODO(unscheduled): consider another logging method
        raise e