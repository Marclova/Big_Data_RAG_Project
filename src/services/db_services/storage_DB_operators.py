from typing import override
from pymongo import MongoClient
from pymongo.database import Database
from src.services.db_services.interfaces.DB_operator_interfaces import Storage_DB_operator_I
from src.models.data_models import Storage_DTModel

"""
Service module to manage the connection and operations on a database meant to store raw data before embedding.
Embedding and storage of vectors are handled elsewhere.
Selected DBs are MongoDB and PostgreSQL
"""

class Storage_MongoDB_operator(Storage_DB_operator_I):
    """
    Class to manage the MongoDB connection and operations for storage.
    """
    def __init__(self, DB_connection_url: str, DB_name: str):
        self.connection: MongoClient = None
        self.database: Database = None

        self.open_connection(DB_connection_url, DB_name)


    @override
    def get_record_using_title(self, input_collection_name: str, title: str) -> dict[any]:
        return self.database[input_collection_name].find_one({"title": title})


    @override
    def get_all_records(self, input_collection_name: str) -> list[dict[any]]:
        return list(self.database[input_collection_name].find())


    @override
    def insert_record(self, target_collection_name: str, data_model: Storage_DTModel) -> bool:
        if self.get_record_using_title(target_collection_name, data_model.title) is None:
            try:
                return (self.database[target_collection_name].insert_one({
                    "url": data_model.url,
                    "title": data_model.title,
                    "pages": data_model.pages,
                    "author": data_model.authors
                }) is not None)
            except Exception as e:
                print(f"Error while inserting the paper '{data_model.title}' into '{target_collection_name}': {e}") #TODO(polishing): consider another logging method}
        else:
            print(f"Error while inserting the paper '{data_model.title}' into '{target_collection_name}': record already exists.") #TODO(polishing): consider another logging method
        return None
    

    @override
    def update_record(self, target_collection_name: str, data_model: Storage_DTModel) -> bool:
        if self.get_record_using_title(target_collection_name, data_model.title) is not None:
            try:
                return (self.database[target_collection_name].update_one({
                    "url": data_model.url,
                    "title": data_model.title,
                    "pages": data_model.pages,
                    "author": data_model.authors
                }) is not None)
            except Exception as e:
                print(f"Error while updating the paper '{data_model.title}' into '{target_collection_name}': {e}") #TODO(polishing): consider another logging method}
        else:
            print(f"Error while updating the paper '{data_model.title}' into '{target_collection_name}': record does not exist.") #TODO(polishing): consider another logging method
        return None
        
    
    # def update_record_using_JSON(self, target_collection_name: str, json: dict[any]) -> results.UpdateResult:
    #     """
    #     Updates a record in the Mongo DB having the corresponding title

    #     Parameters:
    #         target_collection_name (str): The name of the existing DB collection where to insert the record into.
    #         title (str): The name of the article to update.
    #         new_values (dict[any]): The JSON script describing the new values to set in the record.
        
    #     Returns:
    #         UpdateResult: Pymongo's result type for record updates.
    #     """
    #     title = json.get("title", None)
    #     if title is None:
    #         raise ValueError("The input JSON must contain a 'title' field to identify the record to update.")
        
    #     params_to_update: dict[str,dict[str,any]] = dict()
    #     params_to_update.update({"$set": dict()})

    #     # create the update JSON only with the parameters that are present in the input JSON
    #     for param in ["url", "pages", "author"]:
    #         param_value = json.get(param, None)
    #         if param_value is not None:
    #              params_to_update["$set"].update({param: param_value})

    #     return self.database[target_collection_name].update_one({"title": title}, params_to_update)
        
        
    @override
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        # return (self.remove_records_using_manualFilter(target_collection_name, {"title": title}) is not None)
        return (self.database[target_collection_name].delete_one({"title": title}).deleted_count > 0)
    

    # def remove_records_using_manualFilter(self, target_collection_name: str, filter: dict[any]) -> results.DeleteResult:
    #     """
    #     Removal function permitting to insert a custom JSON as filter.

    #     Parameters:
    #     target_collection_name (str): The name of the existing DB collection where to insert the record into.
    #     filter (dict[any]): JSON script to use to make the filtered query in the DB.
        
    #     Returns:
    #     DeleteResult: Pymongo's result type for record deletion.
    #     """
    #     result: results.DeleteResult = self.database[target_collection_name].delete_many(filter)
    #     if result.deleted_count > 0:
    #         return result
    #     return None
    

    #TODO(improving): Try to configure the DB so that it has the 'title' parameter set as 'unique'
    @override
    def open_connection(self, DB_connection_url: str, DB_name: str):
        self.connection = MongoClient(DB_connection_url)
        self.database = self.connection[DB_name]


    @override
    def close_connection(self):
        self.connection.close()


    @override
    def get_engine_name(self) -> str:
        return "MongoDB"



#TODO(before merge): implement the class
class storage_PostgreSQL_operator(Storage_DB_operator_I):
    """
    Class to manage the PostgreSQL connection and operations for storage.
    """
    pass
