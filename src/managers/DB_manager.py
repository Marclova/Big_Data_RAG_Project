from typing import cast
from src.models.DB_config_model import DB_config
from src.models.interfaces.data_model_interface import DTModel_I
from src.models.storage_data_model import Storage_DTModel
from src.models.RAG_data_model import RAG_DTModel
from src.services.db_services.interfaces.DB_operator_interfaces import DB_operator_I, Storage_DB_operator_I, RAG_DB_operator_I
from src.services.db_services.db_operator_factory import initialize_storage_db_operator, initialize_RAG_db_operator



STORAGE = "storage"
RAG = "RAG"



class DB_manager:
    """
    Generalized DB manager to handle DB operations.
    The db connections are supposed to be opened and never closed until the end of the execution.
    An instance of this class is supposed to be related to just one storage DB and one RAG DB. 
        Multiple collections/tables/indexes management is supported though.
    """

    def __init__(self, storage_db_config: DB_config, RAG_db_config: DB_config,
                 handled_storage_collections: list[str], handled_RAG_collections: list[str]) -> None:
        """
        Parameters:
            storage_db_config (DB_config): The configuration to use to initialize the storage DB operator.
            RAG_db_config (DB_config): The configuration to use to initialize the RAG DB operator.
            handled_storage_collections (list[str]): The list of names of the collections/tables in the storage DB that this manager will handle.
            handled_RAG_collections_ (list[str]): The list of names of the collections/tables/indexes in the RAG DB that this manager will handle.
        """
        self.storage_db_operator: Storage_DB_operator_I = initialize_storage_db_operator(storage_db_config)
        self.RAG_db_operator: RAG_DB_operator_I = initialize_RAG_db_operator(RAG_db_config)
        self.handled_storage_collections: list[str] = handled_storage_collections
        self.handled_RAG_collections: list[str] = handled_RAG_collections

        if handled_storage_collections is None or len(handled_storage_collections) == 0:
            raise ValueError("ERROR: At least one storage collection/table must be specified to be handled by the DB manager.")
        if handled_RAG_collections is None or len(handled_RAG_collections) == 0:
            raise ValueError("ERROR: At least one RAG collection/table/index must be specified to be handled by the DB manager.")
        
        if not self.storage_db_operator.check_collectionList_existence(handled_storage_collections):
            raise ValueError("ERROR: One or more specified storage collections/tables do not exist in the target DB.")
        if not self.RAG_db_operator.check_collectionList_existence(handled_RAG_collections):
            raise ValueError("ERROR: One or more specified RAG collections/tables/indexes do not exist in the target DB.")

    #region General DB methods

    # def insert_new_records_into_collections(self, dataModel_list: list[DTModel_I], 
    #                                                target_collection_list: list[str]) -> bool:
    #     """
    #     Method to insert multiple new records into multiple given storage or RAG collections.
    #     Parameters:
    #         target_collection_name (str): The name of the existing DB collection where to insert the records into.
    #         dataModel_list (list[DTModel_I]): The list of papers to insert.
    #     Returns:
    #         bool: the overall operation outcome.
    #     """
    #     if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, None):
    #         return False
        
    #     used_DB_engine: DB_operator_I = self._get_DB_engine_handling_collection(target_collection_list[0])
    #     print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.")

    #     output_flag: bool = True
    #     total_log_counter: int = 0
    #     single_collection_log_counter: int = 0

    #     #TODO(parallelization): make this operation parallel for each collection
    #     for target_collection_name in target_collection_list:
    #         single_collection_log_counter = 0

    #         for dataModel in dataModel_list:

    #             if used_DB_engine.insert_record(target_collection_name, dataModel): #logs for single record insertion are handled in the operator
    #                 single_collection_log_counter += 1
    #                 total_log_counter += 1
    #             else:
    #                 output_flag = False

    #         print(f"INFO: {single_collection_log_counter}/{dataModel_list.__len__()} "
    #               f"papers have been inserted into the storage collection '{target_collection_name}'")
    #     print(f"INFO: Overall, {total_log_counter}/{dataModel_list.__len__()*target_collection_list.__len__()} "
    #           f"papers have been inserted into the target collections.")
    #     return output_flag
    

    # def update_existing_papers_in_storage_collections(self, dataModel_list: list[DTModel_I], 
    #                                                   target_collection_list: list[str]) -> bool:
    #     """
    #     Method to update multiple existing papers in multiple given storage or RAG collections.
    #     Parameters:
    #         target_collection_name (str): The name of the existing DB collection where to update the records into.
    #         dataModel_list (list[DTModel_I]): The list of papers to update.
    #     Returns:
    #         bool: the overall operation outcome.
    #     """
    #     if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, None):
    #         return False
        
    #     used_DB_engine: DB_operator_I = self._get_DB_engine_handling_collection(target_collection_list[0])
    #     print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.")

    #     output_flag: bool = True
    #     total_log_counter: int = 0
    #     single_collection_log_counter: int = 0

    #     #TODO(parallelization): make this operation parallel for each collection
    #     for target_collection_name in target_collection_list:
    #         single_collection_log_counter = 0

    #         for dataModel in dataModel_list:

    #             if used_DB_engine.update_record(target_collection_name, dataModel): #logs for single record insertion are handled in the operator
    #                 single_collection_log_counter += 1
    #                 total_log_counter += 1
    #             else:
    #                 output_flag = False

    #         print(f"INFO: {single_collection_log_counter}/{dataModel_list.__len__()} "
    #               f"papers have been inserted into the storage collection '{target_collection_name}'")
    #     print(f"INFO: Overall, {total_log_counter}/{dataModel_list.__len__()*target_collection_list.__len__()} "
    #           f"papers have been inserted into the target collections.")
    #     return output_flag


    def insert_new_records_into_collections(self, dataModel_list: list[DTModel_I], 
                                                   target_collection_list: list[str]) -> bool:
        """
        Method to insert multiple new records into multiple given storage or RAG collections.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to insert the records into.
            dataModel_list (list[DTModel_I]): The list of papers to insert.
        Returns:
            bool: the overall operation outcome.
        """
        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, None):
            return False
        
        used_DB_engine: DB_operator_I = self._get_DB_engine_handling_collection(target_collection_list[0])
        print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.") #TODO(polishing): consider another logging method
        
        return self._apply_function_on_collections(used_DB_engine.insert_record, target_collection_list, 
                                                   dataModelList_input_type=dataModel_list, 
                                                  operation_name="inserted")


    def update_existing_papers_in_storage_collections(self, dataModel_list: list[DTModel_I], 
                                                  target_collection_list: list[str]) -> bool:
        """
        Method to update multiple existing papers in multiple given storage or RAG collections.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to update the records into.
            dataModel_list (list[DTModel_I]): The list of papers to update.
        Returns:
            bool: the overall operation outcome.
        """
        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, None):
            return False
        
        used_DB_engine: DB_operator_I = self._get_DB_engine_handling_collection(target_collection_list[0])
        print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.") #TODO(polishing): consider another logging method
        
        return self._apply_function_on_collections(used_DB_engine.update_record, target_collection_list, 
                                                   dataModelList_input_type=dataModel_list, 
                                                  operation_name="updated")
            
    #endregion General DB methods
    
    #region Storage DB methods

    def get_one_paper_from_one_storage_collection_using_title(self, target_collection_name: str, title_to_get: str) -> Storage_DTModel:
        """
        Method to retrieve one paper from a given storage collection using its title.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to retrieve the record from.
            title_to_find (str): The title of the paper to retrieve.
        Returns:
            DTModel_I: the retrieved paper model. None if not found.
        """
        return self.storage_db_operator.get_record_using_title(target_collection_name, title_to_get)
        

    def get_all_papers_from_storage_collections(self, target_collection_list: list[str]=None) -> dict[str, list[Storage_DTModel]]:
        """
        Method to retrieve all papers from multiple given storage collections.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to retrieve the records from.
            target_collection_list (list[str]): The list of names of the existing DB collections where to retrieve the records from.
        Returns:
            dict[str, list[DTModel_I]]: a dictionary mapping each collection name to the list of retrieved papers.
        """
        if target_collection_list is None:
            target_collection_list = self.handled_storage_collections
        
        output_dict: dict[str, list[Storage_DTModel]] = dict()

        for target_collection_name in target_collection_list:
            model_list = self.storage_db_operator.get_all_records(target_collection_name)
            
            output_dict.update({target_collection_name: model_list})
        
        return output_dict


    def remove_one_paper_from_storage_collections_using_title(self, title_to_remove: str, 
                                                              target_collection_list: list[str]) -> bool:
        """
        Method to remove a paper from multiple given storage collections using its title.
        Parameters:
            title (str): The title of the papers to remove.
            target_collection_list (list[str]): The list of names of the existing DB collections where to remove the records from.
        """
        # if target_collection_list is None:
        #     target_collection_list = self.handled_storage_collections
        # output_flag = True
        # counter = 0
        #TODO(parallelization): make this operation parallel for each collection
        # for target_collection_name in target_collection_list:
        #     remove_flag = self.storage_db_operator.remove_record_using_title(target_collection_name, title_to_remove) #logs for single record removal are handled in the operator
            
        #     if remove_flag:
        #         counter += 1
        #     output_flag = output_flag and remove_flag

        # print(f"INFO: {counter}/{target_collection_list.__len__()} papers titled '{title_to_remove}' have been removed from the storage collections")
        # return output_flag
    
        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, STORAGE):
            return False
        
        used_DB_engine: Storage_DB_operator_I = cast(Storage_DB_operator_I, 
                                                     self._get_DB_engine_handling_collection(target_collection_list[0]))

        print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.") #TODO(polishing): consider another logging method
        
        return self._apply_function_on_collections(used_DB_engine.remove_record_using_title, target_collection_list, 
                                                   string_input_type=title_to_remove, 
                                                  operation_name="removed")
    
    #endregion Storage DB methods

    #region RAG DB methods

    def get_one_record_from_RAG_one_collection_using_embedded_text(self, target_collection_name: str, 
                                                                   embedded_text_to_get: str) -> RAG_DTModel:
        """
        Method to get through exact match a record from a given RAG collection using its embedded text.
        Parameters:
            target_collection_name (str): The name of the existing DB collection where to retrieve the record from.
            embedded_text_to_find (str): The embedded text of the record to retrieve.
        Returns:
            RAG_DTModel: the retrieved record model. None if not found.
        """
        return self.RAG_db_operator.get_record_using_embedded_text(target_collection_name, embedded_text_to_get)
    

    def remove_one_record_from_RAG_collections_using_embedded_text(self, embedded_text_to_remove: str, 
                                                                    target_collection_list: list[str]) -> bool:
        """
        Method to remove a record from multiple given RAG collections using its embedded text.
        Parameters:
            embedded_text_to_remove (str): The embedded text of the record to remove.
            target_collection_list (list[str]): The list of names of the existing RAG collections where to remove the records from.
        Returns:
            bool: the overall operation outcome.
        """
        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, RAG):
            return False
        
        used_DB_engine: RAG_DB_operator_I = cast(RAG_DB_operator_I, 
                                                 self._get_DB_engine_handling_collection(target_collection_list[0]))
        print(f"INFO: Using DB engine '{used_DB_engine.get_engine_name()}' for the insertion operation.") #TODO(polishing): consider another logging method

        return self._apply_function_on_collections(used_DB_engine.remove_record_using_embedded_text, target_collection_list, 
                                                   string_input_type=embedded_text_to_remove, 
                                                   operation_name="removed")
    
    #retrieve_vectors_using_query
    def retrieve_vectors_from_RAG_collections_using_query(self, target_collection_list: list[str],
                                                          query_text: str, top_k: int) -> dict[str, list[RAG_DTModel]]:
        """
        Method to retrieve the top_k most similar vectors to the input query from multiple given RAG collections.
        Parameters:
            target_collection_list (list[str]): The list of names of the existing RAG collections where to retrieve the vectors from.
            query (str): The input query string to search for similar vectors.
            top_k (int): The number of most similar vectors to retrieve.
        Returns:
            dict[str, list[RAG_DTModel]]: a dictionary mapping each collection name to the list of retrieved vectors.
        """
        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, RAG):
            return dict()
        
        print(f"INFO: Using DB engine '{self.RAG_db_operator.get_engine_name()}' for the vector retrieval operation.") #TODO(polishing): consider another logging method
        output_dict: dict[str, list[RAG_DTModel]] = dict()

        for target_collection_name in target_collection_list:
            model_list = self.RAG_db_operator.retrieve_vectors_using_query(target_collection_name, query_text, top_k)
            
            output_dict.update({target_collection_name: model_list})
        
        return output_dict

    #endregion RAG DB methods

    #region generalized private methods

    def _apply_function_on_collections(self, operation_to_apply: callable, target_collection_list: list[str], 
                                       dataModelList_input_type: list[DTModel_I] = None, string_input_type: str = None, 
                                       operation_name: str="handled") -> bool:
        """
        Generalized method to apply a given function on multiple collections.
        The meant functions are 'update', 'insert' and 'delete'.
        Parameters:
            func_to_apply (callable): The function to apply on the given collections.
            target_collection_list (list[str]): The list of given collections where to apply the function.
            dataModelList_input_type (list[DTModel_I]): The list of data models to use as input for the function.
            string_input_type (str): The string input to use for the function.
            operation_name (str): The name of the operation to perform (for logging purposes), 
                                    to insert in the simple past tense.
        Returns:
            bool: the overall operation outcome.
        """
        if (dataModelList_input_type is None == string_input_type is None):
            raise ValueError("Either 'dataModelList_input_type' or 'string_input_type' must be provided, but not both.")

        if not self._check_collection_list_handling_and_DB_Engine_Usage_integrity(target_collection_list, None):
            return False

        output_flag: bool = True
        total_log_counter: int = 0
        single_collection_log_counter: int = 0

        #TODO(parallelization): make this operation parallel for each collection
        for target_collection_name in target_collection_list:
            single_collection_log_counter = 0

            if dataModelList_input_type is not None:
                for dataModel_input in dataModelList_input_type:

                    if operation_to_apply(target_collection_name, dataModel_input): #logs for single record insertion are handled in the operator
                        single_collection_log_counter += 1
                        total_log_counter += 1
                    else:
                        output_flag = False
            else:
                if operation_to_apply(target_collection_name, string_input_type): #logs for single record insertion are handled in the operator
                    single_collection_log_counter += 1
                    total_log_counter += 1
                else:
                    output_flag = False
            print(f"INFO: {single_collection_log_counter}/{dataModelList_input_type.__len__()} "
                    f"papers have been {operation_name} into the storage collection '{target_collection_name}'") #TODO(polishing): consider another logging method            
        print(f"INFO: Overall, {total_log_counter}/{dataModelList_input_type.__len__()*target_collection_list.__len__()} "
              f"papers have been {operation_name} into the target collections.") #TODO(polishing): consider another logging method
        return output_flag

    #endregion generalized private methods

    #region Integrity check private methods

    def _get_DB_engine_handling_collection(self, target_collection_name: str) -> DB_operator_I:
        """
        Method to determine which DB engine (storage or RAG) is handling the given collection.
        It returns the appropriate DB operator instance that handles the given collection.
        Parameters:
            target_collection_name (str): The name of the collection to check.
        Returns:
            DB_operator_I: The DB operator instance that handles the given collection. None if not found. 
                            None if no matching engine is found.
        """
        if target_collection_name in self.handled_storage_collections:
            return self.storage_db_operator
        elif target_collection_name in self.handled_RAG_collections:
            return self.RAG_db_operator
        else:
            return None
        
    
    def _check_collection_list_handling_and_DB_Engine_Usage_integrity(self, target_collection_list: list[str],
                                                                      the_only_allowed_usage: str=None) -> bool:
        """
        Method to check if the given collection list is handled by this instance of the DB manager
        and if all collections in the list are handled by the same DB engine (storage or RAG).
        Parameters:
            target_collection_list (list[str]): The list of names of the collections to check.
            not_allowed_usage (str): If provided, it can be either "storage" or "RAG" to indicate
                                     that only collections of that usage are allowed in the list.
        Returns:
            bool: True if all the collections in the list are handled by this instance of the DB manager
                  and all of them are handled by the same DB engine. False otherwise.    
        """
        if target_collection_list is None or target_collection_list.__len__() == 0:
            print("ERROR: No target collection specified for paper insertion.")
            return False
        if not self._check_collection_list_handling_integrity(target_collection_list):
            print("ERROR: The provided target collection list contains collections not handled by this instance of the DB manager.")
            return False
        if not self._check_collection_list_DB_Engine_Usage_integrity(target_collection_list, the_only_allowed_usage):
            print("ERROR: The provided target collection list must not contain collections handled by different DB engines. "
                  "Only one DB engine shall be used for each method call.")
            return False
        return True


    def _check_collection_list_handling_integrity(self, target_collection_list: list[str]) -> bool:
        """
        Method to check if all the collections in the given list are handled by this instance of the DB manager.
        Parameters:
            target_collection_list (list[str]): The list of names of the collections to check.
        Returns:
            bool: True if all the collections in the list are handled by this instance of the DB manager. False otherwise.
        """
        for target_collection_name in target_collection_list:
            if (target_collection_name not in self.handled_storage_collections and
                target_collection_name not in self.handled_RAG_collections):
                return False
        return True


    def _check_collection_list_DB_Engine_Usage_integrity(self, target_collection_list: list[str], 
                                                         the_only_allowed_usage: str=None) -> bool:
        """
        Method to check if all the collections in the given list are handled by the same DB engine (storage or RAG).
        Parameters:
            target_collection_list (list[str]): The list of names of the collections to check.
        Returns:
            bool: True if all the collections in the list are handled by the same DB engine. False otherwise.
        """
        valid_usage: str = None
        if target_collection_list[0] in self.handled_storage_collections:
            valid_usage = STORAGE
        elif target_collection_list[0] in self.handled_RAG_collections:
            valid_usage = RAG
        else:
            return False #the first collection is not handled by this manager
        
        if the_only_allowed_usage is not None and valid_usage != the_only_allowed_usage:
            return False

        for i in range(1, target_collection_list.__len__()):
            target_collection_name = target_collection_list[i]
            if valid_usage == STORAGE and target_collection_name in self.handled_RAG_collections:
                return False
            if valid_usage == RAG and target_collection_name in self.handled_storage_collections:
                return False
        return True

    #endregion Integrity check private methods
