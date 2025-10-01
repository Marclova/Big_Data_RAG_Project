import re
from pymongo import MongoClient, results


class MongoDB_manager:
    """
    Class to manage the MongoDB connection and operations.
    """
    def __init__(self, DB_connection_url: str, DB_name: str):
        self.connection = MongoClient(DB_connection_url)
        self.database = self.connection[DB_name]
        
        # # set title as a unique value
        # self.collection.create_index("title", unique=True)

    def get_record_using_title(self, input_collection_name: str, title: str) -> dict[any]:
        """
        Retrieves a record in the given Mongo collection using its title.

        Parameters:
            input_collection_name (str): The name of the collection to retrieve the file from.
            title (str): The title of the record to retrieve.
        Returns:
            dict[any]: The record with the given title. None if no record is found.
        """
        return self.database[input_collection_name].find_one({"title": title})

    def get_all_records(self, input_collection_name: str) -> list[dict[any]]:
        """
        Retrieves all the records in the given Mongo collection.

        Parameters:
            input_collection_name (str): The name of the collection to retrieve the files from.

        Returns:
            list[dict[any]]: The list of records in the collection.
        """
        return list(self.database[input_collection_name].find())


    def insert_record_using_JSON(self, target_collection_name: str, json: dict[any]) -> results.InsertOneResult:
        """
        Insert a new record into the DB using a custom JSON to describe the record's content.

        Parameters:
            output_collection_name (str): The name of the existing DB collection where to insert the record into.
            json (dict[any]): The JSON script describing the record to insert.
         
        Returns:
           InsertOneResult: The inserted value's representation. Null if no value has been inserted.
        """

        try:
            return self.database[target_collection_name].insert_one(json)
        except Exception as e:
            # print(f"Error while inserting the record: {e}") #TODO consider another logging method
            return None
        
    
    def update_record_using_JSON(self, target_collection_name: str, json: dict[any]) -> results.UpdateResult:
        """
        Updates a record in the Mongo DB having the corresponding title

        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            title (str): The name of the article to update.
            new_values (dict[any]): The JSON script describing the new values to set in the record.
        
        Returns:
            UpdateResult: Pymongo's result type for record updates.
        """
        title = json.get("title", None)
        if title is None:
            raise ValueError("The input JSON must contain a 'title' field to identify the record to update.")
        
        params_to_update: dict[str,dict[str,any]] = dict()
        params_to_update.update({"$set": dict()})

        # create the update JSON only with the parameters that are present in the input JSON
        for param in ["url", "pages", "author"]:
            param_value = json.get(param, None)
            if param_value is not None:
                 params_to_update["$set"].update({param: param_value})

        return self.database[target_collection_name].update_one({"title": title}, params_to_update)
        
        

    def remove_record_using_title(self, target_collection_name: str, title: str) -> results.DeleteResult:
        """
        Retrieves and delete from the Mongo DB a record having the corresponding title

        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the record into.
            title (str): The name of the article to remove.
        
        Returns:
            DeleteResult: Pymongo's result type for record deletion.
        """
        
        return self.remove_records_using_manualFilter(target_collection_name, {"title": title})
    

    def remove_records_using_manualFilter(self, target_collection_name: str, filter: dict[any]) -> results.DeleteResult:
        """
        Removal function permitting to insert a custom JSON as filter.

        Parameters:
        target_collection_name (str): The name of the existing DB collection where to insert the record into.
        filter (dict[any]): JSON script to use to make the filtered query in the DB.
        
        Returns:
        DeleteResult: Pymongo's result type for record deletion.
        """
        result: results.DeleteResult = self.database[target_collection_name].delete_many(filter)
        if result.deleted_count > 0:
            return result
        return None



# def _title_normalization(title: str) -> str:
#     """
#     Normalizes the title to prevent issues with special characters.
#     Parameters:
#         title (str): The title to normalize.
#     Returns:
#         str: The normalized title.
#     """
#     return re.sub(r'[^a-zA-Z0-9 ]', '', title).replace(' ', '_')