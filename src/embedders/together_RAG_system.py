from typing import override
from langchain_together import TogetherEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever

from interfaces.embedder_interface import Embedder

from services import scraper_storage_service, raw_data_operator



class Together_Embedder(Embedder):
  """
  This class implements the Embedder interface using the Together API for embedding text files.
  """
  def __init__(self, default_handled_file_extension: str, together_model_name: str, together_API_key: str):
    self.default_extension = raw_data_operator.normalize_extension(default_handled_file_extension)
    self.embeddings = TogetherEmbeddings(model= together_model_name, api_key= together_API_key)
    self.together_model_name = together_model_name


  @override
  def get_embedder_name(self) -> str:
    return self.together_model_name


  @override
  def generate_vectorDict_from_URL(self, file_url: str) -> dict[str, list[float]]:
    vectorStore = self.generate_vectorStore_from_URL(file_url)
    vectorDict: dict[str, list[float]] = dict()

    for (_, doc) in vectorStore.store.items():
      vectorDict.update({doc["text"] : doc["vector"]})
    return vectorDict
  

  #TODO(testing)
  @override
  def convert_vectorJSON_into_vectorStore(self, vectorJSON: dict[str, any]) -> any:
    vector_store_to_return = InMemoryVectorStore(self.embeddings)

    #insert manually the vectors into the vector store
    new_vectorStore = InMemoryVectorStore(self.embeddings)
    return self.add_vector_to_vectorStore(new_vectorStore, vectorJSON["id"], vectorJSON["vector"], 
                                          vectorJSON["text"], vectorJSON["metadata"])


  def generate_vectorStore_from_URL(self, file_url: str, file_extension: str = None) -> InMemoryVectorStore:
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
    if file_extension == None:
      file_extension = self.default_extension
    else:
      file_extension = raw_data_operator.normalize_extension(file_extension)

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
      InMemoryVectorStore: The generated vectorStore, containing the list of vectors.
    """
    text_to_cluster = scraper_storage_service.get_file_content(filePath)
    clusteredText = raw_data_operator.cluster_text(text_to_cluster)
    
    return self.generate_vectorStore_from_clusteredText(clusteredText)


  def generate_vectorStore_from_clusteredText(self, stringList: list[str]) -> InMemoryVectorStore:
    """
    Embeds a string list into a InMemoryVectorStore, which may be used for semantic retrieval.
    Parameters:
      textList (List[str]): Raw string text to elaborate into a vectorStore. The text is supposed to be already clustered.
    Returns:
      InMemoryVectorStore: The generated vectorStore.
    """
    return InMemoryVectorStore.from_texts(stringList, embedding= self.embeddings)
  

  #TODO(testing)
  #TODO(unscheduled) consider a more efficient solution
  def add_vector_to_vectorStore(self, vector_store: InMemoryVectorStore, 
                                id: str, vector: list[float], text: str, metadata: dict[str, any]) -> InMemoryVectorStore:
    """
    Add a raw vector to the given InMemoryVectorStore.\n
    This method is **not efficient**, as it requires to check if the id is already present in the vector store.
    If the id is already present, it will be increased and checked again until a free id is found.
    Parameters:
      vectorStore (InMemoryVectorStore): The vector store to add the vector to.
      id (str): The id of the vector to add.
      vector (list[float]): The vector to add.
      text (str): The text associated with the vector.
    Returns:
      InMemoryVectorStore: The updated vectorStore.
    """
    while (id in vector_store.store):
      id = raw_data_operator.increase_09az_id_with_carry(id)

    return vector_store.store.update({id: {"id": id, "vector": vector, "text": text, "metadata": {}}})


  #TODO(testing)
  #TODO(unscheduled) add an output limit option (for now seems to be 4 by default) [copilot suggested to do something about top_k]
  #TODO(unscheduled) consider to use a InMemoryVectorStore's method for this functionality instead of creating a VectorStoreRetriever
  def elaborate_most_suitable_sentences_from_vectorStore(self, query: str, vectorStore: InMemoryVectorStore) -> list[str]:
    """
    Converts the given InMemoryVectorStore into a VectorStoreRetriever and returns a List[str] of sentences,
    sorted from the most to the less suitable for semantic similitude.
    Parameters:
      query (str): The natural language query used to retrieve an as much suitable sentence as possible.
      vectorStore (InMemoryVectorStore): The vector store, which generates the retriever effectively executing the functionality.
    Returns:
      list[str]: The result of the retriever's invoke function converted as a List[str] from a List[Document].
    """
    retriever = vectorStore.as_retriever()
    # return self.elaborate_most_suitable_sentences_from_retriever(query, retriever)
    retrieved_documents = retriever.invoke(query)

    return [document.page_content for document in retrieved_documents]
  

  
  # def elaborate_most_suitable_sentences_from_retriever(self, query: str, retriever: VectorStoreRetriever) -> list[str]:
  #   """
  #   Uses the given VectorStoreRetriever to return a List[str] of sentences,
  #   sorted from the most to the less suitable sentence for semantic similitude.
  #   Parameters:
  #     query (str): The natural language query used to retrieve an as much suitable sentence as possible.
  #     retriever (VectorStoreRetriever): The retriever which effectively executes the functionality.
  #   Returns:
  #     list[str]: The result of the retriever's invoke function converted as a List[str] from a List[Document].
  #   """
  #   retrieved_documents = retriever.invoke(query)
  #   return [document.page_content for document in retrieved_documents]



# def _normalize_extension(given_string: str) -> str:
#   """
#   Normalizes the given string to have a leading dot (.) if it doesn't already have one.
#   Parameters:
#     given_string (str): The string to normalize.
#   Returns:
#     str: The normalized string with a leading dot.
#   """
#   if given_string[0] != ".":
#     return ("." + given_string)
#   else:
#     return given_string


# def _extract_clusteredText_from_file(filePath: str) -> list[str]:
#   """
#   Extracts the text from a text file (ex. txt or PDF) and clusters it into a list of strings.
#   Parameters:
#     filePath (str): The path to the file.
#   Returns:
#     list[str]: The clustered text extracted from the file.
#   """
#   doc = pymupdf.open(filePath)    
#   text = "\n".join([page.get_textbox("text") for page in doc])

#   textList = _cluster_text_for_embeddings(text)
  
#   return textList

# def _cluster_text_for_embeddings(text: str) -> list[str]: #TODO(unscheduled) consider a more effective solution
#   return text.split("\n")


# #TODO(testing)
# def _increase_09az_id_with_carry(id: str) -> str:
#   """
#   Increases the given id, which is supposed to be a string of digits and lowercase letters, by one.\n
#   The applied increment includes a carry operation, so that the id is always a string of digits and lowercase letters.\n
#   The returned id may be longer than the original one by one character, which in that case will be completely filled with '0's.\n
#   This method may also work with ids containing characters that are not digits nor lowercase letters,
#   but in that case only the last character will have more probability to be normalized into the expected range.
#   Parameters:
#     id (str): The id to increase.
#   Returns:
#     str: The increased id.
#   """
#   index = len(id) - 1
#   carry = True

#   while not(carry) or index >= 0:
#     #increase the current character
#     id[index] = chr(ord(id[index]) + 1)

#     #check if carry is needed
#     if (id[index] > '9' and id[index] < 'a') or id[index] > 'z':
#       id[index] = '0'
#       index -= 1
#     else:
#       carry = False
  
#   if carry: #if carry is True, we need to add a new character to apply the carry
#     id = '0' + id
#   return id    



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