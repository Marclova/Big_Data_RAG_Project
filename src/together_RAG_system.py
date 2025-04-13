import pymupdf
from langchain_together import TogetherEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever

from interfaces.embedder_interface import Embedder

from services import scraper_storage_service


class Together_Embedder(Embedder):
  def __init__(self, default_handled_file_extension: str, together_model_name: str, together_API_key: str):
    self.default_extension = _normalize_extension(default_handled_file_extension)
    self.embeddings = TogetherEmbeddings(model= together_model_name, api_key= together_API_key)

  #interface method
  #TODO turn the output into a dict[str, list[float]] to not have data loss
  def generate_vectorList_as_floatLists_from_URL(self, file_url: str) -> list[list[float]]:
    vectorStore = self.generate_vectorStore_from_URL(file_url)
    vectorList: list[list[float]] = list()

    for (_, doc) in vectorStore.store.items():
      vectorList.insert(vectorList.__len__(), doc["vector"]) #force the new collection to be added as a new element
    return vectorList
  
  # #interface method
  # def convert_floatLists_into_vectorStore(self, vectorList: list[list[float]]) -> any: #TODO consider to implement
  #   empty_vectorStore = InMemoryVectorStore.from_texts(None, self.embeddings)
  
  def generate_vectorStore_from_URL(self, file_url: str, file_extension: str = ".") -> InMemoryVectorStore:
    """
    Embeds the text file (ex. txt or PDF) downloaded from the url into a InMemoryVectorStore, 
    which may be used for semantic retrieval after conversion into a VectorStoreRetriever.
    Parameters:
      file_url (str): The url used to download the file to embed.
    Returns:
      InMemoryVectorStore: The generated generate_vectorStore, containing the list of vectors.
    """
    if file_extension == ".":
      file_extension = self.default_extension
    else:
      file_extension = _normalize_extension(file_extension)

    downloaded_file_path = scraper_storage_service.download_file(file_url, file_extension)
    vectorStore = self.generate_vectorStore_from_file(downloaded_file_path)
    scraper_storage_service.delete_file(downloaded_file_path)

    return vectorStore


  def generate_vectorStore_from_file(self, filePath: str) -> InMemoryVectorStore:
    """
    Embeds a text file (ex. txt or PDF) into a InMemoryVectorStore, 
    which may be used for semantic retrieval after conversion into a VectorStoreRetriever.
    Parameters:
      filePath (str): The local path leading to the file to embed.
    Returns:
      InMemoryVectorStore: The generated generate_vectorStore, containing the list of vectors.
    """
    clusteredText = _extract_clusteredText_from_file(filePath)
    
    return self.generate_vectorStore_from_clusteredText(clusteredText)

  def generate_vectorStore_from_clusteredText(self, stringList: list[str]) -> InMemoryVectorStore:
    """
    Embeds a string list into a VectorStoreRetriever, which may be used for semantic retrieval.
    Parameters:
      textList (List[str]): Raw string data to convert
    Returns:
      InMemoryVectorStore: The generated generate_vectorStore, containing the list of vectors.
    """
    return InMemoryVectorStore.from_texts(stringList, embedding= self.embeddings)


  def elaborate_most_suitable_sentences_from_vectorStore(self, query: str, vectorStore: InMemoryVectorStore) -> list[str]:
    """
    Converts the given InMemoryVectorStore into a VectorStoreRetriever and returns a List[str] of sentences,
    sorted from the most to the less suitable sentence for semantic similitude.
    Parameters:
      query (str): The natural language query used to retrieve an as much suitable sentence as possible.
      vectorStore (InMemoryVectorStore): The vector store, which generates the retriever effectively executing the functionality.
    Returns:
      list[str]: The result of the retriever's invoke function converted as a List[str] from a List[Document].
    """
    retriever = vectorStore.as_retriever()
    return self.elaborate_most_suitable_sentences_from_retriever(query, retriever)
  
  #TODO consider to add an output limit option (for now seems to be 4 by default)
  def elaborate_most_suitable_sentences_from_retriever(self, query: str, retriever: VectorStoreRetriever) -> list[str]:
    """
    Uses the given VectorStoreRetriever to return a List[str] of sentences,
    sorted from the most to the less suitable sentence for semantic similitude.
    Parameters:
      query (str): The natural language query used to retrieve an as much suitable sentence as possible.
      retriever (VectorStoreRetriever): The retriever which effectively executes the functionality.
    Returns:
      list[str]: The result of the retriever's invoke function converted as a List[str] from a List[Document].
    """
    retrieved_documents = retriever.invoke(query)
    return [document.page_content for document in retrieved_documents]



def _normalize_extension(given_string: str) -> str:
  """
  Normalizes the given string so that it begins with "."

  Returns:
    str: The normalized string or the same string given.
  """
  if given_string[0] != ".":
    return ("." + given_string)
  else:
    return given_string


def _extract_clusteredText_from_file(filePath: str) -> list[str]:
  doc = pymupdf.open(filePath)    
  text = "\n".join([page.get_textbox("text") for page in doc])

  textList = _cluster_text_for_embeddings(text)
  
  return textList

def _cluster_text_for_embeddings(text: str) -> list[str]: #TODO consider a more effective solution
  return text.split("\n")


if __name__ == "__main__":

  #argument retrieval and chatBot testing
  #Prepare the information to convert into vectors
  textList = ["I like when people stop talking about themselves.", "Removing weapons from the world would not stop wars.",
              "It's quite funny how the sky becomes green sometimes.", "Saitama would win any kind of fighting match, hands down.",
              "Cute cat videos are the most liked", "Ingesting poisonous substances is unhealthy."]
  
  #Pick a query to send to the retriever
  query = "Is the sky green sometimes?"
  # query = "Who's the best in fighting matches?"
  # query = "How to have world peace"
  # query = "I like cat videos"
  
  #Give environment data
  model_name = "togethercomputer/m2-bert-80M-8k-retrieval"
  together_API_key = "9247636f968300e75c8ed9f7540734db51991313c7798264da83ee877260f2c0"
  
  #execute test
  t_RAG = Together_Embedder(".pdf", model_name, together_API_key)
  vectorStore = t_RAG.generate_vectorStore_from_clusteredText(textList)
  retrieved_sentences = t_RAG.elaborate_most_suitable_sentences_from_vectorStore(query, vectorStore)

  #print results
  print("\n")
  print("query: " + query)
  print("Most suitable sentence: " + retrieved_sentences[0])
  print("\n")
  print("Ordered sentences list:\n" + str(retrieved_sentences))
  print("\n")

  print("vectorStore content:\n")
  i = 0
  for _, doc in vectorStore.store.items():
    print(str(i) + ":")
    print("vector length: " + str(doc["vector"].__len__()))
    print("text: " + doc["text"])
    i += 1
  print("\n")