import unittest
import os
from app.data.climate_loaders.SSRDLoader import SSRDLoader

class TestSRDLoader(unittest.TestCase):

    def write_mock_csv(self, content: str, filename: str = "mock_srd.csv"):
        with open(filename, "w") as f:
            f.write(content)

    def tearDown(self):
        if os.path.exists("mock_srd.csv"):
            os.remove("mock_srd.csv")

    def test_srd_data_structure(self):
        csv_content = (
            "date,mean_srd,srd_var\n"
            "2024-01-01,-20.5,1.2\n"
            "2024-01-02,-25.0,1.1\n"
            "2024-01-03,-19.8,1.3\n"
        )
        self.write_mock_csv(csv_content)
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        data = srd_loader.get_srd_data()

        self.assertIn("Saskatoon", data)
        self.assertEqual(len(data["Saskatoon"]), 3)
        self.assertIn(0, data["Saskatoon"]) 
        self.assertIsInstance(data["Saskatoon"][1], tuple)
        self.assertEqual(data["Saskatoon"][1][0], -25.0)

    def test_values_are_floats(self):
        self.write_mock_csv(
            "date,mean_srd,srd_var\n2024-01-01,-20.5,1.2\n"
        )
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        mean, var = list(srd_loader.get_srd_data()["Saskatoon"].values())[0]
        self.assertIsInstance(mean, float)
        self.assertIsInstance(var, float)

    def test_day_number_indexing(self):
        self.write_mock_csv(
            "date,mean_srd,srd_var\n"
            "2024-01-01,-20.5,1.2\n2024-01-02,-25.0,1.1\n"
        )
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        days = list(srd_loader.get_srd_data()["Saskatoon"].keys())
        self.assertEqual(days, [0, 1])

    def test_skips_null_values(self):
        self.write_mock_csv(
            "date,mean_srd,srd_var\n"
            "2024-01-01,,0.2\n"
            "2024-01-02,3.0,\n"
        )
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        data = srd_loader.get_srd_data()["Saskatoon"]
        self.assertEqual(len(data), 0)  # both rows should be skipped

    def test_skips_negative_variance(self):
        self.write_mock_csv(
            "date,mean_srd,srd_var\n"
            "2024-01-01,2.5,-0.1\n"
        )
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        self.assertEqual(len(srd_loader.get_srd_data()["Saskatoon"]), 0)

    def test_missing_required_columns(self):
        self.write_mock_csv(
            "date,wrong_col,srd_var\n2024-01-01,2.5,0.2\n"
        )
        srd_loader = SSRDLoader("mock_srd.csv", "Saskatoon")
        self.assertEqual(srd_loader.get_srd_data(), {"Saskatoon": {}})

    def test_invalid_file(self):
        srd_loader = SSRDLoader("invalid.csv", "Someplace")
        self.assertEqual(srd_loader.get_srd_data(), {"Someplace": {}})


if __name__ == "__main__":
    unittest.main()