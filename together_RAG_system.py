from typing import List
from langchain_together import TogetherEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever

class Together_RAG:
  def __init__(self, together_model_name: str, together_API_key: str):
    self.embeddings = TogetherEmbeddings(model= together_model_name, api_key= together_API_key)

  def do_embedding_and_generate_retriever_from_stringList(self, textList: List[str]) -> VectorStoreRetriever:
    """
    Embeds a string list into a VectorStoreRetriever, which may be used for semantic retrieval.
    Parameters:
      textList (List[str]): Raw string data to convert
    Returns:
      VectorStoreRetriever: The generated retriever, ready to invoke queries.
    """
    vectorstore = InMemoryVectorStore.from_texts(textList, embedding= self.embeddings)
    return vectorstore.as_retriever()

  #TODO evaluate if to add an output limit option (for now seems to be 4 by default)
  def retrieve_most_suitable_sentences(self, query: str, vectorStore: VectorStoreRetriever) -> List[str]:
    """
    Uses the given VectorStoreRetriever to return a List[str] of sentences,
    sorted from the most to the less suitable sentence for semantic similitude.
    Parameters:
      query (str): The natural language query used to retrieve an as much suitable sentence as possible.
      vectorStore (VectorStoreRetriever): The vector retriever containing the embedding and effectively executing the functionality
    Returns:
      List[str]: The result of the retriever's invoke function converted as a List[str] from a List[Document].
    """
    retrieved_documents = vectorStore.invoke(query)
    return [document.page_content for document in retrieved_documents]



if __name__ == "__main__":
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
  t_RAG = Together_RAG(model_name, together_API_key)
  retriever = t_RAG.do_embedding_and_generate_retriever_from_stringList(textList)
  retrieved_sentences = t_RAG.retrieve_most_suitable_sentences(query, retriever)

  #print results
  print("\n")
  print("query: " + query)
  print("Most suitable sentence: " + retrieved_sentences[0])
  print("\n")
  print("Ordered sentences list:\n" + str(retrieved_sentences))