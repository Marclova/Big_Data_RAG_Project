from typing import override
from pymongo import MongoClient
from pymongo.database import Database
from pg import DB as PyGreSQLClient

from src.common.constants import Featured_storage_DB_engines_enum as storage_engines_enum

from src.services.db_services.interfaces.DB_operator_interfaces import Storage_DB_operator_I

from src.models.data_models import Storage_DTModel


"""
Service module to manage the connection and operations on a database meant to store raw data before embedding.
Embedding and storage of vectors are handled elsewhere.
Selected DBs are MongoDB and PostgreSQL
"""

#TODO(improvement): consider adding exception handling for DB connections and operations

class Storage_MongoDB_operator(Storage_DB_operator_I):
    """
    Class to manage the MongoDB connection and operations for storage.
    """
    def __init__(self, DB_connection_url: str, DB_name: str):
        if((DB_connection_url is None) or (DB_name is None)):
            raise ValueError("MongoDB connection URL and DB name must be provided.")

        self.connection: MongoClient
        self.database: Database

        self.open_connection(DB_connection_url, DB_name)


    @override
    def get_record_using_title(self, target_collection_name: str, title: str) -> dict[any]:
        if((target_collection_name is None) or (title is None)):
            raise ValueError("Target collection name and title must be provided.")
        if(self.check_collection_existence(target_collection_name) is False):
            raise ValueError(f"The target collection '{target_collection_name}' does not exist in the database.")

        return self.database[target_collection_name].find_one({"title": title})


    @override
    def get_all_records(self, input_collection_name: str) -> list[dict[any]]:
        if((input_collection_name is None) or (self.check_collection_existence(input_collection_name) is False)):
            raise ValueError("Input collection name must be provided and must exist in the database.")

        return list(self.database[input_collection_name].find())


    @override
    def insert_record(self, target_collection_name: str, data_model: Storage_DTModel) -> bool:
        if((target_collection_name is None) or (data_model is None)):
            raise ValueError("Target collection name and data model must be provided.")
        if(self.check_collection_existence(target_collection_name) is False):
            raise ValueError(f"The target collection '{target_collection_name}' does not exist in the database.")

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
        if((target_collection_name is None) or (data_model is None)):
            raise ValueError("Target collection name and data model must be provided.")
        if(self.check_collection_existence(target_collection_name) is False):
            raise ValueError(f"The target collection '{target_collection_name}' does not exist in the database.")
        
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
        
        
    @override
    def remove_record_using_title(self, target_collection_name: str, title: str) -> bool:
        if((target_collection_name is None) or (title is None)):
            raise ValueError("Target collection name and title must be provided.")
        if(self.check_collection_existence(target_collection_name) is False):
            raise ValueError(f"The target collection '{target_collection_name}' does not exist in the database.")

        # return (self.remove_records_using_manualFilter(target_collection_name, {"title": title}) is not None)
        return (self.database[target_collection_name].delete_one({"title": title}).deleted_count > 0)
    

    @override
    def check_collection_existence(self, collection_to_check: str) -> bool:
        if(collection_to_check is None):
            return False
        return (self.database.get_collection(collection_to_check) != None)


    @override
    def open_connection(self, DB_connection_url: str, DB_name: str) -> bool:
        if((DB_connection_url is None) or (DB_name is None)):
            raise ValueError("MongoDB connection URL and DB name must be provided.")

        self.connection = MongoClient(DB_connection_url)
        self.database = self.connection[DB_name]
        return True


    @override
    def close_connection(self):
        self.connection.close()
        self.database = None


    @override
    def get_engine_name(self) -> str:
        return storage_engines_enum.MONGODB



class storage_PyGreSQL_operator(Storage_DB_operator_I):
    """
    Class to manage the PostgreSQL connection and operations for storage.
    """
    def __init__(self, dbname: str, host: str, port: int, user: str, passwd: str):
        if((dbname is None) or (host is None) or (port is None) or (user is None) or (passwd is None)):
            raise ValueError("All PostgreSQL connection parameters must be provided.")
        self.database: PyGreSQLClient
        
        self.open_connection(dbname, host, port, user, passwd)


    @override
    def get_record_using_title(self, target_table_name: str, title: str) -> Storage_DTModel:
        if((target_table_name is None) or (title is None)):
            raise ValueError("Target table name and title must be provided.")

        query = f"SELECT * FROM {target_table_name} WHERE title = {title}"
        record = self.database.query(query).getresult()[0] #only one element is supposed to be retrieved

        return Storage_DTModel(url=record[0], title=record[1], pages=record[2], authors=record[3])


    @override
    def get_all_records(self, target_table_name: str) -> list[Storage_DTModel]:
        if(target_table_name is None):
            raise ValueError("Target table name must be provided.")
        
        query = f"SELECT * FROM {target_table_name}"

        DTModel_list: list[Storage_DTModel] = list()
        records_list = self.database.query(query).getresult()
        for record in records_list:
            DTModel_list.append(Storage_DTModel(url=record[0], title=record[1], pages=record[2], authors=record[3]))
        
        return DTModel_list

    @override
    def insert_record(self, target_table_name: str, data_model: Storage_DTModel) -> bool:
        if((target_table_name is None) or (data_model is None)):
            raise ValueError("Target table name and data model must be provided.")
        
        authors_list = self._generate_authors_string_for_query(data_model.authors)
        query = (f"INSERT INTO {target_table_name}"
                 f"VALUES('{data_model.url}', '{data_model.title}', '{data_model.pages}', '{authors_list}'")

        return (self.database.query(query) != None)

    
    @override
    def update_record(self, target_table_name: str, data_model: Storage_DTModel) -> bool:
        if((target_table_name is None) or (data_model is None)):
            raise ValueError("Target table name and data model must be provided.")

        authors_list = self._generate_authors_string_for_query(data_model.authors)
        query = (f"UPDATE {target_table_name} "
                 f"SET url = {data_model.url}, pages = {data_model.pages}, authors = {authors_list} "
                 f"WHERE title = {data_model.title}")
        
        return (self.database.query(query) != None)


    @override
    def remove_record_using_title(self, target_table_name: str, title: str) -> bool:
        if((target_table_name is None) or (title is None)):
            raise ValueError("Target table name and title must be provided.")

        query = f"DELETE FROM {target_table_name} WHERE title = {title}"
        return (self.database.query(query) != None)


    @override
    def check_collection_existence(self, collection_to_check: list[str]) -> bool:
        if(collection_to_check is None):
            return False
        return (collection_to_check in self.database.get_tables())


    @override
    def open_connection(self, dbname: str, host: str, port: int, user: str, passwd: str):
        if((dbname is None) or (host is None) or (port is None) or (user is None) or (passwd is None)):
            raise ValueError("All PostgreSQL connection parameters must be provided.")

        self.database = PyGreSQLClient(dbname, host, port, user, passwd)


    @override
    def close_connection(self):
        self.database.close()


    @override
    def get_engine_name(self) -> str:
        return storage_engines_enum.PYGRESQL


    def _generate_authors_string_for_query(authors: list[str]):
        """
        Generates the 'authors' substring of a PyGreSQL query to insert as a single array value.
        """
        authors_list = ""
        for author in authors:
            authors_list = f"\"{author}\", "
        authors_list = authors_list.removesuffix(", ")
        authors_list = "{" + authors_list + "}"

        return authors_list