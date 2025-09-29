import os
import yaml
import unittest
import src.services.raw_data_operator as RD_operator


class Raw_data_operator_tester(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        stream = open(os.path.join("tests", "covering_tests", "test_samples.yaml"), 'r', encoding="utf-8")
        cls.samples = yaml.safe_load(stream)
        stream.close()


    def test_normalize_extension(self):
        self.assertEqual(RD_operator.normalize_extension("pdf"), ".pdf")
        self.assertEqual(RD_operator.normalize_extension(".pdf"), ".pdf")


    def test_cluster_text(self):
        text_to_cluster = self.samples["text_to_cluster"]
        clustered_text = self.samples["clustered_text"]
        
        self.assertEqual(RD_operator.cluster_text(text_to_cluster), clustered_text)


    # The decision/condition coverage criteria has been applied for this test method
    def test_increase_09az_id_with_carry(self):
        with self.assertRaises(ValueError):
            RD_operator.increase_09az_id_with_carry(None)
        with self.assertRaises(ValueError):
            RD_operator.increase_09az_id_with_carry("")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("5z"), "60")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("5z|"), "600")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("59"), "5a")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("5<"), "5a")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("50"), "51")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("50"), "51")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("5+"), "50")
        self.assertEqual(RD_operator.increase_09az_id_with_carry("55"), "56")


if __name__ == "__main__":
    unittest.main()