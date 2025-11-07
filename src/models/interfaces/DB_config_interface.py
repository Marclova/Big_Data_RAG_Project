from abc import ABC, abstractmethod

@abstractmethod
class DB_config_I(ABC):
    @abstractmethod
    def __init__(self, db_engine: str, *args):
        pass
