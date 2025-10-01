import os
import yaml
from RAG_manager import RAG_Mongo
from embedders.together_RAG_system import Together_Embedder


#TODO implement a proper main with a user options menu
if __name__ == "__main__":

    #TODO Use the yaml file only when the users wants to use default parameters
    #load params from yaml file
    params_path = os.path.join(os.path.dirname(__file__), "params.yaml")
    with open(params_path, "r") as f:
        params = yaml.safe_load(f)

    DB_connection_url = params["DB_connection_url"]
    DB_name = params["DB_name"]
    input_dbCollection_name = params["input_dbCollection_name"]
    output_dbCollection_name = params["output_dbCollection_name"]
    embedder_model_name = params["embedder_model_name"]
    embedder_API_key = params["embedder_API_key"]

    #TODO adapt the main implementation to the fact that the RAG manager will handle different types of DB and embedders
    rag_mongo = RAG_Mongo(DB_connection_url, DB_name, input_dbCollection_name, output_dbCollection_name)

    text_embedder = Together_Embedder(".pdf", embedder_model_name, embedder_API_key)

    titleURL_couples = rag_mongo.get_all_records_from_DB()
    all_right = rag_mongo.embed_all_PDF_from_DTModel_URL(text_embedder, titleURL_couples)

    if all_right: #TODO consider another logging method
        print("Everything went fine")
    else:
        print("Something went wrong")