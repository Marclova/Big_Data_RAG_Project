from interfaces.embedder_interface import Embedder
import RAG_Embeddings
import services.DB_operator as DB_operator

class RAG_Mongo:
    """Solution for RAG system on MongoDB"""

    def __init__(self, DB_connection_url: str, DB_name: str, input_dbCollection_name: str, output_dbCollection_name: str):
        self.inputFiles_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name, input_dbCollection_name)
        self.embedding_DBManager = DB_operator.MongoDB_manager(DB_connection_url, DB_name, input_dbCollection_name)
        self.embedding_dbCollection_name = output_dbCollection_name

    def get_all_PDF_URLs_from_MongoDB(self) -> dict[str,str]: #TODO testing required
        """
        Makes a query to retrieve all PDF from the DB collection set by the __init__ function.
        The used collection is supposed to be a MongoDB collection containing
        
        Returns:
            Dict[str,str]: The list of couples title-URL to download the PDF files from
        """
        return self.inputFiles_DBManager.get_all_titleURL_couples()


    def embed_all_PDF_from_URLs(self, text_embedder: Embedder, titleURL_couples: dict[str,str], 
                                expected_files_extension: str) -> list[list[float]]: #TODO testing required
        """
        Uses the embedder to embed each of the files listed as URLs.

        Parameters:
            text_embedder (any): An embedder able to embed text files
            titleURL_couples (dict[str,str]): The list of couples title-URL to download the PDF files from
            expected_files_extension (str): The expected extension, supposedly shared between all the dealt files.

        Returns:
            list[list[float]]: The list of converted vectors, which may be interpreted as a list[Vectors];\n
            One vector corresponds to a cluster text and the whole vector list should correspond to a document.
        """
        for (title, url) in titleURL_couples:
            vectorList = text_embedder.generate_vectorList_as_floatLists_from_URL(url)
            record = {
                "text" : title,
                "embedding" : vectorList
                }
            if self.embedding_DBManager.insert_record_using_JSON(record) == None:
                print("ERROR: '" + title + "' has not been inserted into the DB") #TODO consider another logging method

    # def download_PDF_from_DB():
    #     ...

    # def convert_from_PDF_to_txt():
    #     ...




if __name__ == "__main__":
    text = RAG_Embeddings.extract_text_from_pdf("https://ceur-ws.org/Vol-3849/forum1.pdf")

    with open("test.txt", 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)