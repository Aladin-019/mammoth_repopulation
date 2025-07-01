import unittest
from unittest.mock import patch
from app.models.climate_drivers.UVDriver import UVDriver
import numpy as np

class TestUVDriver(unittest.TestCase):
    def setUp(self):
        self.mock_uv_data = {
            "Saskatoon": {
                0: (2.5, 0.2),  # Day 1
                1: (3.0, 0.1),  # Day 2
                2: (2.8, 0.3)   # Day 3
            }
        }
        self.climate_driver = UVDriver(self.mock_uv_data)

    @patch("numpy.random.normal", return_value=99.0)
    def test_generate_daily_uv_no_offset(self, mock_normal):
        """Test UV generation without biome offset."""
        result = self.climate_driver.generate_daily_uv("Saskatoon", 0)
        self.assertEqual(result, 99.0)
        mock_normal.assert_called_once_with(2.5, np.sqrt(0.2))

    @patch("numpy.random.normal", return_value=88.0)
    def test_generate_daily_uv_with_offset(self, mock_normal):
        """Test UV generation with biome offset."""
        result = self.climate_driver.generate_daily_uv("Saskatoon", 2, biome_offset=2.0)
        self.assertEqual(result, 88.0)
        mock_normal.assert_called_once_with(2.8 + 2.0, np.sqrt(0.3))  # 2.8 + 2 offset

    def test_missing_location(self):
        """Test behavior when location is not in UV data."""
        result = self.climate_driver.generate_daily_uv("UnknownPlace", 0)
        self.assertIsNone(result)

    def test_day_out_of_range(self):
        """Test behavior when day index is out of range for existing location."""
        result = self.climate_driver.generate_daily_uv("Saskatoon", 100)
        self.assertIsNone(result)

    def test_uv_data_is_none(self):
        """Test when the UV data tuple for a day is None."""
        broken_data = {
            "Saskatoon": {
                0: None
            }
        }
        climate_driver = UVDriver(broken_data)
        result = climate_driver.generate_daily_uv("Saskatoon", 0)
        self.assertIsNone(result)

    def test_uv_data_contains_none_values(self):
        """Test when mean or variance in the UV data tuple is None."""
        broken_data = {
            "Saskatoon": {
                0: (None, 0.2),
                1: (2.5, None),
                2: (None, None)
            }
        }
        climate_driver = UVDriver(broken_data)
        self.assertIsNone(climate_driver.generate_daily_uv("Saskatoon", 0))
        self.assertIsNone(climate_driver.generate_daily_uv("Saskatoon", 1))
        self.assertIsNone(climate_driver.generate_daily_uv("Saskatoon", 2))

    def test_variance_negative(self):
        """Test behavior when variance is negative."""
        broken_data = {
            "Saskatoon": {
                0: (2.5, -0.1)
            }
        }
        climate_driver = UVDriver(broken_data)
        result = climate_driver.generate_daily_uv("Saskatoon", 0)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()