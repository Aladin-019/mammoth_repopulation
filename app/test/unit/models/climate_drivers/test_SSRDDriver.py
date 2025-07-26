import unittest
from unittest.mock import patch
from app.models.climate_drivers.SSRDDriver import SSRDDriver
import numpy as np

class TestRainfallDriver(unittest.TestCase):
    def setUp(self):
        self.mock_srd_data = {
            "Saskatoon": {
                0: (5.0, 1.0),  # Day 1
                1: (10.0, 2.0),  # Day 2
                2: (15.0, 3.0)   # Day 3
            }
        }
        self.climate_driver = SSRDDriver(self.mock_srd_data)

    # Test the constructor
    @patch("numpy.random.normal", return_value=99.0)
    def test_generate_daily_srd_no_offset(self, mock_normal):
        result = self.climate_driver.generate_daily_srd("Saskatoon", 0)
        self.assertEqual(result, 99.0)
        mock_normal.assert_called_once_with(5.0, np.sqrt(1.0))

    # Test with biome offset
    @patch("numpy.random.normal", return_value=88.0)
    def test_generate_daily_srd_with_offset(self, mock_normal):
        result = self.climate_driver.generate_daily_srd("Saskatoon", 2, offset=2.0)
        self.assertEqual(result, 88.0)
        mock_normal.assert_called_once_with(17.0, np.sqrt(3.0))  # 15 + 2 offset

    def test_missing_location(self):
        """Test behavior when location is not in srd data."""
        result = self.climate_driver.generate_daily_srd("UnknownPlace", 0)
        self.assertIsNone(result)

    def test_day_out_of_range(self):
        """Test behavior when day index is out of range for existing location."""
        result = self.climate_driver.generate_daily_srd("Saskatoon", 100)
        self.assertIsNone(result)

    def test_srd_data_is_none(self):
        """Test when the srd data tuple for a day is None."""
        broken_data = {
            "Saskatoon": {
                0: None
            }
        }
        climate_driver = SSRDDriver(broken_data)
        result = climate_driver.generate_daily_srd("Saskatoon", 0)
        self.assertIsNone(result)

    def test_srd_data_contains_none_values(self):
        """Test when mean or variance in the srd data tuple is None."""
        broken_data = {
            "Saskatoon": {
                0: (None, 0.2),
                1: (2.5, None),
                2: (None, None)
            }
        }
        climate_driver = SSRDDriver(broken_data)
        self.assertIsNone(climate_driver.generate_daily_srd("Saskatoon", 0))
        self.assertIsNone(climate_driver.generate_daily_srd("Saskatoon", 1))
        self.assertIsNone(climate_driver.generate_daily_srd("Saskatoon", 2))

    def test_variance_negative(self):
        """Test behavior when variance is negative."""
        broken_data = {
            "Saskatoon": {
                0: (2.5, -0.1)
            }
        }
        climate_driver = SSRDDriver(broken_data)
        result = climate_driver.generate_daily_srd("Saskatoon", 0)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()