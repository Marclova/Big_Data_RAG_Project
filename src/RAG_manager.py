from interfaces.embedder_interface import Embedder
import services.DB_operator as DB_operator
from together_RAG_system import Together_Embedder

class RAG_Mongo:
    """Solution for RAG system on MongoDB"""

    def __init__(self, DB_connection_url: str, DB_name: str, input_dbCollection_name: str, output_dbCollection_name: str):
        self.inputFiles_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name)
        self.embedding_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name)
        self.input_dbCollection_name = input_dbCollection_name
        self.output_dbCollection_name = output_dbCollection_name

    def get_all_PDF_URLs_from_MongoDB(self) -> dict[str,str]:
        """
        Makes a query to retrieve all PDF from the DB collection set by the __init__ function.
        The used collection is supposed to be a MongoDB collection containing
        
        Returns:
            Dict[str,str]: The list of couples title-URL to download the PDF files from
        """
        return self.inputFiles_DBManager.get_all_titleURL_couples(self.input_dbCollection_name)

    #TODO turn the output into a dict[str, list[float]] to not have data loss
    def embed_all_PDF_from_URLs(self, text_embedder: Embedder, 
                                titleURL_couples: dict[str,str]) -> bool:
        """
        Uses the embedder to embed each of the files listed as URLs.

        Parameters:
            text_embedder (any): An embedder able to embed text files
            titleURL_couples (dict[str,str]): The list of couples title-URL to download the PDF files from.

        Returns:
            bool: True if the embedding has been done correctly, False if at least one error occurred.
        """
        result = True
        for title, url in titleURL_couples.items():
            vectorList = text_embedder.generate_vectorList_as_floatLists_from_URL(url)
            record = {
                "text" : title,
                "embedding" : vectorList
                }
            if self.embedding_DBManager.insert_record_using_JSON(self.output_dbCollection_name, record) == None:
                print("ERROR: '" + title + "' has not been inserted into the DB") #TODO consider another logging method
                result = False
        return result

    # def download_PDF_from_DB():
    #     ...

    # def convert_from_PDF_to_txt():
    #     ...



if __name__ == "__main__":
    # Example usage
    DB_connection_url = "mongodb://localhost:27017/"
    DB_name = "testDB"
    input_dbCollection_name = "records"
    output_dbCollection_name = "embedding_files"

    rag_mongo = RAG_Mongo(DB_connection_url, DB_name, input_dbCollection_name, output_dbCollection_name)
    
    text_embedder = Together_Embedder(".pdf", "togethercomputer/m2-bert-80M-8k-retrieval", "9247636f968300e75c8ed9f7540734db51991313c7798264da83ee877260f2c0")

    titleURL_couples = rag_mongo.get_all_PDF_URLs_from_MongoDB()
    all_right = rag_mongo.embed_all_PDF_from_URLs(text_embedder, titleURL_couples)