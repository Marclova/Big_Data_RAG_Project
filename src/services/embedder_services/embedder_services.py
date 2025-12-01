from typing import override
import numpy
from numpy.typing import NDArray

from pinecone import Inference, Pinecone
from pinecone.inference.models.embedding_list import EmbeddingsList
from pinecone.core.openapi.inference.model.embedding import Embedding

from services.embedder_services.interfaces.embedder_interfaces import Embedder_I

from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index.core.vector_stores import (VectorStoreQuery, VectorStoreQueryResult)


floatVector = list[float]

class Pinecone_embedder(Embedder_I):
    """
    This class uses the Pinecone API for embedding text files (ex. TXT, PDF).
    """
    def __init__(self, embedder_model_name, embedder_api_key):
        self.embedder: Inference = Pinecone(api_key=embedder_api_key).inference
        self.embedder_name = embedder_model_name

    
    #TODO(testing): The 'Embedding' data structure may be not as expected
    @override
    def generate_vectors_from_textChunks(self, textChunkList) -> dict[str,floatVector]:
        dict_to_return: dict[str,floatVector] = dict()

        #I don't trust the library to return a correctly ordered list, so I use the 'embed' function with one element at time
        for text in textChunkList:
            embeddings_list: EmbeddingsList = self.embedder.embed(model=self.embedder_name, inputs=[text])
            embedding: Embedding = embeddings_list.__getitem__(0)
            vector: floatVector = embedding.get("values")

            dict_to_return.update({text:vector})
        return dict_to_return


    @override
    def get_embedder_name(self) -> str:
        return self.embedder_name        



class OpenAI_embedder(Embedder_I):
    """
    This class uses the HuggingFace API for embedding text files (ex. TXT, PDF).
    """

    def __init__(self, embedder_model_name, embedder_api_key):
        self.embedder = OpenAIEmbedding(api_key=embedder_api_key, model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL)
        self.embedder_name = embedder_model_name

    def generate_vectors_from_textChunks(self, textChunkList: list[str]) -> dict[str,floatVector]:
        embeddings_dict: dict[str,floatVector] = dict()

        for text in textChunkList:
            # 'ndarray[float]'s
            np_raw_vector_array = numpy.array(self.embedder.get_text_embedding(text, dtype=float))
            # 'float'
            norm = numpy.linalg.norm(np_raw_vector_array)

            if (norm == 0):
                np_normalized_vector_array = np_raw_vector_array
            else:
                np_normalized_vector_array = np_raw_vector_array / norm
            
            # add a new '{text:floatVector}'
            embeddings_dict[text] = np_normalized_vector_array.tolist()
        return embeddings_dict


    def get_embedder_name(self):
        return OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL




# # ---------------------------------------------------------------------------------------
# def main():
#     # Initialize a Pinecone client with your API key
#     pc = Pinecone(api_key="pcsk_MsR7p_Jbw3Zr62guG3NRcmCTJLQBWzXoVgFQd8qmif2ABNkLB9B27LbLwbgjhTpGsSTs8")

#     # Define a sample dataset where each item has a unique ID and piece of text
#     data = [
#         {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
#         {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
#         {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
#         {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
#         {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
#         {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
#     ]

#     # Convert the text into numerical vectors that Pinecone can index
#     embeddings: EmbeddingsList = pc.inference.embed(
#         model="llama-text-embed-v2",
#         inputs=[d['text'] for d in data],
#         parameters={"input_type": "passage", "truncate": "END"}
#     )

#     print(embeddings)

# if __name__ == "__main__":
#     main()