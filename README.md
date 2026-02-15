# Big_Data_RAG_Project
License: MIT
A modular and extendible RAG system permitting to add and interchange used providers and implementations.
The system covers every aspect of a RAG service:
- Source documents storage
- Vectors embedding and storage
- Semantic argument retrieval (including inter-top_k redundance filtering)
- Minimal chatbot chat management
- Minimal GUI

NOTE: This project has been created as commit for an university exam and immediate application for economical purposes is unadvised.


### How to start the program
Fill the 'app_config_input.yaml' file with the required config data and execute the file main.py.
Both files are located in the project root along with this README file.
[see 'app_config_input.yaml and config models' for more info about the yaml file]



## Architecture:
The modularity of the project is based on a layer structure composed in the following way:
    'GUI -> application -> (coordinator -> manager) -> (operator , static service)'

### Brief description of each layer:
- GUI: Responsible to require user input and show the output
- application layer: Responsible to delegate the request to the right manager or coordinator.
- coordinator layer: Mid-layer between the application and manager layers, enabling operations that require coordination between managers. So it is required whenever an operation requires the evolvement of two or more managers.
- manager layer: Needed to apply the 'Abstract Factory Design Pattern', permitting to interchange different implementations to perform the same feature, depending on the selected specialization of the handled interface.
- operator layer: Responsible to provide actual implementation of the features described by the interfaces.
- static services: Useful modules to streamline the code and avoid redundance on static non-ergonomic operations on data and sources.

### implementation rules:
- Horizontal, upwards and two-steps dependencies are forbidden, indeed every module can only call the successive layer.
- The 'Abstract Factory Design Pattern' is applied on the operator layer, so managers must only interact with concrete classes through interfaces and instantiate them trough abstract factory methods.
- Every manager must interact with one and only one operator interface (so multiple and different instances of the same interface are allowed in one single manager are allowed).



## Data flow:
The whole RAG system's activity is composed by 4 distinct phases:
1) Document storage: A storage DB is manually populated with documents containing data to be ingested.
2) Document Ingestion: Documents from the storage DB are ingested by an embedder and converted into vectors. 
Afterwards the vectors are stored into a vectorial DB (metadata and text chunks from the storage DB are copied into the vectorial DB also).
3) Semantic Argument Retrieval: A question is provided by the user and converted into a vector. Afterwards a cosine similarity search is performed (either by the DB itself or by a third party) to provide 'top_k' vectors in response, along with the correlated text chunks.
4) Data presentation: The resulting list of text chunks, containing information matching the user's query, are shown back to the user. The data presentation may be requested both as a raw dataset and as script for a chatbot.

### Data models:
Data format conversion is handled by data models, which may be created both through code variables and JSON data. In the same way they can both distribute data both by accessing to their parameters and by the method 'DTModel_I.generate_JSON_data()'.
The currently featured classes extending 'DT_Model_I' and corrispective accepted JSON data formats are:

- Storage_DTModel:
{
	"url": str,
	"title": str,
	"pages": str,
	"author": [str]
}

- RAG_DTModel:
{
	"id": str,
	"text": str,
	"vector": [float],
	"metadata": {
		"url": str,
		"title": str,
		"pages": str,
		"author": [str],
		"embedder": str
	}
}



## RAGMongoDB
This specific specialization of the 'RAG_DB_operator_I', whose class is called 'RAG_MongoDB_operator', is an adaptation for MongoDB in order to include a built-in cosine vectorial search, performing all the similarity calculations and a basilar intra-top_k redundance filtering.
It has shown satisfactory results with tests performed on a most limited dataset, composed by 3 PDF files compelling 3 different topics.
Excluding the absence of scalability and possible parallelization optimizations, the search algorithm should be efficient.
Here's the humoristic estimation from Marclova:
Best case:
- top_m-candidate-lists generation = O(n)
- top_k-list insertion = O(n)
- intra-top_k redundance filtering = O(Σ(2,k)) -> O(1)

Pedantic overall derivation = O(2n+Σ(2,k))
Simplified overall derivation = O(n)

