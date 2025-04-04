import re
from pymongo import MongoClient, results

class MongoDB_manager:
    """Solution for MongoDB with collections having records with the columns 'title' and 'url'."""

    def __init__(self, DB_connection_url: str, DB_name: str, collection_name: str):
        self.connection = MongoClient(DB_connection_url)
        self.database = self.connection[DB_name]
        # self.database = MongoClient(DB_connection_url)[DB_name]
        self.collection = self.database[collection_name]
        
        #set title as a unique value
        self.collection.create_index("title", unique=True)


    # def get_all_titleURL_couples(self, input_collection_name: str, title_normalization: bool = True) -> dict[str,str]:
    def get_all_titleURL_couples(self, title_normalization: bool = True) -> dict[str,str]:
        """
        Retrieves all the records in the Mongo collection.

        Parameters:
            input_collection_name (str): The name of the collection to retrieve the files from.

        Returns:
            dict[str,str]: The list of couples title-url to download the PDF files from.
        """
        # input_collection_name = self.database[input_collection_name]
        query_result = self.collection.find()
        # query_result = input_collection_name.find()
        result: dict[str,str] = dict()

        for record in query_result:
            pdf_URL: str = record["url"]
            pdf_title :str = record["title"]

            if title_normalization:
                pdf_title = _title_normalization(pdf_title)
            
            result.update(pdf_title, pdf_URL)
        
        return result
    
    
    #TODO testing needed
    # def insert_record_using_JSON(self, target_collection_name: str, json: dict[any]) -> results.InsertOneResult:
    def insert_record_using_JSON(self, json: dict[any]) -> results.InsertOneResult:
        """
        Insert a new record into the DB using a custom JSON.

        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            json (dict[any]): The JSON script describing the record to insert.
         
        Returns:
           InsertOneResult: The inserted value's representation. Null if no value has been inserted.
        """
        try:
            # target_collection = self.database[target_collection_name]
            # return target_collection.insert_one(json)
            return self.collection.insert_one(json)
        except:
            return None
    

    # def remove_records_using_title(self, target_collection_name: str, title: str, title_normalization: bool = True) -> results.DeleteResult:
    def remove_records_using_title(self, title: str, title_normalization: bool = True) -> results.DeleteResult:
        """
        Retrieves and delete from the Mongo DB a record having the corresponding title

        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            title (str): The name of the article to remove.
        
        Returns:
            DeleteResult: Pymongo's result type for record deletion.
        """
        
        if title_normalization:
                title = _title_normalization(title)
        
        # return self.remove_records_using_manualFilter(target_collection_name, {"title": title})
        return self.remove_records_using_manualFilter({"title": title})
    

    # def remove_records_using_manualFilter(self, target_collection_name: str, filter: dict[any]) -> results.DeleteResult:
    def remove_records_using_manualFilter(self, filter: dict[any]) -> results.DeleteResult:
        """
        Removal function permitting to insert a custom JSON as filter.

        Parameters:
        target_collection_name (str): The name of the existing DB collection where to insert the record into.
        filter (dict[any]): JSON script to use to make the filtered query in the DB.
        
        Returns:
        DeleteResult: Pymongo's result type for record deletion.
        """
        # return self.database[target_collection_name].delete_many(filter)
        return self.collection.delete_many(filter)



def _title_normalization(title: str) -> str:
    """
    Simple string normalization to prevent string issues on queries with titles.
    
    Returns:
        str: Normalized title
    """
    return re.sub(r'[^a-zA-Z0-9 ]', '', title).replace(' ', '_')

# def _URL_normalization(url: str) -> str:
#     ...