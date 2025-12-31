import unittest
from unittest.mock import Mock
import sys
import os

# Add the app directory to the path to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Import directly from the modules to avoid circular imports
from app.models.Flora.Flora import Flora
from app.models.Fauna.Fauna import Fauna
from app.interfaces.flora_plot_info import FloraPlotInformation


class TestFlora(unittest.TestCase):
    """Test cases for the Flora class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        class MockPlot(FloraPlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 20.0
            def get_current_uv(self, day: int) -> float:
                return 5.0
            def get_current_rainfall(self, day: int) -> float:
                return 10.0
            def get_current_melt_water_mass(self, day: int) -> float:
                return 5.0
            def get_current_soil_temp(self, day: int) -> float:
                return 15.0
            def get_all_fauna(self) -> list:
                return []
            def get_all_flora(self) -> list:
                return []
            def get_plot_area(self) -> float:
                return 1.0
            def get_current_snowfall(self, day: int) -> float:
                return 0.0
            def get_avg_snow_height(self) -> float:
                return 0.0
            def get_previous_snow_height(self) -> float:
                return 0.0
        
        self.mock_plot = MockPlot()
        
        class TestFauna(Fauna):
            def __init__(self):
                self.name = "test_fauna"
                self.population = 10
                self.feeding_rate = 2.0
            
            def get_name(self):
                return self.name
            
            def get_feeding_rate(self):
                return self.feeding_rate
        
        self.mock_fauna = TestFauna()
        
        self.valid_params = {
            'name': 'Test Grass',
            'description': 'A test grass species',
            'avg_mass': 2.0,  # 100.0 total_mass / 50 population = 2.0 avg_mass
            'population': 50,
            'ideal_growth_rate': 5.0,
            'ideal_temp_range': (10.0, 30.0),
            'ideal_uv_range': (1.0, 10.0),
            'ideal_hydration_range': (5.0, 20.0),
            'ideal_soil_temp_range': (5.0, 25.0),
            'consumers': [self.mock_fauna],
            'root_depth': 3,  # Set to 3 to include soil_temperature in environmental conditions
            'plot': self.mock_plot
        }
        
        self.flora = Flora(**self.valid_params)
    
    def test_init_valid_parameters(self):
        """Test Flora initialization with valid parameters."""
        flora = Flora(**self.valid_params)
        
        self.assertEqual(flora.name, 'Test Grass')
        self.assertEqual(flora.description, 'A test grass species')
        self.assertEqual(flora.total_mass, 100.0)
        self.assertEqual(flora.population, 50)
        self.assertEqual(flora.ideal_growth_rate, 5.0)
        self.assertEqual(flora.ideal_temp_range, (10.0, 30.0))
        self.assertEqual(flora.ideal_uv_range, (1.0, 10.0))
        self.assertEqual(flora.ideal_hydration_range, (5.0, 20.0))
        self.assertEqual(flora.ideal_soil_temp_range, (5.0, 25.0))
        self.assertEqual(flora.consumers, [self.mock_fauna])
        self.assertEqual(flora.root_depth, 3)  # Changed to 3 to match valid_params
        self.assertEqual(flora.plot, self.mock_plot)
    
    def test_init_invalid_name(self):
        """Test Flora initialization with invalid name."""
        params = self.valid_params.copy()
        params['name'] = 123  # Invalid type
        
        with self.assertRaises(TypeError) as context:
            Flora(**params)
        self.assertIn("must be an instance of str", str(context.exception))
    
    def test_init_empty_name(self):
        """Test Flora initialization with empty name."""
        params = self.valid_params.copy()
        params['name'] = ""  # Empty string
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_init_invalid_avg_mass(self):
        """Test Flora initialization with invalid avg_mass."""
        params = self.valid_params.copy()
        params['avg_mass'] = -10.0  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_population(self):
        """Test Flora initialization with invalid population."""
        params = self.valid_params.copy()
        params['population'] = -5  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_ideal_growth_rate(self):
        """Test Flora initialization with invalid ideal_growth_rate."""
        params = self.valid_params.copy()
        params['ideal_growth_rate'] = -2.0  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_temp_range(self):
        """Test Flora initialization with invalid temperature range."""
        params = self.valid_params.copy()
        params['ideal_temp_range'] = (30.0, 10.0)  # Wrong order
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_init_invalid_uv_range(self):
        """Test Flora initialization with invalid UV range."""
        params = self.valid_params.copy()
        params['ideal_uv_range'] = (10.0, 1.0)  # Wrong order
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_init_invalid_hydration_range(self):
        """Test Flora initialization with invalid hydration range."""
        params = self.valid_params.copy()
        params['ideal_hydration_range'] = (20.0, 5.0)  # Wrong order
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_init_invalid_soil_temp_range(self):
        """Test Flora initialization with invalid soil temperature range."""
        params = self.valid_params.copy()
        params['ideal_soil_temp_range'] = (25.0, 5.0)  # Wrong order
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_init_invalid_consumers(self):
        """Test Flora initialization with invalid consumers."""
        params = self.valid_params.copy()
        params['consumers'] = "not a list"  # Invalid type
        
        with self.assertRaises(TypeError) as context:
            Flora(**params)
        self.assertIn("must be an instance of list", str(context.exception))
    
    def test_init_invalid_root_depth(self):
        """Test Flora initialization with invalid root_depth."""
        params = self.valid_params.copy()
        params['root_depth'] = 5  # Out of range
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be between 1 and 4", str(context.exception))
    
    def test_init_invalid_plot(self):
        """Test Flora initialization with invalid plot."""
        params = self.valid_params.copy()
        params['plot'] = None  # None value
        
        with self.assertRaises(ValueError) as context:
            Flora(**params)
        self.assertIn("must be provided", str(context.exception))
    
    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.flora.get_name(), 'Test Grass')
    
    def test_get_description(self):
        """Test get_description method."""
        self.assertEqual(self.flora.get_description(), 'A test grass species')
    
    def test_get_total_mass(self):
        """Test get_total_mass method."""
        self.assertEqual(self.flora.get_total_mass(), 100.0)
    
    def test_update_flora_mass_valid_day(self):
        """Test update_flora_mass with valid day parameter."""
        initial_mass = self.flora.total_mass
        self.flora.update_flora_mass(day=1)
        
        # mass should have changed due to environmental conditions
        self.assertNotEqual(self.flora.total_mass, initial_mass)
    
    def test_update_flora_mass_invalid_day_type(self):
        """Test update_flora_mass with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.flora.update_flora_mass(day="invalid")
        self.assertIn("must be a number", str(context.exception))
    
    def test_update_flora_mass_negative_day(self):
        """Test update_flora_mass with negative day."""
        with self.assertRaises(ValueError) as context:
            self.flora.update_flora_mass(day=-1)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_get_current_environmental_conditions(self):
        """Test _get_current_environmental_conditions method."""
        conditions = self.flora._get_current_environmental_conditions(day=1)
        
        self.assertIsInstance(conditions, dict)
        self.assertIn('temperature', conditions)
        self.assertIn('uv', conditions)
        self.assertIn('hydration', conditions)
        self.assertIn('soil_temperature', conditions)
        
        expected_hydration = 10.0 + 5.0  # rainfall + melt_water_mass
        self.assertEqual(conditions['hydration'], expected_hydration)
    
    def test_calculate_environmental_penalty_ideal_conditions(self):
        """Test _calculate_environmental_penalty with ideal conditions."""
        
        # within all ranges
        ideal_conditions = {
            'temperature': 20.0,
            'uv': 5.0,
            'hydration': 12.5,
            'soil_temperature': 15.0
        }
        
        penalty = self.flora._calculate_environmental_penalty(ideal_conditions)
        self.assertEqual(penalty, 0.0)  # should apply no penalty
    
    def test_calculate_environmental_penalty_poor_conditions(self):
        """Test _calculate_environmental_penalty with poor conditions."""

        # outside all ranges
        poor_conditions = {
            'temperature': 50.0,
            'uv': 20.0,
            'hydration': 50.0,
            'soil_temperature': 50.0
        }
        
        penalty = self.flora._calculate_environmental_penalty(poor_conditions)
        self.assertLess(penalty, 0.0)  # should have negative penalty
        self.assertGreaterEqual(penalty, -2.0)  # should be capped at -2.0
    
    def test_calculate_environmental_penalty_invalid_input(self):
        """Test _calculate_environmental_penalty with invalid input."""
        with self.assertRaises(TypeError) as context:
            self.flora._calculate_environmental_penalty("not a dict")
        self.assertIn("must be an instance of dict", str(context.exception))
    
    def test_calculate_base_growth_rate(self):
        """Test _calculate_base_growth_rate method."""

        # no penalty
        growth_rate = self.flora._calculate_base_growth_rate(0.0)
        self.assertEqual(growth_rate, 5.0)  # should equal ideal_growth_rate

        # negative penalty
        growth_rate = self.flora._calculate_base_growth_rate(-1.0)
        self.assertEqual(growth_rate, 0.0)  # should be 5.0 * (1 + (-1)) = 0.0
    
    def test_calculate_base_growth_rate_invalid_input(self):
        """Test _calculate_base_growth_rate with invalid input."""
        with self.assertRaises(TypeError) as context:
            self.flora._calculate_base_growth_rate("not a float")
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_update_mass_from_growth_and_consumption(self):
        """Test _update_mass_from_growth_and_consumption method."""
        initial_mass = self.flora.total_mass
        
        # positive growth (growth > consumption)
        self.flora._update_mass_from_growth_and_consumption(0.1, 0.05)  # 10% growth, 5% consumption
        self.assertGreater(self.flora.total_mass, initial_mass)
        
        # negative growth (consumption > growth)
        self.flora._update_mass_from_growth_and_consumption(0.05, 0.1)  # 5% growth, 10% consumption
        self.assertLess(self.flora.total_mass, initial_mass)
        
        # mass doesn't go negative
        self.flora._update_mass_from_growth_and_consumption(-1.0, 0.0)  # Large negative growth
        self.assertGreaterEqual(self.flora.total_mass, 0.0)
    
    def test_update_mass_from_growth_and_consumption_invalid_input(self):
        """Test _update_mass_from_growth_and_consumption with invalid input."""
        with self.assertRaises(TypeError) as context:
            self.flora._update_mass_from_growth_and_consumption("not float", 0.1)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_apply_canopy_shading(self):
        """Test _apply_canopy_shading method."""
        conditions = {
            'temperature': 20.0,
            'uv': 10.0,
            'hydration': 15.0,
            'soil_temperature': 15.0
        }
        
        shaded_conditions = self.flora._apply_canopy_shading(conditions)
        
        self.assertIsInstance(shaded_conditions, dict)
        self.assertEqual(shaded_conditions['temperature'], 20.0)  # Unchanged
        self.assertEqual(shaded_conditions['hydration'], 15.0)    # Unchanged
        self.assertEqual(shaded_conditions['soil_temperature'], 15.0)  # Unchanged
        self.assertLessEqual(shaded_conditions['uv'], 10.0)  # UV should be reduced or unchanged
    
    def test_apply_canopy_shading_invalid_input(self):
        """Test _apply_canopy_shading with invalid input."""
        with self.assertRaises(TypeError) as context:
            self.flora._apply_canopy_shading("not a dict")
        self.assertIn("must be an instance of dict", str(context.exception))

    def test_get_total_plot_canopy_cover(self):
        """Test _get_total_plot_canopy_cover method."""
        # Create a mock tree with canopy cover
        mock_tree = Mock()
        mock_tree.get_Tree_canopy_cover.return_value = 5.0
        
        class MockPlotWithTree(FloraPlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 20.0
            def get_current_uv(self, day: int) -> float:
                return 5.0
            def get_current_rainfall(self, day: int) -> float:
                return 10.0
            def get_current_melt_water_mass(self, day: int) -> float:
                return 5.0
            def get_current_soil_temp(self, day: int) -> float:
                return 15.0
            def get_all_fauna(self) -> list:
                return []
            def get_all_flora(self) -> list:
                return [mock_tree]
            def get_plot_area(self) -> float:
                return 1.0
            def get_current_snowfall(self, day: int) -> float:
                return 0.0
            def get_avg_snow_height(self) -> float:
                return 0.0
            def get_previous_snow_height(self) -> float:
                return 0.0
        
        # Create a new flora instance with the mock plot that has a tree
        mock_plot_with_tree = MockPlotWithTree()
        flora_with_tree = Flora(**{**self.valid_params, 'plot': mock_plot_with_tree})
        
        canopy_cover = flora_with_tree._get_total_plot_canopy_cover()
        self.assertEqual(canopy_cover, 5.0)
    
    def test_distance_from_ideal_ideal_value(self):
        """Test distance_from_ideal with ideal value."""
        # Value in the middle of the range
        distance = self.flora.distance_from_ideal(20.0, (10.0, 30.0))
        self.assertEqual(distance, 0.0)  # Should be ideal
    
    def test_distance_from_ideal_below_range(self):
        """Test distance_from_ideal with value below range."""
        distance = self.flora.distance_from_ideal(5.0, (10.0, 30.0))
        self.assertLess(distance, 0.0)  # Should be negative
        self.assertGreaterEqual(distance, -2.0)  # Should be capped at -2.0
    
    def test_distance_from_ideal_above_range(self):
        """Test distance_from_ideal with value above range."""
        distance = self.flora.distance_from_ideal(40.0, (10.0, 30.0))
        self.assertLess(distance, 0.0)  # Should be negative
        self.assertGreaterEqual(distance, -2.0)  # Should be capped at -2.0
    
    def test_distance_from_ideal_equal_min_max(self):
        """Test distance_from_ideal with equal min and max values."""
        distance = self.flora.distance_from_ideal(10.0, (10.0, 10.0))
        self.assertEqual(distance, 0.0)  # Should return 0 to avoid division by zero
    
    def test_distance_from_ideal_invalid_input(self):
        """Test distance_from_ideal with invalid input."""
        with self.assertRaises(TypeError) as context:
            self.flora.distance_from_ideal("not float", (10.0, 30.0))
        self.assertIn("must be an instance of float", str(context.exception))
        
        with self.assertRaises(TypeError) as context:
            self.flora.distance_from_ideal(20.0, "not tuple")
        self.assertIn("must be an instance of tuple", str(context.exception))
    
    def test_total_consumption_rate(self):
        """Test total_consumption_rate method."""
        class MockPlotWithFauna(FloraPlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 20.0
            def get_current_uv(self, day: int) -> float:
                return 5.0
            def get_current_rainfall(self, day: int) -> float:
                return 10.0
            def get_current_melt_water_mass(self, day: int) -> float:
                return 5.0
            def get_current_soil_temp(self, day: int) -> float:
                return 15.0
            def get_all_fauna(self) -> list:
                return [self.mock_fauna]
            def get_all_flora(self) -> list:
                return []
            def get_plot_area(self) -> float:
                return 1.0
            def get_current_snowfall(self, day: int) -> float:
                return 0.0
            def get_avg_snow_height(self) -> float:
                return 0.0
            def get_previous_snow_height(self) -> float:
                return 0.0
        
        # Create a new flora instance with the mock plot that has fauna
        mock_plot_with_fauna = MockPlotWithFauna()
        mock_plot_with_fauna.mock_fauna = self.mock_fauna  # Store reference
        
        flora_with_fauna = Flora(**{**self.valid_params, 'plot': mock_plot_with_fauna})
        
        consumption_rate = flora_with_fauna.total_consumption_rate()
        expected_rate = 10 * 2.0  # population * feeding_rate
        self.assertEqual(consumption_rate, expected_rate)
    
    def test_total_consumption_rate_no_consumers_on_plot(self):
        """Test total_consumption_rate when consumers are not on the plot."""
        class DifferentTestFauna(Fauna):
            def __init__(self):
                self.name = "different_fauna"
                self.population = 5
                self.feeding_rate = 1.0
            
            def get_name(self):
                return self.name
            
            def get_feeding_rate(self):
                return self.feeding_rate
        
        different_fauna = DifferentTestFauna()
        
        class MockPlotWithDifferentFauna(FloraPlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 20.0
            def get_current_uv(self, day: int) -> float:
                return 5.0
            def get_current_rainfall(self, day: int) -> float:
                return 10.0
            def get_current_melt_water_mass(self, day: int) -> float:
                return 5.0
            def get_current_soil_temp(self, day: int) -> float:
                return 15.0
            def get_all_fauna(self) -> list:
                return [self.mock_fauna]  # Different fauna on plot
            def get_all_flora(self) -> list:
                return []
            def get_plot_area(self) -> float:
                return 1.0
            def get_current_snowfall(self, day: int) -> float:
                return 0.0
            def get_avg_snow_height(self) -> float:
                return 0.0
            def get_previous_snow_height(self) -> float:
                return 0.0
        
        # Create a new flora instance with the mock plot that has different fauna
        mock_plot_with_different_fauna = MockPlotWithDifferentFauna()
        mock_plot_with_different_fauna.mock_fauna = self.mock_fauna  # Store reference
        
        flora = Flora(**{**self.valid_params, 'consumers': [different_fauna], 'plot': mock_plot_with_different_fauna})
        
        consumption_rate = flora.total_consumption_rate()
        self.assertEqual(consumption_rate, 0.0)  # Should be 0 since consumer not on plot
    
    def test_capacity_penalty_base_implementation(self):
        """Test capacity_penalty base implementation."""
        initial_mass = self.flora.total_mass
        self.flora.capacity_penalty()
        self.assertEqual(self.flora.total_mass, initial_mass)  # should be unchanged
    
    def test_validate_string_valid(self):
        """Test _validate_string with valid input."""
        # Should not raise any exception
        Flora._validate_string("valid string", "test_param")
        Flora._validate_string("", "test_param", allow_empty=True)
    
    def test_validate_string_invalid(self):
        """Test _validate_string with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_string(123, "test_param")
        self.assertIn("must be a string", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_string("", "test_param")
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_validate_positive_number_valid(self):
        """Test _validate_positive_number with valid input."""
        # Should not raise any exception
        Flora._validate_positive_number(5, "test_param")
        Flora._validate_positive_number(5.0, "test_param")
        Flora._validate_positive_number(0, "test_param", allow_zero=True)
        Flora._validate_positive_number(5, "test_param", allow_zero=False)
    
    def test_validate_positive_number_invalid(self):
        """Test _validate_positive_number with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_positive_number("not a number", "test_param")
        self.assertIn("must be a number", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_positive_number(-5, "test_param")
        self.assertIn("must be non-negative", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_positive_number(0, "test_param", allow_zero=False)
        self.assertIn("must be positive", str(context.exception))
    
    def test_validate_range_tuple_valid(self):
        """Test _validate_range_tuple with valid input."""
        # Should not raise any exception
        Flora._validate_range_tuple((1.0, 5.0), "test_param")
        Flora._validate_range_tuple((0, 10), "test_param")
    
    def test_validate_range_tuple_invalid(self):
        """Test _validate_range_tuple with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_range_tuple("not a tuple", "test_param")
        self.assertIn("must be a tuple", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_range_tuple((1.0,), "test_param")
        self.assertIn("must be a tuple of 2 values", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_range_tuple((1.0, 5.0, 10.0), "test_param")
        self.assertIn("must be a tuple of 2 values", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_range_tuple(("a", "b"), "test_param")
        self.assertIn("must contain only numbers", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_range_tuple((5.0, 1.0), "test_param")
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_validate_integer_range_valid(self):
        """Test _validate_integer_range with valid input."""
        # Should not raise any exception
        Flora._validate_integer_range(5, "test_param", 1, 10)
        Flora._validate_integer_range(1, "test_param", 1, 10)
        Flora._validate_integer_range(10, "test_param", 1, 10)
    
    def test_validate_integer_range_invalid(self):
        """Test _validate_integer_range with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_integer_range(5.0, "test_param", 1, 10)
        self.assertIn("must be an integer", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_integer_range(0, "test_param", 1, 10)
        self.assertIn("must be between 1 and 10", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_integer_range(11, "test_param", 1, 10)
        self.assertIn("must be between 1 and 10", str(context.exception))
    
    def test_validate_list_valid(self):
        """Test _validate_list with valid input."""
        # Should not raise any exception
        Flora._validate_list([1, 2, 3], "test_param")
        Flora._validate_list([], "test_param")
        Flora._validate_list([self.mock_fauna], "test_param", Fauna)
    
    def test_validate_list_invalid(self):
        """Test _validate_list with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_list("not a list", "test_param")
        self.assertIn("must be a list", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            Flora._validate_list([1, "string", 3], "test_param", int)
        self.assertIn("must contain only int objects", str(context.exception))
    
    def test_validate_not_none_valid(self):
        """Test _validate_not_none with valid input."""
        # Should not raise any exception
        Flora._validate_not_none("valid", "test_param")
        Flora._validate_not_none(0, "test_param")
        Flora._validate_not_none(False, "test_param")
    
    def test_validate_not_none_invalid(self):
        """Test _validate_not_none with invalid input."""
        with self.assertRaises(ValueError) as context:
            Flora._validate_not_none(None, "test_param")
        self.assertIn("must be provided", str(context.exception))
    
    def test_validate_instance_valid(self):
        """Test _validate_instance with valid input."""
        # Should not raise any exception
        Flora._validate_instance("string", str, "test_param")
        Flora._validate_instance(5, int, "test_param")
        Flora._validate_instance(5.0, float, "test_param")
    
    def test_validate_instance_invalid(self):
        """Test _validate_instance with invalid input."""
        with self.assertRaises(TypeError) as context:
            Flora._validate_instance("string", int, "test_param")
        self.assertIn("must be an instance of int", str(context.exception))
        
        with self.assertRaises(TypeError) as context:
            Flora._validate_instance(5, str, "test_param")
        self.assertIn("must be an instance of str", str(context.exception))


if __name__ == '__main__':
    unittest.main()
