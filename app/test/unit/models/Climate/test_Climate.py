import unittest
import logging
from unittest.mock import Mock, patch
from app.models.Climate import Climate
from app.interfaces.plot_info import PlotInformation


class TestClimate(unittest.TestCase):
    """Test cases for the Climate class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        logging.basicConfig(level=logging.DEBUG)
        
        self.mock_plot = Mock(spec=PlotInformation)
        self.mock_plot.delta_snow_height = Mock(return_value=0.1)
        self.mock_plot.get_flora_mass_composition = Mock(return_value=(0.8, 0.1, 0.05, 0.05))
        
        self.climate = Climate("southern taiga", self.mock_plot)

    def test_init(self):
        """Test Climate initialization."""
        self.assertEqual(self.climate.biome, "southern taiga")
        self.assertEqual(self.climate.consecutive_frozen_soil_days, 0)
        # Climate uses class-level _class_loaders, not instance-level loaders
        
        for data_type in ['temperature', 'soil_temp', 'snowfall', 'rainfall', 'uv', 'ssrd']:
            self.assertEqual(self.climate.recent_values[data_type].maxlen, 7)  # deque max len
            self.assertEqual(len(self.climate.recent_values[data_type]), 0)  # deque empty

    def test_init_invalid_biome_type(self):
        """Test initialization with invalid biome type."""
        with self.assertRaises(TypeError) as context:
            Climate(101, self.mock_plot)
        self.assertIn("Biome must be a string", str(context.exception))

    def test_init_unknown_biome(self):
        """Test initialization with unknown biome."""
        with self.assertRaises(ValueError) as context:
            Climate("unknown_biome", self.mock_plot)
        self.assertIn("Unknown biome", str(context.exception))

    def test_set_biome(self):
        """Test setting biome."""
        self.climate.set_biome("northern taiga")
        self.assertEqual(self.climate.biome, "northern taiga")

    def test_set_biome_invalid_type(self):
        """Test setting biome with invalid type."""
        with self.assertRaises(TypeError) as context:
            self.climate.set_biome(101)
        self.assertIn("Biome must be a string", str(context.exception))

    def test_set_biome_unknown_biome(self):
        """Test setting biome with unknown biome name."""
        with self.assertRaises(ValueError) as context:
            self.climate.set_biome("unknown_biome")
        self.assertIn("Unknown biome", str(context.exception))

    def test_get_biome(self):
        """Test getting biome."""
        self.assertEqual(self.climate.get_biome(), "southern taiga")

    def test_get_fallback_value_no_fallback(self):
        """Test getting fallback value when none exists."""
        with self.assertRaises(RuntimeError) as context:
            self.climate._get_fallback_value('temperature', 1)
        self.assertIn("No recent fallback values available", str(context.exception))

    def test_get_fallback_value_with_fallback(self):
        """Test getting fallback value when one exists."""
        self.climate.recent_values['temperature'].append(15.0)
        result = self.climate._get_fallback_value('temperature', 1)
        self.assertEqual(result, 15.0)

    def test_get_fallback_value_multiple_values(self):
        """Test getting fallback value when multiple values exist."""
        self.climate.recent_values['temperature'].extend([10.0, 12.0, 15.0])
        result = self.climate._get_fallback_value('temperature', 1)
        self.assertEqual(result, 15.0)  # should return most recent

    def test_get_fallback_value_with_none_values(self):
        """Test getting fallback value when some values are None."""
        self.climate.recent_values['temperature'].extend([None, 12.0, 15.0, None])
        result = self.climate._get_fallback_value('temperature', 1)
        self.assertEqual(result, 15.0)  # should return most recent non-None

    def test_get_fallback_value_all_none_values(self):
        """Test getting fallback value when all values are None."""
        self.climate.recent_values['temperature'].extend([None, None, None])
        with self.assertRaises(RuntimeError) as context:
            self.climate._get_fallback_value('temperature', 1)
        self.assertIn("All recent fallback values for temperature on day 1 are None", str(context.exception))

    def test_get_fallback_value_mixed_none_values(self):
        """Test getting fallback value with mixed None and valid values."""
        self.climate.recent_values['temperature'].extend([None, 10.0, None, 20.0, None])
        result = self.climate._get_fallback_value('temperature', 1)
        self.assertEqual(result, 20.0)  # Should return most recent non-None value

    def test_update_recent_value(self):
        """Test updating recent value."""
        self.climate._update_recent_value('temperature', 20.0)
        self.assertEqual(list(self.climate.recent_values['temperature']), [20.0])

    def test_update_recent_value_none(self):
        """Test updating recent value with None (should now update)."""
        self.climate.recent_values['temperature'].append(15.0)
        self.climate._update_recent_value('temperature', None)
        self.assertEqual(list(self.climate.recent_values['temperature']), [15.0, None])

    def test_update_recent_value_with_none_values(self):
        """Test updating recent values with None values mixed in."""
        self.climate._update_recent_value('temperature', 10.0)
        self.climate._update_recent_value('temperature', None)
        self.climate._update_recent_value('temperature', 20.0)
        self.climate._update_recent_value('temperature', None)
        self.assertEqual(list(self.climate.recent_values['temperature']), [10.0, None, 20.0, None])

    def test_update_recent_value_maxlen(self):
        """Test that recent values respect the maxlen limit."""
        for i in range(10):
            self.climate._update_recent_value('temperature', float(i))
        
        expected_values = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]  # 0.0, 1.0, 2.0 get dequeued
        self.assertEqual(list(self.climate.recent_values['temperature']), expected_values)
        self.assertEqual(len(self.climate.recent_values['temperature']), 7)

    def test_get_current_temperature_invalid_day(self):
        """Test getting temperature with invalid day."""
        with self.assertRaises(ValueError) as context:
            self.climate._get_current_temperature(0)
        self.assertIn("Day must be between 1 and 365", str(context.exception))

    def test_get_current_temperature_invalid_day_type(self):
        """Test getting temperature with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.climate._get_current_temperature("1")
        self.assertIn("Day must be an integer", str(context.exception))

    @patch('app.models.Climate.Climate.TemperatureDriver')
    @patch('app.models.Climate.Climate.TemperatureLoader')
    def test_get_current_temperature_success(self, mock_loader_class, mock_driver_class):
        """Test successful temperature calculation."""
        mock_loader = Mock()
        mock_loader.get_temp_data.return_value = {"southern taiga": {1: (10.0, 5.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_temp.return_value = 15.0
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_temperature(1)
        
        self.assertEqual(result, 15.0)
        self.assertEqual(list(self.climate.recent_values['temperature']), [15.0])

    @patch('app.models.Climate.Climate.TemperatureDriver')
    @patch('app.models.Climate.Climate.TemperatureLoader')
    def test_get_current_temperature_with_fallback(self, mock_loader_class, mock_driver_class):
        """Test temperature calculation with fallback when driver returns None."""
        self.climate.recent_values['temperature'].append(12.0)
        
        mock_loader = Mock()
        mock_loader.get_temp_data.return_value = {"southern taiga": {1: (10.0, 5.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_temp.return_value = None
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_temperature(1)  # should use fallback value 12.0
        self.assertEqual(result, 12.0)

    @patch('app.models.Climate.Climate.TemperatureDriver')
    @patch('app.models.Climate.Climate.TemperatureLoader')
    def test_get_current_temperature_no_fallback(self, mock_loader_class, mock_driver_class):
        """Test temperature calculation when driver returns None and no fallback."""
        mock_loader = Mock()
        mock_loader.get_temp_data.return_value = {"southern taiga": {1: (10.0, 5.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_temp.return_value = None
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        with self.assertRaises(RuntimeError) as context:
            self.climate._get_current_temperature(1)
        self.assertIn("No recent fallback values available", str(context.exception))

    def test_get_current_soil_temp_invalid_day(self):
        """Test getting soil temperature with invalid day."""
        with self.assertRaises(ValueError) as context:
            self.climate._get_current_soil_temp(366)
        self.assertIn("Day must be between 1 and 365", str(context.exception))

    @patch('app.models.Climate.Climate.SoilTemp4Driver')
    @patch('app.models.Climate.Climate.SoilTemp4Loader')
    def test_get_current_soil_temp_success(self, mock_loader_class, mock_driver_class):
        """Test successful soil temperature calculation."""
        mock_loader = Mock()
        mock_loader.get_soil_temp4_data.return_value = {"southern taiga": {1: (5.0, 2.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_soil_temp.return_value = 3.0
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_soil_temp(1)
        
        self.assertEqual(result, 3.0)
        self.assertEqual(list(self.climate.recent_values['soil_temp']), [3.0])

    def test_update_consecutive_frozen_soil_days_positive_temp(self):
        """Test updating consecutive frozen days with positive temperature."""
        initial_count = self.climate.consecutive_frozen_soil_days
        self.climate._update_consecutive_frozen_soil_days(5.0)
        self.assertEqual(self.climate.consecutive_frozen_soil_days, 0)

    def test_update_consecutive_frozen_soil_days_negative_temp(self):
        """Test updating consecutive frozen days with negative temperature."""
        initial_count = self.climate.consecutive_frozen_soil_days
        self.climate._update_consecutive_frozen_soil_days(-5.0)
        self.assertEqual(self.climate.consecutive_frozen_soil_days, initial_count + 1)

    def test_update_consecutive_frozen_soil_days_zero_temp(self):
        """Test updating consecutive frozen days with zero temperature."""
        initial_count = self.climate.consecutive_frozen_soil_days
        self.climate._update_consecutive_frozen_soil_days(0.0)
        self.assertEqual(self.climate.consecutive_frozen_soil_days, 0)

    def test_update_consecutive_frozen_soil_days_invalid_type(self):
        """Test updating consecutive frozen days with invalid soil temperature type."""
        initial_count = self.climate.consecutive_frozen_soil_days
        self.climate._update_consecutive_frozen_soil_days("invalid")
        self.assertEqual(self.climate.consecutive_frozen_soil_days, initial_count)

    def test_is_permafrost_not_enough_days(self):
        """Test is_permafrost when not enough consecutive frozen days."""
        self.climate.consecutive_frozen_soil_days = 4  # threshold is 5 days for testing
        result = self.climate.is_permafrost()
        self.assertFalse(result)

    def test_is_permafrost_enough_days(self):
        """Test is_permafrost when enough consecutive frozen days."""
        self.climate.consecutive_frozen_soil_days = 730
        result = self.climate.is_permafrost()
        self.assertTrue(result)

    def test_is_permafrost_more_than_enough_days(self):
        """Test is_permafrost when more than enough consecutive frozen days."""
        self.climate.consecutive_frozen_soil_days = 10000
        result = self.climate.is_permafrost()
        self.assertTrue(result)

    def test_is_permafrost_exactly_720_days(self):
        """Test is_permafrost when exactly at the threshold."""
        self.climate.consecutive_frozen_soil_days = 720
        result = self.climate.is_permafrost()
        self.assertTrue(result)

    def test_is_steppe_valid_steppe_conditions(self):
        """
        Test is_steppe with valid steppe conditions.
        Note: is_steppe() is currently disabled (always returns False) until fauna is implemented.
        """
        self.climate.consecutive_frozen_soil_days = 720  # valid permafrost
        self.mock_plot.get_flora_mass_composition.return_value = (0.9, 0.1, 0.0, 0.0)  # valid steppe ratios
        result = self.climate.is_steppe()
        self.assertFalse(result)  # is_steppe is currently disabled and always returns False

    def test_is_steppe_non_steppe_conditions_invalid_permafrost(self):
        """
        Test is_steppe with non-steppe conditions.
        Valid flora ratios but invalid permafrost.
        """
        self.climate.consecutive_frozen_soil_days = 100  # invalid permafrost (not enough days)
        self.mock_plot.get_flora_mass_composition.return_value = (0.9, 0.1, 0.0, 0.0)  # valid steppe ratios
        result = self.climate.is_steppe()
        self.assertFalse(result)

    def test_is_steppe_non_steppe_conditions_invalid_ratios(self):
        """
        Test is_steppe with non-steppe conditions.
        Valid permafrost but invalid flora ratios.
        """
        self.climate.consecutive_frozen_soil_days = 720  # valid permafrost
        self.mock_plot.get_flora_mass_composition.return_value = (0.3, 0.3, 0.3, 0.1)  # invalid ratios
        result = self.climate.is_steppe()
        self.assertFalse(result)

    def test_is_steppe_invalid_flora_composition_length(self):
        """
        Test is_steppe with invalid flora composition (wrong length).
        """
        self.climate.consecutive_frozen_soil_days = 720  # valid permafrost
        self.mock_plot.get_flora_mass_composition.return_value = (0.8, 0.2)  # only 2 values instead of 4
        result = self.climate.is_steppe()
        self.assertFalse(result)

    def test_is_steppe_invalid_flora_ratios_sum(self):
        """
        Test is_steppe with invalid flora ratios that don't sum to 1.0.
        """
        self.climate.consecutive_frozen_soil_days = 720  # valid permafrost
        self.mock_plot.get_flora_mass_composition.return_value = (0.9, 0.2, 0.0, 0.0)  # sums to 1.1 not 1.0
        result = self.climate.is_steppe()
        self.assertFalse(result)

    def test_clamp_static_method(self):
        """Test the static clamp method."""
        self.assertEqual(Climate.clamp(5.0, 0.0, 10.0), 5.0)
        self.assertEqual(Climate.clamp(-5.0, 0.0, 10.0), 0.0)
        self.assertEqual(Climate.clamp(15.0, 0.0, 10.0), 10.0)
        self.assertEqual(Climate.clamp(0.0, 0.0, 10.0), 0.0)
        self.assertEqual(Climate.clamp(10.0, 0.0, 10.0), 10.0)

    def test_2mtemp_change_from_snow_delta_static_method(self):
        """Test the static _2mtemp_change_from_snow_delta method."""
        # Test positive snow delta (more snow = cools air)
        # AIR_SENSITIVITY = 20.0, so -0.1 * 20.0 = -2.0°C (clamped to -15.0 max)
        result = Climate._2mtemp_change_from_snow_delta(0.1)
        self.assertIsInstance(result, float)
        self.assertEqual(result, -2.0)  # -0.1 * 20.0 = -2.0°C
        
        # Test negative snow delta (less snow = warms air)
        result = Climate._2mtemp_change_from_snow_delta(-0.1)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 2.0)  # -(-0.1) * 20.0 = 2.0°C
        
        # Test zero snow delta (no change)
        result = Climate._2mtemp_change_from_snow_delta(0.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 0.0)  # -0.0 * 20.0 = 0.0°C
        
        # Test clamping at maximum negative value (MAX_DAILY_AIR_DELTA = 1.5)
        result = Climate._2mtemp_change_from_snow_delta(1.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, -1.5)  # -1.0 * 2.0 = -2.0, clamped to -1.5
        
        # Test clamping at maximum positive value (MAX_DAILY_AIR_DELTA = 1.5)
        result = Climate._2mtemp_change_from_snow_delta(-1.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 1.5)  # -(-1.0) * 2.0 = 2.0, clamped to 1.5

    def test_soil_temp_change_from_snow_delta_static_method(self):
        """Test the static _soil_temp_change_from_snow_delta method."""
        # Test positive snow delta (more snow = warms soil)
        # SOIL_SENSITIVITY = 50.0, so 0.1 * 50.0 = 5.0°C (clamped to 30.0 max)
        result = Climate._soil_temp_change_from_snow_delta(0.1)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 5.0)  # 0.1 * 50.0 = 5.0°C
        
        # Test negative snow delta (less snow = cools soil)
        result = Climate._soil_temp_change_from_snow_delta(-0.1)
        self.assertIsInstance(result, float)
        self.assertEqual(result, -5.0)  # -0.1 * 50.0 = -5.0°C
        
        # Test zero snow delta (no change)
        result = Climate._soil_temp_change_from_snow_delta(0.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 0.0)  # 0.0 * 50.0 = 0.0°C
        
        # Test clamping at maximum positive value (MAX_DAILY_SOIL_DELTA = 3.0)
        result = Climate._soil_temp_change_from_snow_delta(1.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 3.0)  # 1.0 * 5.0 = 5.0, clamped to 3.0
        
        # Test clamping at maximum negative value (MAX_DAILY_SOIL_DELTA = 3.0)
        result = Climate._soil_temp_change_from_snow_delta(-1.0)
        self.assertIsInstance(result, float)
        self.assertEqual(result, -3.0)  # -1.0 * 5.0 = -5.0, clamped to -3.0

    def test_load_climate_loader_caching(self):
        """Test that climate loaders are cached."""
        loader1 = self.climate._load_climate_loader("temperature", Mock)
        loader2 = self.climate._load_climate_loader("temperature", Mock)
        self.assertIs(loader1, loader2)
        
        loader3 = self.climate._load_climate_loader("snowfall", Mock)
        self.assertIsNot(loader1, loader3)

    def test_load_climate_loader_unknown_type(self):
        """Test loading climate loader with unknown type."""
        with self.assertRaises(ValueError) as context:
            self.climate._load_climate_loader("unknown_type", Mock)
        self.assertIn("Unknown loader type", str(context.exception))

    def test_biome_file_map_structure(self):
        """
        Test that BIOME_FILE_MAP has the expected structure.
        Each biome must have all data types, that are strings and contain a csv file path.
        """
        from app.models.Climate.Climate import BIOME_FILE_MAP
        
        expected_biomes = ["southern taiga", "northern taiga", "southern tundra", "northern tundra"]
        expected_data_types = ["temperature", "snowfall", "rainfall", "uv", "soil_temp4", "ssrd"]
        
        for biome in expected_biomes:
            self.assertIn(biome, BIOME_FILE_MAP)
            for data_type in expected_data_types:
                self.assertIn(data_type, BIOME_FILE_MAP[biome])
                self.assertIsInstance(BIOME_FILE_MAP[biome][data_type], str)
                self.assertTrue(BIOME_FILE_MAP[biome][data_type].endswith('.csv'))

    @patch('app.models.Climate.Climate.SnowfallDriver')
    @patch('app.models.Climate.Climate.SnowfallLoader')
    def test_get_current_snowfall_success(self, mock_loader_class, mock_driver_class):
        """Test successful snowfall calculation."""
        mock_loader = Mock()
        mock_loader.get_snowfall_data.return_value = {"southern taiga": {1: (5.0, 2.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_snowfall.return_value = 3.0
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_snowfall(1)
        self.assertEqual(result, 3.0)

    @patch('app.models.Climate.Climate.RainfallDriver')
    @patch('app.models.Climate.Climate.RainfallLoader')
    def test_get_current_rainfall_success(self, mock_loader_class, mock_driver_class):
        """Test successful rainfall calculation."""
        mock_loader = Mock()
        mock_loader.get_rainfall_data.return_value = {"southern taiga": {1: (2.0, 1.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_rainfall.return_value = 1.5
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_rainfall(1)
        self.assertEqual(result, 1.5)

    @patch('app.models.Climate.Climate.UVDriver')
    @patch('app.models.Climate.Climate.UVLoader')
    def test_get_current_uv_success(self, mock_loader_class, mock_driver_class):
        """Test successful UV calculation."""
        mock_loader = Mock()
        mock_loader.get_uv_data.return_value = {"southern taiga": {1: (3.0, 1.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_uv.return_value = 2.5
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_uv(1)
        self.assertEqual(result, 2.5)

    @patch('app.models.Climate.Climate.SSRDDriver')
    @patch('app.models.Climate.Climate.SSRDLoader')
    def test_get_current_SSRD_success(self, mock_loader_class, mock_driver_class):
        """Test successful SSRD calculation."""
        mock_loader = Mock()
        mock_loader.get_srd_data.return_value = {"southern taiga": {1: (100.0, 20.0)}}
        mock_loader_class.return_value = mock_loader
        
        mock_driver = Mock()
        mock_driver.generate_daily_srd.return_value = 80.0
        mock_driver_class.return_value = mock_driver
        
        Climate._class_loaders.clear()  # Clear class-level cache
        
        result = self.climate._get_current_SSRD(1)
        self.assertEqual(result, 80.0)


if __name__ == '__main__':
    unittest.main()
