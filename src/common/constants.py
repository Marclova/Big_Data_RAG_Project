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
    

#TODO(polishing): define data model values enum for conversion from dict response to DTModel


class DB_use_types_enum(_Checks_enum_values_Mixin):
    STORAGE = "storage"
    RAG = "RAG"


class Featured_storage_DB_engines_enum(_Checks_enum_values_Mixin):
    MONGODB = "MongoDB"
    PYGRESQL = "PyGreSQL"
    

class Featured_RAG_DB_engines_enum(_Checks_enum_values_Mixin):
    MONGODB = "MongoDB"
    PINECONE = "Pinecone"


class Featured_embedding_models_enum(_Checks_enum_values_Mixin):
    PINECONE_LLAMA_TEXT_EMBED_V2= "llama-text-embed-v2"
    OPEN_AI_TEXT_EMBED_3_SMALL = OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL.value


class Featured_chatBot_models_enum(_Checks_enum_values_Mixin):
    BOTLIBRE = "BotLibre<unnamed>" #no specific model names required
    OPENAI = "OpenAI" #TODO(FIX): specify a specific model name