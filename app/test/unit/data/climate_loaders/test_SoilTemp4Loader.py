import unittest
import os
from app.data.climate_loaders.SoilTemp4Loader import SoilTemp4Loader

class TestSoilTemp4Loader(unittest.TestCase):

    def write_mock_csv(self, content: str, filename: str = "mock_soil_temp4.csv"):
        with open(filename, "w") as f:
            f.write(content)

    def tearDown(self):
        if os.path.exists("mock_soil_temp4.csv"):
            os.remove("mock_soil_temp4.csv")

    def test_soil_temp4_data_structure(self):
        csv_content = (
            "Date,Mean_Temp_C,Variance_Temp_C\n"
            "2024-01-01,-20.5,1.2\n"
            "2024-01-02,-25.0,1.1\n"
            "2024-01-03,-19.8,1.3\n"
        )
        self.write_mock_csv(csv_content)
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        data = soil_temp4_loader.get_soil_temp4_data()

        self.assertIn("Saskatoon", data)
        self.assertEqual(len(data["Saskatoon"]), 3)
        self.assertIn(0, data["Saskatoon"]) 
        self.assertIsInstance(data["Saskatoon"][1], tuple)
        self.assertEqual(data["Saskatoon"][1][0], -25.0)

    def test_values_are_floats(self):
        self.write_mock_csv(
            "Date,Mean_Temp_C,Variance_Temp_C\n2024-01-01,-20.5,1.2\n"
        )
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        mean, var = list(soil_temp4_loader.get_soil_temp4_data()["Saskatoon"].values())[0]
        self.assertIsInstance(mean, float)
        self.assertIsInstance(var, float)

    def test_day_number_indexing(self):
        self.write_mock_csv(
            "Date,Mean_Temp_C,Variance_Temp_C\n"
            "2024-01-01,-20.5,1.2\n2024-01-02,-25.0,1.1\n"
        )
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        days = list(soil_temp4_loader.get_soil_temp4_data()["Saskatoon"].keys())
        self.assertEqual(days, [0, 1])

    def test_skips_null_values(self):
        self.write_mock_csv(
            "Date,Mean_Temp_C,Variance_Temp_C\n"
            "2024-01-01,,0.2\n"
            "2024-01-02,3.0,\n"
        )
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        data = soil_temp4_loader.get_soil_temp4_data()["Saskatoon"]
        self.assertEqual(len(data), 0)  # both rows should be skipped

    def test_skips_negative_variance(self):
        self.write_mock_csv(
            "Date,Mean_Temp_C,Variance_Temp_C\n"
            "2024-01-01,2.5,-0.1\n"
        )
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        self.assertEqual(len(soil_temp4_loader.get_soil_temp4_data()["Saskatoon"]), 0)

    def test_missing_required_columns(self):
        self.write_mock_csv(
            "Date,wrong_col,Variance_Temp_C\n2024-01-01,2.5,0.2\n"
        )
        soil_temp4_loader = SoilTemp4Loader("mock_soil_temp4.csv", "Saskatoon")
        self.assertEqual(soil_temp4_loader.get_soil_temp4_data(), {"Saskatoon": {}})

    def test_invalid_file(self):
        soil_temp4_loader = SoilTemp4Loader("invalid.csv", "Someplace")
        self.assertEqual(soil_temp4_loader.get_soil_temp4_data(), {"Someplace": {}})


if __name__ == "__main__":
    unittest.main()