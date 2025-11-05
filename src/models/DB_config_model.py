


class DB_config:
    """
    Set of configurations for a database connection.
    It contains all the parameters that may be needed to connect to different types of DBs, 
        so some parameters won't be used depending on the selected DB type.
    This setting class is meant to be extended with minimum effort to add new DB types.
    """

    def __init__(self, usage_type: str, db_engine: str, 
                 api_key: str, environment: str, index_name: str):

        self.usage_type = usage_type  # e.g., "storage" or "RAG"
        self.db_engine = db_engine      # e.g., "MongoDB", "PostgreSQL", "Pinecone"
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
