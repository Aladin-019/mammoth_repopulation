import unittest
from unittest.mock import patch
from app.models.climate_drivers.TemperatureDriver import TemperatureDriver
import numpy as np

class TestTemperatureDriver(unittest.TestCase):
    def setUp(self):
        self.mock_temp_data = {
            "Saskatoon": {
                0: (-10.0, 2.0),  # Day 1
                1: (-12.0, 1.5),  # Day 2
                2: (-15.0, 3.0)   # Day 3
            }
        }
        self.climate_driver = TemperatureDriver(self.mock_temp_data)

    # Test the constructor
    @patch("numpy.random.normal", return_value=99.0)
    def test_generate_daily_temp_no_offset(self, mock_normal):
        result = self.climate_driver.generate_daily_temp("Saskatoon", 0)
        self.assertEqual(result, 99.0)
        mock_normal.assert_called_once_with(-10.0, 2.0)

    # Test with biome offset
    @patch("numpy.random.normal", return_value=88.0)
    def test_generate_daily_temp_with_offset(self, mock_normal):
        result = self.climate_driver.generate_daily_temp("Saskatoon", 2, biome_offset=2.0)
        self.assertEqual(result, 88.0)
        mock_normal.assert_called_once_with(-13.0, 3.0)  # -15 + 2 offset

if __name__ == "__main__":
    unittest.main()