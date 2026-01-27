from abc import ABC, abstractmethod

@abstractmethod
class DB_config_I(ABC):
    """
    Marker interface for DB configurations.
    DB_config don't have a more structured common interface because 
        the various DB engines are very various, requiring different parameters.
    """
    @abstractmethod
    def __init__(self, db_engine: str, connection_url: str, *args):
        pass