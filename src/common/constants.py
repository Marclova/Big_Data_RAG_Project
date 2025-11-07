from enum import Enum



class _Checks_enum_values_Mixin(Enum):
    """
    Interface extended by sub-types of Enum to ensure a value checking functionality.
    """
    @classmethod
    def has_value(cls, value: str) -> bool:
        """
        Checks if the given value matches one of the defined values.
        Parameters:
            value: (str): The value to check.
        Returns:
            bool: True if it matches. False otherwise.
        """
        return value in cls._value2member_map_


class DB_use_types_enum(_Checks_enum_values_Mixin, Enum):
    STORAGE = "storage"
    RAG = "RAG"



class Featured_storage_DB_engines_enum(_Checks_enum_values_Mixin, Enum):
    MONGODB = "MongoDB"
    POSTGRESQL = "PostgreSQL"
    


class Featured_RAG_DB_engines_enum(_Checks_enum_values_Mixin, Enum):
    MONGODB = "MongoDB"
    PINECONE = "Pinecone"
