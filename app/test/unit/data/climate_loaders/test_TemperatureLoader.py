import unittest
import pandas as pd
from io import StringIO
from app.data.climate_loaders.TemperatureLoader import TemperatureLoader

class TestTemperatureLoader(unittest.TestCase):
    def setUp(self):
        # Simulated CSV content
        self.mock_csv = StringIO(
        "date,mean_temp,temp_var\n"
        "2024-01-01,-20.5,1.2\n"
        "2024-01-02,-25.0,1.1\n"
        "2024-01-03,-19.8,1.3\n"
        )
        # Make mock csv called "mock_temp.csv"
        with open("mock_temp.csv", "w") as f:
            f.write(self.mock_csv.getvalue())

    def tearDown(self):
        import os
        os.remove("mock_temp.csv")

    # Test that the TemperatureLoader initializes correctly and
    # data structure is as expected
    def test_temp_data_structure(self):
        temp_loader = TemperatureLoader("mock_temp.csv", "Saskatoon")
        data = temp_loader.get_temp_data()

        self.assertIn("Saskatoon", data)
        self.assertEqual(len(data["Saskatoon"]), 3)
        self.assertIn(0, data["Saskatoon"]) 
        self.assertIsInstance(data["Saskatoon"][1], tuple)
        self.assertEqual(data["Saskatoon"][1][0], -25.0)

    # Test that the mean and variance are floats
    def test_values_are_floats(self):
        temp_loader = TemperatureLoader("mock_temp.csv", "Saskatoon")
        for mean, var in temp_loader.get_temp_data()["Saskatoon"].values():
            self.assertIsInstance(mean, float)
            self.assertIsInstance(var, float)

    # Test that the day numbers are correct
    def test_day_number_indexing(self):
        temp_loader = TemperatureLoader("mock_temp.csv", "Saskatoon")
        
        days = list(temp_loader.get_temp_data()["Saskatoon"].keys())
        self.assertEqual(days, [0, 1, 2])  # Jan 1–3 should be day 0–2


if __name__ == "__main__":
    unittest.main()
