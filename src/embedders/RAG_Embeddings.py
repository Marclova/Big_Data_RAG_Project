#!/usr/bin/env python
# coding: utf-8

# In[2]:


get_ipython().system('pip install pymongo')
get_ipython().system('pip install pymupdf')
get_ipython().system('pip install sentence-transformers')
get_ipython().system('pip install torch --upgrade')
get_ipython().system('pip uninstall transformers sentence-transformers -y')
get_ipython().system('pip install transformers sentence-transformers')
get_ipython().run_line_magic('pip', 'install torch==1.9.0')
get_ipython().run_line_magic('pip', 'install transformers --upgrade')


# In[1]:


from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF


# In[2]:


client = MongoClient("mongodb://localhost:27017/")
print(client.list_database_names())


# In[3]:


VOLUME_ID = "3500"  # Burayı değiştirebilirsin
BASE_URL = f"https://ceur-ws.org/Vol-{VOLUME_ID}/"


# In[4]:


def get_pdf_links(volume_url):
    response = requests.get(volume_url)
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = [BASE_URL + a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")]
    return pdf_links

pdf_urls = get_pdf_links(BASE_URL)
print(f"{len(pdf_urls)} PDF found!")


# In[5]:


def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    pdf_path = "temp.pdf"
    
    # Save the PDF
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    # Open pdf and extract the text
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])

    return text

# Sample test
pdf_url = "https://ceur-ws.org/Vol-3500/paper1.pdf"  # CEUR'dan bir PDF URL
sample_text = extract_text_from_pdf(pdf_url)
print(sample_text[:500])  # İlk 500 karakteri göster


# In[6]:


from sentence_transformers import SentenceTransformer

# Upload the model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("The model was succesfully uploaded!")



# In[7]:


def convert_text_to_embeddings(text):
    sentences = text.split("\n")  # Her satırı bir cümle olarak kabul edebiliriz
    embeddings = model.encode(sentences)  # Model ile embedding'e çevir
    return embeddings


# In[10]:


# Save the data to MongoDB
def save_embeddings_to_mongodb(embeddings, sentences, db_name="ceur_papers", collection_name="embeddings"):
    client = MongoClient("mongodb://localhost:27017/")  # MongoDB bağlantısı
    db = client[db_name]
    collection = db[collection_name]
    
    for i, embedding in enumerate(embeddings):
        document = {
            "text": sentences[i],
            "embedding": embedding.tolist()  # Numpy array'ini listeye çeviriyoruz
        }
        collection.insert_one(document)

    print("Data was succesfully uploaded to MongoDB!")


# In[11]:


def process_pdf_and_store(pdf_url):
    # Load the model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Extract the text from the pdf
    text = extract_text_from_pdf(pdf_url)
    
    # Transform the text to Embedding
    embeddings = convert_text_to_embeddings(text)
    
    # Save to MongoDB
    save_embeddings_to_mongodb(embeddings, text.split("\n"))

# Start the process with pdf URL
pdf_url = "https://ceur-ws.org/Vol-3500/paper1.pdf"  
process_pdf_and_store(pdf_url)


# In[3]:


from langchain.chains import RetrievalQA
from langchain.llms import OpenAI  # or HuggingFaceHub
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from typing import List


# In[10]:


class MongoDBRetriever(BaseRetriever):
    def __init__(self, db_name="ceur_papers", collection_name="embeddings", top_k: int = 5):
        super().__init__()
        # These are not Pydantic fields — internal use only
        self._client = MongoClient("mongodb://localhost:27017/")
        self._db = self._client[db_name]
        self._collection = self._db[collection_name]
        self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self._top_k = top_k

    def _get_relevant_documents(self, query: str) -> List[Document]:
        query_embedding = self._model.encode([query])[0]

        docs = list(self._collection.find())

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        scored_docs = [
            (doc["text"], cosine_similarity(query_embedding, np.array(doc["embedding"])))
            for doc in docs
        ]

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_docs = scored_docs[:self._top_k]

        return [Document(page_content=text, metadata={}) for text, _ in top_docs]


# In[14]:


from langchain.chat_models import ChatOpenAI
  # UPDATED import for latest LangChain
from langchain.chains import RetrievalQA

# Initialize the OpenAI language model
llm = ChatOpenAI(
    openai_api_key="sk-proj-eJOe.........",
    model="gpt-3.5-turbo"
)

# Initialize your custom MongoDB retriever
retriever = MongoDBRetriever()

# Create a Retrieval-QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True  # This means the output is a dict
)

# Ask a question
query = "What are the main contributions of paper1?"

# Use invoke() instead of run() because multiple outputs exist
response = qa_chain.invoke({"query": query})

# Print results
print("Answer:")
print(response["result"])

print("\nSource Preview:")
for i, doc in enumerate(response["source_documents"], 1):
    print(f"\nSource {i}:")
    print(doc.page_content[:300])  # print a short preview of each source


# In[6]:





# In[2]:





# In[ ]:




