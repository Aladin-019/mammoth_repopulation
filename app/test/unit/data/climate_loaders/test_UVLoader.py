import unittest
import pandas as pd
from io import StringIO
from app.data.climate_loaders.UVLoader import UVLoader

class TestUVLoader(unittest.TestCase):
    def setUp(self):
        # Simulated CSV content
        self.mock_csv = StringIO(
        "date,mean_uv,uv_var\n"
        "2024-01-01,2.5,0.2\n"
        "2024-01-02,3.0,0.1\n"
        "2024-01-03,2.8,0.3\n"
        )
        # Make mock csv
        with open("mock_uv.csv", "w") as f:
            f.write(self.mock_csv.getvalue())

    def tearDown(self):
        import os
        os.remove("mock_uv.csv")

    # Test that the UVLoader initializes correctly and
    # data structure is as expected
    def test_uv_data_structure(self):
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        data = uv_loader.get_uv_data()

        self.assertIn("Saskatoon", data)
        self.assertEqual(len(data["Saskatoon"]), 3)
        self.assertIn(0, data["Saskatoon"]) 
        self.assertIsInstance(data["Saskatoon"][1], tuple)
        self.assertEqual(data["Saskatoon"][1][0], 3.0)

    # Test that the mean and variance are floats
    def test_values_are_floats(self):
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")
        for mean, var in uv_loader.get_uv_data()["Saskatoon"].values():
            self.assertIsInstance(mean, float)
            self.assertIsInstance(var, float)

    # Test that the day numbers are correct
    def test_day_number_indexing(self):
        uv_loader = UVLoader("mock_uv.csv", "Saskatoon")

        days = list(uv_loader.get_uv_data()["Saskatoon"].keys())
        self.assertEqual(days, [0, 1, 2])  # Jan 1–3 should be day 0–2


if __name__ == "__main__":
    unittest.main()
