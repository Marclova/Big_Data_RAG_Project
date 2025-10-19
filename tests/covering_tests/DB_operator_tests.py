import os
import yaml
import unittest
from pymongo import results
from services.storage_DB_operator import MongoDB_manager

class DB_operator_tester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        stream = open(os.path.join("tests", "covering_tests", "test_samples.yaml"), 'r', encoding="utf-8")
        cls.samples = yaml.safe_load(stream)
        stream.close()

    def test_DB_interactions(self):
        connection_url = self.samples["test_collection_url"]
        collection_name = self.samples["test_collection_name"]
        DB_operator = MongoDB_manager(connection_url, self.samples["test_db_name"])

        record_to_insert: dict[str,any] = self.samples["record_to_insert"]

        # clean the collection before testing
        if DB_operator.get_all_records(collection_name) != []:
            DB_operator.database[collection_name].delete_many({})

        # test insert, get all and get
        self.assertIsInstance(DB_operator.insert_record_using_JSON(collection_name, record_to_insert), results.InsertOneResult)
        self.assertEqual(DB_operator.get_all_records(collection_name), [record_to_insert])
        self.assertEqual(DB_operator.get_record_using_title(collection_name, record_to_insert["title"]), record_to_insert)
        self.assertEqual(DB_operator.insert_record_using_JSON(collection_name, record_to_insert), None)
        # test update
        with self.assertRaises(ValueError):
            DB_operator.update_record_using_JSON(collection_name, {"pages": record_to_insert["pages"]*2})
        self.assertIsInstance(DB_operator.update_record_using_JSON(collection_name, 
                                                                   {"title": record_to_insert["title"], 
                                                                    "pages": record_to_insert["pages"]*2}), 
                                                                    results.UpdateResult)
        self.assertEqual(DB_operator.get_record_using_title(collection_name, record_to_insert["title"])["pages"], 
                         record_to_insert["pages"]*2)
        # test delete
        self.assertIsInstance(DB_operator.remove_record_using_title(collection_name, record_to_insert["title"]), results.DeleteResult)
        self.assertEqual(DB_operator.get_all_records(collection_name), [])
        self.assertEqual(DB_operator.get_record_using_title(collection_name, record_to_insert["title"]), None)
        self.assertEqual(DB_operator.remove_record_using_title(collection_name, record_to_insert["title"]), None)

if __name__ == "__main__":
    unittest.main()