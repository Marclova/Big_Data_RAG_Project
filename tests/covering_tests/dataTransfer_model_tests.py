#TODO(MAYOR FIX): re-enable these tests after updating the DT_model according to the latest version of the project
#                   (now we use RAG_DT_model and Storage_DT_model separately)

# import os
# import yaml
import unittest

# from src.models.data_models import DT_model

# class DataTransfer_model_tester(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         stream = open(os.path.join("tests", "covering_tests", "test_samples.yaml"), 'r', encoding="utf-8")
#         cls.samples = yaml.safe_load(stream)
#         stream.close()


#     def test_DT_model_initialization(self):
#         # url cannot be None
#         with self.assertRaises(ValueError):
#             DT_model(url=None, title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                      id=self.samples["file_id"], vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], 
#                      embedder_name=self.samples["mock_embedder"])
        
#         # text and embedder cannot be None if vector is provided
#         with self.assertRaises(ValueError):
#             DT_model(url=self.samples["file_url"], title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                      id=self.samples["file_id"], vector=self.samples["mock_vector"], text=None, embedder_name=self.samples["mock_embedder"])
#         with self.assertRaises(ValueError):
#             DT_model(url=self.samples["file_url"], title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                      id=self.samples["file_id"], vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], embedder_name=None)

#         # minimal valid initialization
#         model = DT_model(url=self.samples["file_url"], title=None, authors=None, 
#                          id=None, vector=None, text=None, embedder_name=None)
#         self.assertEqual(model.url, self.samples["file_url"])
#         self.assertEqual(model.title, "untitled")
#         self.assertEqual(model.authors, ["unknown"])
#         self.assertEqual(model.id, -1)
#         self.assertEqual(model.vector, list())
#         self.assertEqual(model.text, "")
#         self.assertEqual(model.embedder_name, "")

#         # full valid initialization
#         model = DT_model(url=self.samples["file_url"], title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                          id=self.samples["file_id"], vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], 
#                          embedder_name=self.samples["mock_embedder"])
#         self.assertEqual(model.url, self.samples["file_url"])
#         self.assertEqual(model.title, self.samples["file_name"])
#         self.assertEqual(model.authors, self.samples["file_authors"])
#         self.assertEqual(model.id, self.samples["file_id"])
#         self.assertEqual(model.vector, self.samples["mock_vector"])
#         self.assertEqual(model.text, self.samples["text_to_cluster"])
#         self.assertEqual(model.embedder_name, self.samples["mock_embedder"])


#     def test_update_vector(self):
#         model = DT_model(url=self.samples["file_url"], title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                          id=self.samples["file_id"], vector=None, text=None, embedder_name=None)
        
#         # vector cannot be None or empty
#         with self.assertRaises(ValueError):
#             model.update_vector(vector=None, text=self.samples["text_to_cluster"], embedder_name=self.samples["mock_embedder"])
#         with self.assertRaises(ValueError):
#             model.update_vector(vector=list(), text=self.samples["text_to_cluster"], embedder_name=self.samples["mock_embedder"])
        
#         # text and embedder cannot be None
#         with self.assertRaises(ValueError):
#             model.update_vector(vector=self.samples["mock_vector"], text=None, embedder_name=self.samples["mock_embedder"])
#         with self.assertRaises(ValueError):
#             model.update_vector(vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], embedder_name=None)

#         # check for absence of (text=None ^ vector=None ^ embedder=None) tolerance
#         # this tolerance is allowed only during initialization
#         with self.assertRaises(ValueError):
#             model.update_vector(vector=None, text=None, embedder_name=None)
        
#         # valid update
#         model = DT_model(url=self.samples["file_url"], title=None, authors=None, 
#                          id=None, vector=None, text=None, embedder_name=None)
#         model.update_vector(vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], 
#                             embedder_name=self.samples["mock_embedder"])
#         self.assertEqual(model.vector, self.samples["mock_vector"])
#         self.assertEqual(model.text, self.samples["text_to_cluster"])
#         self.assertEqual(model.embedder_name, self.samples["mock_embedder"])


#     def test_generate_JSON_data(self):
#         model = DT_model(url=self.samples["file_url"], title=self.samples["file_name"], authors=self.samples["file_authors"], 
#                          id=self.samples["file_id"], vector=self.samples["mock_vector"], text=self.samples["text_to_cluster"], 
#                          embedder_name=self.samples["mock_embedder"])
#         json_data = model.generate_JSON_data()
#         self.assertEqual(json_data["id"], self.samples["file_id"])
#         self.assertEqual(json_data["vector"], self.samples["mock_vector"])
#         self.assertEqual(json_data["text"], self.samples["text_to_cluster"])
#         self.assertEqual(json_data["metadata"]["title"], self.samples["file_name"])
#         self.assertEqual(json_data["metadata"]["authors"], self.samples["file_authors"])
#         self.assertEqual(json_data["metadata"]["url"], self.samples["file_url"])

if __name__ == '__main__':
    unittest.main()