from typing import override
from pinecone import Inference, Pinecone
from pinecone.inference.models.embedding_list import EmbeddingsList
from pinecone.core.openapi.inference.model.embedding import Embedding

from services.embedder_services.interfaces.embedder_interfaces import Embedder_I



class Pinecone_embedder(Embedder_I):
    """
    This class uses the Pinecone API for embedding text files (ex. TXT, PDF).
    """
    def __init__(self, embedder_model_name, embedder_api_key):
        self.embedder: Inference = Pinecone(api_key=embedder_api_key).inference
        self.embedder_name = embedder_model_name

    
    #TODO(testing): The 'Embedding' data structure may be not as expected
    @override
    def generate_vectors_from_textChunks(self, textChunkList) -> dict[str,list[float]]:
        dict_to_return: dict[str,list[float]] = dict()

        #I don't trust the library to return a correctly ordered list, so I use the 'embed' function with one element at time
        for text in textChunkList:
            embeddings_list: EmbeddingsList = self.embedder.embed(model=self.embedder_name, inputs=[text])
            embedding: Embedding = embeddings_list.__getitem__(0)
            vector: list[float] = embedding.get("values")

            dict_to_return.update({text:vector})
        return dict_to_return


    @override
    def get_embedder_name(self) -> str:
        return self.embedder_name        



#TODO(before merge): implement class
class HuggingFace_embedder(Embedder_I):
    """
    This class uses the HuggingFace API for embedding text files (ex. TXT, PDF).
    """
    pass



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