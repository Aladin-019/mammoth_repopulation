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
        mock_normal.assert_called_once_with(-10.0, np.sqrt(2.0))

    # Test with biome offset
    @patch("numpy.random.normal", return_value=88.0)
    def test_generate_daily_temp_with_offset(self, mock_normal):
        result = self.climate_driver.generate_daily_temp("Saskatoon", 2, offset=2.0)
        self.assertEqual(result, 88.0)
        mock_normal.assert_called_once_with(-13.0, np.sqrt(3.0))  # -15 + 2 offset

    def test_missing_location(self):
        """Test behavior when location is not in temperature data."""
        result = self.climate_driver.generate_daily_temp("UnknownPlace", 0)
        self.assertIsNone(result)

    def test_day_out_of_range(self):
        """Test behavior when day index is out of range for existing location."""
        result = self.climate_driver.generate_daily_temp("Saskatoon", 100)
        self.assertIsNone(result)

    def test_temp_data_is_none(self):
        """Test when the temperature data tuple for a day is None."""
        broken_data = {
            "Saskatoon": {
                0: None
            }
        }
        climate_driver = TemperatureDriver(broken_data)
        result = climate_driver.generate_daily_temp("Saskatoon", 0)
        self.assertIsNone(result)

    def test_temp_data_contains_none_values(self):
        """Test when mean or variance in the temperature data tuple is None."""
        broken_data = {
            "Saskatoon": {
                0: (None, 0.2),
                1: (2.5, None),
                2: (None, None)
            }
        }
        climate_driver = TemperatureDriver(broken_data)
        self.assertIsNone(climate_driver.generate_daily_temp("Saskatoon", 0))
        self.assertIsNone(climate_driver.generate_daily_temp("Saskatoon", 1))
        self.assertIsNone(climate_driver.generate_daily_temp("Saskatoon", 2))

    def test_variance_negative(self):
        """Test behavior when variance is negative."""
        broken_data = {
            "Saskatoon": {
                0: (2.5, -0.1)
            }
        }
        climate_driver = TemperatureDriver(broken_data)
        result = climate_driver.generate_daily_temp("Saskatoon", 0)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()