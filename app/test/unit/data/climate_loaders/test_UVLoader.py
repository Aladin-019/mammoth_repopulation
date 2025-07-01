import unittest
import pandas as pd
from io import StringIO
import os
import logging
from app.data.climate_loaders.UVLoader import UVLoader

class TestUVLoader(unittest.TestCase):

    def write_mock_csv(self, content: str, filename: str = "mock_uv.csv"):
        with open(filename, "w") as f:
            f.write(content)

    def tearDown(self):
        if os.path.exists("mock_uv.csv"):
            os.remove("mock_uv.csv")

    def test_uv_data_structure(self):
        csv_content = (
            "date,mean_uv,uv_var\n"
            "2024-01-01,2.5,0.2\n"
            "2024-01-02,3.0,0.1\n"
            "2024-01-03,2.8,0.3\n"
        )
        self.write_mock_csv(csv_content)
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        data = uv_loader.get_uv_data()

        self.assertIn("Saskatoon", data)
        self.assertEqual(len(data["Saskatoon"]), 3)
        self.assertIn(0, data["Saskatoon"]) 
        self.assertIsInstance(data["Saskatoon"][1], tuple)
        self.assertEqual(data["Saskatoon"][1][0], 3.0)

    def test_values_are_floats(self):
        self.write_mock_csv(
            "date,mean_uv,uv_var\n2024-01-01,2.5,0.2\n"
        )
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        mean, var = list(uv_loader.get_uv_data()["Saskatoon"].values())[0]
        self.assertIsInstance(mean, float)
        self.assertIsInstance(var, float)

    def test_day_number_indexing(self):
        self.write_mock_csv(
            "date,mean_uv,uv_var\n"
            "2024-01-01,2.5,0.2\n2024-01-02,3.0,0.1\n"
        )
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        days = list(uv_loader.get_uv_data()["Saskatoon"].keys())
        self.assertEqual(days, [0, 1])

    def test_skips_null_values(self):
        self.write_mock_csv(
            "date,mean_uv,uv_var\n"
            "2024-01-01,,0.2\n"
            "2024-01-02,3.0,\n"
        )
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        data = uv_loader.get_uv_data()["Saskatoon"]
        self.assertEqual(len(data), 0)  # both rows should be skipped

    def test_skips_negative_variance(self):
        self.write_mock_csv(
            "date,mean_uv,uv_var\n"
            "2024-01-01,2.5,-0.1\n"
        )
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        self.assertEqual(len(uv_loader.get_uv_data()["Saskatoon"]), 0)

    def test_missing_required_columns(self):
        self.write_mock_csv(
            "date,wrong_col,uv_var\n2024-01-01,2.5,0.2\n"
        )
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        self.assertEqual(uv_loader.get_uv_data(), {"Saskatoon": {}})

    def test_invalid_file(self):
        uv_loader = UVLoader("invalid.csv", "Someplace")
        self.assertEqual(uv_loader.get_uv_data(), {"Someplace": {}})


if __name__ == "__main__":
    unittest.main()
