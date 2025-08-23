import unittest
import sys
import os

# Add the app directory to the path to handle imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from app.models.Fauna.Fauna import Fauna
from app.interfaces.plot_info import PlotInformation


class TestFauna(unittest.TestCase):
    """Test cases for the Fauna class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        class MockPlot(PlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 15.0
            def get_all_fauna(self) -> list:
                return []
            def get_all_flora(self) -> list:
                return []
            def get_avg_snow_height(self) -> float:
                return 5.0
            def get_previous_snow_height(self) -> float:
                return 4.0
            def get_plot_id(self):
                return 1
        
        self.mock_plot = MockPlot()
        
        self.valid_params = {
            'name': 'Test Fauna',
            'description': 'A test fauna species',
            'population': 50,
            'avg_mass': 100.0,
            'ideal_growth_rate': 2.0,
            'ideal_temp_range': (10.0, 25.0),
            'min_food_per_day': 50.0,
            'feeding_rate': 5.0,
            'avg_steps_taken': 1000.0,
            'avg_feet_area': 0.5,
            'plot': self.mock_plot
        }
        
        self.fauna = Fauna(**self.valid_params)
    
    def test_init_valid_parameters(self):   
        """Test Fauna initialization with valid parameters."""
        self.assertEqual(self.fauna.name, 'Test Fauna')
        self.assertEqual(self.fauna.description, 'A test fauna species')
        self.assertEqual(self.fauna.population, 50)
        self.assertEqual(self.fauna.avg_mass, 100.0)
        self.assertEqual(self.fauna.ideal_growth_rate, 2.0)
        self.assertEqual(self.fauna.ideal_temp_range, (10.0, 25.0))
        self.assertEqual(self.fauna.feeding_rate, 5.0)
        self.assertEqual(self.fauna.min_food_per_day, 50.0)
        self.assertEqual(self.fauna.avg_steps_taken, 1000.0)
        self.assertEqual(self.fauna.avg_feet_area, 0.5)
        self.assertEqual(self.fauna.plot, self.mock_plot)
        
        # Test calculated total_mass
        expected_total_mass = 50 * 100.0  # population * avg_mass
        self.assertEqual(self.fauna._total_mass, expected_total_mass)
    
    def test_init_invalid_name_type(self):
        """Test Fauna initialization with invalid name type."""
        params = self.valid_params.copy()
        params['name'] = 123  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be a string", str(context.exception))
    
    def test_init_invalid_name_empty(self):
        """Test Fauna initialization with empty name."""
        params = self.valid_params.copy()
        params['name'] = ""  # Empty string
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_init_invalid_description_type(self):
        """Test Fauna initialization with invalid description type."""
        params = self.valid_params.copy()
        params['description'] = 123  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be a string, got:", str(context.exception))
    
    def test_init_description_empty_allowed(self):
        """Test Fauna initialization with empty description (should be allowed)."""
        params = self.valid_params.copy()
        params['description'] = ""  # Empty string should be allowed
        
        fauna = Fauna(**params)
        self.assertEqual(fauna.description, "")
    
    def test_init_invalid_population_type(self):
        """Test Fauna initialization with invalid population type."""
        params = self.valid_params.copy()
        params['population'] = "50"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of int", str(context.exception))
    
    def test_init_invalid_population_negative(self):
        """Test Fauna initialization with negative population."""
        params = self.valid_params.copy()
        params['population'] = -10  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_avg_mass_type(self):
        """Test Fauna initialization with invalid avg_mass type."""
        params = self.valid_params.copy()
        params['avg_mass'] = "100.0"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_avg_mass_negative(self):
        """Test Fauna initialization with negative avg_mass."""
        params = self.valid_params.copy()
        params['avg_mass'] = -50.0  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_ideal_growth_rate_type(self):
        """Test Fauna initialization with invalid ideal_growth_rate type."""
        params = self.valid_params.copy()
        params['ideal_growth_rate'] = "2.0"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_ideal_growth_rate_negative(self):
        """Test Fauna initialization with negative ideal_growth_rate."""
        params = self.valid_params.copy()
        params['ideal_growth_rate'] = -1.0  # Negative value
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_ideal_temp_range_type(self):
        """Test Fauna initialization with invalid ideal_temp_range type."""
        params = self.valid_params.copy()
        params['ideal_temp_range'] = "10,25"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of tuple", str(context.exception))
    
    def test_init_invalid_ideal_temp_range_wrong_order(self):
        """Test Fauna initialization with ideal_temp_range in wrong order."""
        params = self.valid_params.copy()
        params['ideal_temp_range'] = (25.0, 10.0)  # max, min order
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be in (min, max) order", str(context.exception))
    
    def test_init_invalid_feeding_rate_type(self):
        """Test Fauna initialization with invalid feeding_rate type."""
        params = self.valid_params.copy()
        params['feeding_rate'] = "5.0"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_feeding_rate_zero(self):
        """Test Fauna initialization with zero feeding_rate."""
        params = self.valid_params.copy()
        params['feeding_rate'] = 0.0  # Zero value (not allowed)
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be positive", str(context.exception))
    
    def test_init_invalid_avg_steps_taken_type(self):
        """Test Fauna initialization with invalid avg_steps_taken type."""
        params = self.valid_params.copy()
        params['avg_steps_taken'] = "1000"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_avg_steps_taken_negative(self):
        """Test Fauna initialization with negative avg_steps_taken."""
        params = self.valid_params.copy()
        params['avg_steps_taken'] = -100.0  # Negative value (float)
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_avg_feet_area_type(self):
        """Test Fauna initialization with invalid avg_feet_area type."""
        params = self.valid_params.copy()
        params['avg_feet_area'] = "0.5"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_avg_feet_area_zero(self):
        """Test Fauna initialization with zero avg_feet_area."""
        params = self.valid_params.copy()
        params['avg_feet_area'] = 0.0  # Zero value (not allowed)
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be positive", str(context.exception))
    
    def test_init_invalid_plot_none(self):
        """Test Fauna initialization with None plot."""
        params = self.valid_params.copy()
        params['plot'] = None  # None value
        
        with self.assertRaises(ValueError) as context:
            Fauna(**params)
        self.assertIn("must be provided", str(context.exception))
    
    def test_init_invalid_plot_type(self):
        """Test Fauna initialization with wrong plot type."""
        params = self.valid_params.copy()
        params['plot'] = "not a plot"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Fauna(**params)
        self.assertIn("must be an instance of PlotInformation", str(context.exception))
    
    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.fauna.get_name(), 'Test Fauna')
    
    def test_get_description(self):
        """Test get_description method."""
        self.assertEqual(self.fauna.get_description(), 'A test fauna species')
    
    def test_get_population(self):
        """Test get_population method."""
        self.assertEqual(self.fauna.get_population(), 50)
    
    def test_get_total_mass(self):
        """Test get_total_mass method."""
        expected_total_mass = 50 * 100.0  # population * avg_mass
        self.assertEqual(self.fauna.get_total_mass(), expected_total_mass)
    
    def test_get_feeding_rate(self):
        """Test get_feeding_rate method."""
        self.assertEqual(self.fauna.get_feeding_rate(), 5.0)
    
    def test_get_avg_steps_taken(self):
        """Test get_avg_steps_taken method."""
        self.assertEqual(self.fauna.get_avg_steps_taken(), 1000.0)
    
    def test_get_avg_feet_area(self):
        """Test get_avg_feet_area method."""
        self.assertEqual(self.fauna.get_avg_feet_area(), 0.5)
    
    def test_distance_from_ideal_ideal_value(self):
        """Test distance_from_ideal with ideal value."""
        # Test with value in the middle of ideal range
        result = self.fauna.distance_from_ideal(17.5, (10.0, 25.0))
        self.assertEqual(result, 0.0)
    
    def test_distance_from_ideal_at_min(self):
        """Test distance_from_ideal with value at minimum."""
        result = self.fauna.distance_from_ideal(10.0, (10.0, 25.0))
        self.assertEqual(result, 0.0)
    
    def test_distance_from_ideal_at_max(self):
        """Test distance_from_ideal with value at maximum."""
        result = self.fauna.distance_from_ideal(25.0, (10.0, 25.0))
        self.assertEqual(result, 0.0)
    
    def test_distance_from_ideal_below_range(self):
        """Test distance_from_ideal with value below range."""
        result = self.fauna.distance_from_ideal(5.0, (10.0, 25.0))
        self.assertLess(result, 0.0)
    
    def test_distance_from_ideal_above_range(self):
        """Test distance_from_ideal with value above range."""
        result = self.fauna.distance_from_ideal(30.0, (10.0, 25.0))
        self.assertLess(result, 0.0)
    
    def test_distance_from_ideal_same_min_max(self):
        """Test distance_from_ideal with same min and max values."""
        result = self.fauna.distance_from_ideal(15.0, (15.0, 15.0))
        self.assertEqual(result, 0.0)

    def test_distance_from_min_food_enough(self):
        """Test distance_from_min_food returns 0 when food is sufficient."""
        min_food = self.fauna.min_food_per_day
        self.assertEqual(self.fauna.distance_from_min_food(min_food), 0.0)
        self.assertEqual(self.fauna.distance_from_min_food(min_food + 10), 0.0)

    def test_distance_from_min_food_just_below(self):
        """Test distance_from_min_food returns small negative when just below minimum."""
        min_food = self.fauna.min_food_per_day
        self.assertLess(self.fauna.distance_from_min_food(min_food - 1), 0.0)

    def test_distance_from_min_food_far_below(self):
        """Test distance_from_min_food returns -1.0 when food is zero."""
        self.assertEqual(self.fauna.distance_from_min_food(0.0), -1.0)

    def test_distance_from_min_food_half(self):
        """Test distance_from_min_food returns -0.5 when food is half the minimum."""
        min_food = self.fauna.min_food_per_day
        self.assertAlmostEqual(self.fauna.distance_from_min_food(min_food / 2), -0.5)

if __name__ == '__main__':
    unittest.main()
