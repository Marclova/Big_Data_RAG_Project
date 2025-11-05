from typing import override
from langchain_together import TogetherEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from models.RAG_data_model import RAG_DTModel
from services.embedder_services.interfaces.embedder_interfaces import Embedder_with_retrieval_I
from src.services.other_services import scraper_storage_service, raw_data_operator


#TODO(before merge): implement class
class HuggingFace_embedder(Embedder_with_retrieval_I):
  """
  This class implements the Embedder interface using the Together API for embedding text files (ex. TXT, PDF).
  This embedder is also used to support argument retrieval for DBs without such native functionality.
  """
  pass

#TODO(testing): Impossible to test without paying fees
class Together_embedder(Embedder_with_retrieval_I):
  """
  This class implements the Embedder interface using the HuggingFace API for embedding text files (ex. TXT, PDF).
  This embedder is also used to support argument retrieval for DBs without such native functionality.
  This embedder requires fees to perform services.
  """
  @override
  def __init__(self, embedder_model_name: str, embedder_api_key: str):
    self.embedder = TogetherEmbeddings(model= embedder_model_name, api_key= embedder_api_key)
    self.together_model_name = embedder_model_name


  @override
  def get_embedder_name(self) -> str:
    return self.together_model_name


  @override
  def generate_vectorDict_from_URL(self, file_url: str) -> dict[str, list[float]]:
    vectorStore = self.generate_vector_from_URL(file_url)
    vectorDict: dict[str, list[float]] = dict()

    for (_, doc) in vectorStore.store.items():
      vectorDict.update({doc["text"] : doc["vector"]})
    return vectorDict
  

  @override
  def generate_vector_from_URL(self, file_url: str) -> list[RAG_DTModel]:
    """
    Embeds the text file (ex. txt or PDF) downloaded from the url into a InMemoryVectorStore, 
    which may be used for semantic retrieval after conversion into a VectorStoreRetriever.
    Parameters:
      file_url (str): The url used to download the file to embed.
      file_extension (str, default=self.default_extension):
        The expected extension of the file to download. If not specified, the default one is picked from the class instance.
    Returns:
      InMemoryVectorStore: The generated vectorStore, containing the list of vectors.
    """
    text_chunks: list[str] = scraper_storage_service.extract_and_partition_text_from_url(file_url)
    vectors: list[list[float]] = self.embedder.embed_documents(text_chunks)
    
    #creating the RAG_DTModels to deliver results
    model_list: list[RAG_DTModel] = list()
    for index in range(0, text_chunks.__len__()-1):
      model_list.append = RAG_DTModel(vector=vectors[index], text=text_chunks[index], 
                                      embedder_name=self.get_embedder_name(), url=file_url,
                                      title=None, pages=None, authors=None)
    return model_list
  

  #TODO(before merge): implement method
  @override
  def retrieve_vectors_using_query(self, target_collection_name: str, query: str, top_k: int) -> list[RAG_DTModel]:
    pass