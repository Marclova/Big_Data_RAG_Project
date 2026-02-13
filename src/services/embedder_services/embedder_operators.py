import logging
from typing import override
import numpy

from pinecone import Pinecone
from pinecone.inference import Inference
from pinecone.inference.models.embedding_list import EmbeddingsList
from pinecone.core.openapi.inference.model.embedding import Embedding

from src.common.constants import Featured_embedding_models_enum as embed_models

from src.services.embedder_services.interfaces.embedder_interfaces import Embedder_I

from llama_index.embeddings.openai import OpenAIEmbedding


floatVector = list[float]

class Pinecone_embedder(Embedder_I):
    """
    This class uses the Pinecone API for embedding text files (ex. TXT, PDF).
    """
    def __init__(self, embedder_model_name: embed_models, embedder_api_key: str):
        if((embedder_model_name is None) or 
           (embedder_api_key is None) or (embedder_api_key == "")):
            raise ValueError("Embedding model name and API key must be provided")
        if(not embed_models.has_value(value=embedder_model_name.value)):
            raise ValueError(f"Embedding model '{embedder_model_name}' not featured")
        
        self.embedder: Inference = Pinecone(api_key=embedder_api_key).inference
        self.embedder_name: str = embedder_model_name.value


    @override
    def get_configuration_info(self) -> str:
        return ("Embedder: {\n"
                f"   embedder_name: '{self.get_embedder_name()}',\n"
                f"   access_type: 'API key'"
                f"   API_key: '{self.embedder.config.api_key}'\n"
                "}")
    

    @override
    def generate_vectors_from_textChunks(self, textChunkList) -> dict[str,floatVector]:
        if(textChunkList is None):
            raise ValueError("Text chunk list must be provided")
        
        dict_to_return: dict[str,floatVector] = dict()
        #I don't trust the library to return a correctly ordered list, so I use the 'embed' function with one element at time
        for text in textChunkList:
            vector = self.generate_vector_from_text(text)

            dict_to_return.update({text:vector})
        return dict_to_return
    

    @override
    def generate_vector_from_text(self, text: str) -> floatVector:
        if(text is None):
            raise ValueError("Text must be provided")
        
        embeddings_list: EmbeddingsList = self.embedder.embed(model=self.embedder_name, inputs=[text], 
                                                              parameters={"input_type": "passage", "truncate": "END"})
        embedding: Embedding = embeddings_list.__getitem__(0)
        vector: floatVector = embedding.get("values")
        return vector


    @override
    def get_embedder_name(self) -> str:
        return self.embedder_name


    @override
    def delete_sensitive_info(self):
        self.embedder.config.api_key = None



class OpenAI_embedder(Embedder_I):
    """
    This class uses the HuggingFace API for embedding text files (ex. TXT, PDF).
    """

    def __init__(self, embedder_model_name: str, embedder_api_key: str):
        if((embedder_model_name is None) or (embedder_api_key is None)):
            raise ValueError("Embedding model name and API key must be provided")

        self.embedder = OpenAIEmbedding(api_key=embedder_api_key, model=embedder_model_name)
        self.embedder_name: str = embedder_model_name

    def generate_vectors_from_textChunks(self, textChunkList: list[str]) -> dict[str,floatVector]:
        if(textChunkList is None):
            raise ValueError("Text chunk list must be provided")
        
        embeddings_dict: dict[str,floatVector] = dict()
        for text in textChunkList:
            new_vector = self.generate_vector_from_text(text)
            if(new_vector is not None):
                embeddings_dict[text] = new_vector
        return embeddings_dict
    

    def generate_vector_from_text(self, text: str) -> floatVector:
        if(text is None):
            raise ValueError("Text must be provided")
        
        # 'ndarray[float]'
        np_raw_vector_array = numpy.array(self.embedder.get_text_embedding(text))
        # 'float'
        norm = numpy.linalg.norm(np_raw_vector_array)

        if(norm == 0): # null vector
            logging.info(f"[INFO]: the text starting with '{text[:30]}...' results having no information. The resulting vector has been discarded.")
            return None
        elif(norm == 1): # not normalizable or already normalized vector
            np_normalized_vector_array = np_raw_vector_array
        else:
            np_normalized_vector_array = np_raw_vector_array / norm
        
        return np_normalized_vector_array.tolist()


    def get_embedder_name(self):
        return self.embedder_name
    
    @override
    def delete_sensitive_info(self):
        self.embedder.api_key = None