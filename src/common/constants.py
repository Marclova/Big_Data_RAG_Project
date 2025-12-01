from enum import Enum
from typing import override
from llama_index.embeddings.openai import OpenAIEmbeddingModelType


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
    

#TODO(polishing): define data model values enum


class DB_use_types_enum(_Checks_enum_values_Mixin):
    STORAGE = "storage"
    RAG = "RAG"


class Featured_storage_DB_engines_enum(_Checks_enum_values_Mixin):
    MONGODB = "MongoDB"
    PYGRESQL = "PyGreSQL"
    

class Featured_RAG_DB_engines_enum(_Checks_enum_values_Mixin):
    MONGODB = "MongoDB"
    PINECONE = "Pinecone"


class Featured_embedding_models(_Checks_enum_values_Mixin):
    class __Pincecone_Embedders_enum(_Checks_enum_values_Mixin):
        LLAMA_TEXT_EMBED_V2= "llama-text-embed-v2"
    class __OPENAI_Embedders_enum(_Checks_enum_values_Mixin):
        TEXT_EMBED_3_SMALL = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL

    PINECONE = __Pincecone_Embedders_enum
    OPENAI = __OPENAI_Embedders_enum

    @override
    def has_value(cls, value:str) -> bool:
        return (Featured_embedding_models.PINECONE.has_value(value=value) or
                Featured_embedding_models.OPENAI.has_value(value=value))



#TODO define chatBot models enum