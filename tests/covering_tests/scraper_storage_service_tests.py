import os
import yaml
import unittest
import src.services.scraper_storage_service as webScraper

class Scraper_storage_service_tester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        stream = open(os.path.join("tests", "covering_tests", "test_samples.yaml"), 'r', encoding="utf-8")
        cls.samples = yaml.safe_load(stream)
        stream.close()


    def test_get_file_content(self):
        file_URL = self.samples["file_url"]
        file_extension = self.samples["file_extension"]
        folder_path = os.path.join(*self.samples["folder_path"])

        file_content_sample = self.samples["text_to_cluster"]
        file_path_sample = os.path.join(folder_path, "test_file.pdf")

        #cleanup if file already exists from previous failed tests
        os.remove(file_path_sample) if os.path.exists(file_path_sample) else None

        #file creation
        self.assertFalse(os.path.exists(file_path_sample))
        self.assertEqual(webScraper.download_file(file_URL, file_extension, file_name="test_file", folder_path=folder_path),
                         file_path_sample)
        self.assertTrue(os.path.exists(file_path_sample))
        #file content check
        self.assertIn(file_content_sample, webScraper.get_file_content(file_path_sample))
        #file deletion
        self.assertEqual(webScraper.delete_file(file_path_sample), 1)
        self.assertEqual(webScraper.delete_file(file_path_sample), 0)
        self.assertFalse(os.path.exists(file_path_sample))

if __name__ == "__main__":
    unittest.main()