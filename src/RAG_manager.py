from interfaces.embedder_interface import Embedder
import services.DB_operator as DB_operator
from embedders.together_RAG_system import Together_Embedder
from models.dataTransfer_model import DT_model


class RAG_Mongo:
    """
    Solution for RAG system on MongoDB
    """
    def __init__(self, DB_connection_url: str, DB_name: str, input_dbCollection_name: str, output_dbCollection_name: str):
        self.inputFiles_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name)
        self.embedding_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name)
        self.input_dbCollection_name = input_dbCollection_name
        self.output_dbCollection_name = output_dbCollection_name


    def get_all_records_from_DB(self) -> list[DT_model]:
        """
        Makes a query to retrieve all PDF from the input DB collection set by the __init__ function.
        The used collection is supposed to be a MongoDB collection containing records with the following fields:\n
        url: str \n
        title: str \n
        pages: str \n
        author: [str]
        Returns:
            list[DT_model]: The list of models containing the data from the DB.
        """
        # return self.inputFiles_DBManager.get_all_titleURL_couples(self.input_dbCollection_name)
        record_list = self.inputFiles_DBManager.get_all_records(self.input_dbCollection_name)
        model_list = list()

        for record in record_list:
            # model_list.append(DT_model(None, None, None, record["url"], record["title"], record["authors"]))
            model_list.append(DT_model(record["url"], record["title"], record["author"]))
        return model_list


    #TODO consider to make this method return a list of models instead of a boolean value
    def embed_all_PDF_from_URLs(self, text_embedder: Embedder, 
                                data_models: list[DT_model]) -> bool:
        """
        Uses the embedder to embed each PDF file from the given models list.
        The embedding is done using the URL of the PDF file to retrieve the file's content.
        The retrieved content and the calculated embedding are then updated both in the data_models list and in the DB.
        The embedding is done using the embedder's generate_vectorList_as_floatLists_from_URL method.

        Parameters:
            text_embedder (Embedder): An embedder able to embed text files
            data_models (list[DT_model]): The list of models containing the data from the DB.
        Returns:
            bool: True if the embedding has been done correctly, False if at least one error occurred.
        """
        global_result = True
        #create a set of vector for each document (contained in the model)
        for model in data_models:
            local_result = True
            vectorDict = text_embedder.generate_vectorDict_from_URL(model.url) #onerous operation

            #create and insert a record in the DB for each cluster-vector couple
            for cluster_index, (text, vector) in enumerate(vectorDict.items()):
                model.update_vector(vector, text, text_embedder.get_embedder_name())        
                if self.embedding_DBManager.insert_record_using_JSON(self.output_dbCollection_name, model.generate_JSON_data()) == None:
                    print(f"ERROR: cluster text [{cluster_index}] of '{model.title}' has not been inserted into the DB") #TODO(unscheduled) consider another logging method
                    global_result = False
                    local_result = False

            if local_result:
                print("INFO: All vectors from '" + model.title + "' have been inserted correctly into the DB") #TODO(unscheduled) consider another logging method
            else:
                print("INFO: At least one vector from '" + model.title + "' have not been inserted into the DB") #TODO(unscheduled) consider another logging method

        print(f"INFO: All {data_models.__len__()} documents have been processed") #TODO(unscheduled) consider another logging method   
        return global_result




if __name__ == "__main__":
    """ Example usage """
    DB_connection_url = "mongodb://localhost:27017/"
    DB_name = "testDB"
    input_dbCollection_name = "records"
    output_dbCollection_name = "embedding_files"

    rag_mongo = RAG_Mongo(DB_connection_url, DB_name, input_dbCollection_name, output_dbCollection_name)
    
    text_embedder = Together_Embedder(".pdf", "togethercomputer/m2-bert-80M-8k-retrieval", "9247636f968300e75c8ed9f7540734db51991313c7798264da83ee877260f2c0")

    titleURL_couples = rag_mongo.get_all_records_from_DB()
    all_right = rag_mongo.embed_all_PDF_from_URLs(text_embedder, titleURL_couples)

    if all_right:
        print("Everything went fine")
    else:
        print("Something went wrong")