Worse case:
- top_m-candidate-lists generation = O(n*log(n))
- top_k-list insertion = O(4n+(n-k)*k*log(k)) -> O(n)
- intra-top_k redundance filtering = O(Σ(2,k)+k*(n-k)) -> O(n)

Pedantic overall derivation = O(n*log(n) + 4n + n*k*log(k) - k^2*log(k) + nk - k^2/2 + k/2 - 1)
Simplified overall derivation = O(n log n)

### semantic search
The RAGMongoDB semantic search is composed by the main phases:
- Creation of top_m-candidate-lists: In this phase are created from '1' to 'DB_query_size/batch_size' lists of candidates to be inserted in the resulting 'top_k-list'.
- Candidates comparison and intra-top_k redundance filtering: The candidates are compared one by one with the others as they are inserted in the top_k-list, making sure they are not too similar to each other. If this happens, the closest one to the vector query keeps the place.



## project configuration
### version and modules installation
The project has been tested on the following Python versions: 3.12.9, 3.13.12.

In order to install the required modules it is required to execute the command "pip install -r requirements.txt" in the project root using your environment console.
In case some some of the module installations fail, it has proven to solve the problem to select individually the failed module by typing 'pip install <module_name>'

### Possible issues with PyGreSQL installation:

In case you're facing problems about the file 'libpq.dll', the following procedure is mandatory, unless PygreSQL imports and implementations are manually removed (or commented) from the 'storage_DB_operators.py' file in the project.

The PyGreSQL import for your environment will need PostGreSQL to be installed on the local machine system and, in case the local machine is a Windows pc, it is also necessary to insert "C:\Program Files\PostgreSQL\<version>\bin" as ambient variable into 'path'.
The PostGreSQL installer has to be downloaded from this link: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

### app_config_input.yaml and config models:
The repository already gives you the structured yaml file.
All the defined loose variables and dicts are meant to required by the startup file 'main.py' and by that file only.
Every defined dict is meant to be extracted by using the corresponding string enumeration (defined in '\common\constraints.py') and used to generate a specific specialization instance of the interface 'Configuration_model_I'.

The enumeration 'DB_use_types_enum' is an exception because it is needed for a further specialization of the 'DB_config_I' interface.



## Limitations:
- Databases: Only MongoDB and its built-in variant 'RAGMongoDB' have been tested. 
- RAG data model: The data model 'RAG_DBModel' is not compatible with the Pinecone DBs required data format [see 'Issues and Possible Improvements'].
- Embedding: Only PDF ingestion is implemented. With information loss about the document's structure, layout and images.
- Semantic search: The implementation is not scalable. RAGMongoDB presents a tentative, proposing a 'divide-et-impera' solution which is actually performed entirely in a sequential way though.
- Chatbot: The scripting is poorly managed; simply inserting all the retrieved info and instructions as a message, obscuring it to the user. So a long-term chat is supported with the limitation of performing a semantic search only with the first message from the user, causing the chatbot to not be able to have updated data according with the topic shift in the conversation.
- GUI: It doesn't cover all the provided functionalities. But commented implementation on the controller already exists (only GUI extension is needed).



## Issues and Possible Improvements:
    - RAG_DTModel: The JSON generated by 'RAG_DTModel.generate_JSON_data()' needs to be converted into a new format to fit a standard RAG DB, causing cascade fixes on:
        - The factory method 'RAG_DTModel.create_from_JSONData()'.
        - Classes extending 'DB_operator_I'.
        - Some of the implementation concerning low-level operations on JSONs (in the form of 'dict[str, any]') generated by the modified method (most probably already covered by the previous point, but still needed to be mentioned).
        - Some real-world issues are not handled (es. the provider stop working mid-operation).
        - Ambiguous management of Exception rising and error/info logging (no clear responsibility between layers and logic about when raising an error or when performing a log).
        - Sometimes logs are not caught by the class 'TkinterLogHandler' for unclear reasons (probably due to a misunderstanding of the meant implementation for the library).