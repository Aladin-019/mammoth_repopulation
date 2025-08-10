import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the app directory to the path to handle imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

from app.models.Fauna.Predator import Predator
from app.models.Fauna.Fauna import Fauna
from app.interfaces.plot_info import PlotInformation


class TestPredator(unittest.TestCase):
    
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
                return 0.1
            def get_previous_snow_height(self) -> float:
                return 0.05
            def over_predator_capacity(self) -> bool:
                return False
            def get_temperature(self, day: int) -> float:
                return 15.0
        
        self.mock_plot = MockPlot()
        
        class MockPrey(Fauna):
            def __init__(self, plot):
                super().__init__(
                    name="test_prey",
                    description="A test prey",
                    population=10,
                    avg_mass=30.0,
                    ideal_temp_range=(5.0, 20.0),
                    ideal_food_range=(20.0, 80.0),
                    ideal_growth_rate=0.2,
                    feeding_rate=1.0,
                    avg_steps_taken=5.0,
                    avg_feet_area=0.2,
                    plot=plot
                )
            
            def get_name(self):
                return "test_prey"
            
            def get_total_mass(self):
                return self.population * self.avg_mass
        
        self.mock_prey = MockPrey(self.mock_plot)
        
        # Valid parameters for Predator constructor
        self.valid_params = {
            'name': "test_predator",
            'description': "A test predator species",
            'population': 3,
            'avg_mass': 80.0,
            'ideal_temp_range': (8.0, 22.0),
            'ideal_food_range': (100.0, 500.0),
            'ideal_growth_rate': 0.08,
            'feeding_rate': 2.5,
            'avg_steps_taken': 12.0,
            'avg_feet_area': 0.6,
            'plot': self.mock_plot,
            'prey': [self.mock_prey]
        }
    
    def test_init_valid_parameters(self):
        """Test Predator initialization with valid parameters."""
        predator = Predator(**self.valid_params)
        
        self.assertEqual(predator.name, "test_predator")
        self.assertEqual(predator.description, "A test predator species")
        self.assertEqual(predator.population, 3)
        self.assertEqual(predator.avg_mass, 80.0)
        self.assertEqual(predator.ideal_temp_range, (8.0, 22.0))
        self.assertEqual(predator.ideal_food_range, (100.0, 500.0))
        self.assertEqual(predator.ideal_growth_rate, 0.08)
        self.assertEqual(predator.feeding_rate, 2.5)
        self.assertEqual(predator.avg_steps_taken, 12.0)
        self.assertEqual(predator.avg_feet_area, 0.6)
        self.assertEqual(predator.plot, self.mock_plot)
        self.assertEqual(predator.prey, [self.mock_prey])
    
    def test_init_invalid_prey_type(self):
        """Test Predator initialization with invalid prey type."""
        params = self.valid_params.copy()
        params['prey'] = "not a list"  # Invalid type
        
        with self.assertRaises(TypeError) as context:
            Predator(**params)
        self.assertIn("must be an instance of list", str(context.exception))
    
    def test_init_invalid_prey_element_type(self):
        """Test Predator initialization with invalid prey element type."""
        params = self.valid_params.copy()
        params['prey'] = ["not a Fauna object"]  # Invalid element type
        
        with self.assertRaises(ValueError) as context:
            Predator(**params)
        self.assertIn("must contain only Fauna objects", str(context.exception))
    
    def test_total_available_prey_mass_no_prey_on_plot(self):
        """Test total available prey mass when no prey are on the plot."""
        predator = Predator(**self.valid_params)
        
        # Mock plot to return empty fauna list
        self.mock_plot.get_all_fauna = Mock(return_value=[])
        
        result = predator.total_available_prey_mass()
        self.assertEqual(result, 0.0)
    
    def test_total_available_prey_mass_with_prey_on_plot(self):
        """Test total available prey mass when prey are on the plot."""
        predator = Predator(**self.valid_params)
        
        self.mock_plot.get_all_fauna = Mock(return_value=[self.mock_prey])
        
        result = predator.total_available_prey_mass()
        # Expected: population * avg_mass = 10 * 30.0 = 300.0
        self.assertEqual(result, 300.0)
    
    def test_total_available_prey_mass_different_prey_on_plot(self):
        """Test total available prey mass when different prey are on the plot."""
        predator = Predator(**self.valid_params)
        
        # Prey that's not in predator's prey list
        class DifferentPrey(Fauna):
            def __init__(self, plot):
                super().__init__(
                    name="different_prey",
                    description="A different prey",
                    population=8,
                    avg_mass=25.0,
                    ideal_temp_range=(3.0, 18.0),
                    ideal_food_range=(15.0, 70.0),
                    ideal_growth_rate=0.18,
                    feeding_rate=0.8,
                    avg_steps_taken=4.0,
                    avg_feet_area=0.15,
                    plot=plot
                )
            
            def get_name(self):
                return "different_prey"
            
            def get_total_mass(self):
                return self.population * self.avg_mass
        
        different_prey = DifferentPrey(self.mock_plot)
        
        self.mock_plot.get_all_fauna = Mock(return_value=[different_prey])
        
        result = predator.total_available_prey_mass()
        # Should be 0.0 because the prey on the plot is not in predator's prey list
        self.assertEqual(result, 0.0)
    
    def test_update_predator_mass_valid_day(self):
        """Test updating predator mass with valid day."""
        predator = Predator(**self.valid_params)
        
        predator._get_current_environmental_conditions = Mock(return_value={
            'temperature': 15.0,
            'food': 200.0
        })
        predator._calculate_environmental_penalty = Mock(return_value=-0.3)
        predator._calculate_base_growth_rate = Mock(return_value=0.056)
        predator._update_mass_from_growth = Mock()
        
        predator.update_predator_mass(1)
        
        # Verify the methods were called correctly
        predator._get_current_environmental_conditions.assert_called_once_with(1)
        predator._calculate_environmental_penalty.assert_called_once()
        predator._calculate_base_growth_rate.assert_called_once_with(-0.3)
        predator._update_mass_from_growth.assert_called_once_with(0.056)
    
    def test_update_predator_mass_invalid_day_type(self):
        """Test updating predator mass with invalid day type."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            predator.update_predator_mass("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_update_predator_mass_negative_day(self):
        """Test updating predator mass with negative day."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(ValueError) as context:
            predator.update_predator_mass(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_environmental_conditions(self):
        """Test getting current environmental conditions."""
        predator = Predator(**self.valid_params)
        
        self.mock_plot.get_temperature = Mock(return_value=15.0)
        predator.total_available_prey_mass = Mock(return_value=250.0)
        
        result = predator._get_current_environmental_conditions(1)
        
        expected = {
            'temperature': 15.0,
            'food': 250.0
        }
        self.assertEqual(result, expected)
        self.mock_plot.get_temperature.assert_called_once_with(1)
        predator.total_available_prey_mass.assert_called_once()
    
    def test_calculate_environmental_penalty_ideal_conditions(self):
        """Test environmental penalty calculation with ideal conditions."""
        predator = Predator(**self.valid_params)
        
        environmental_conditions = {
            'temperature': 15.0,  # Midpoint of ideal range (8.0, 22.0)
            'food': 300.0         # Midpoint of ideal range (100.0, 500.0)
        }
        
        result = predator._calculate_environmental_penalty(environmental_conditions)
        
        # Both conditions are ideal (distance = 0), so penalty should be 0
        self.assertEqual(result, 0.0)
    
    def test_calculate_environmental_penalty_poor_conditions(self):
        """Test environmental penalty calculation with poor conditions."""
        predator = Predator(**self.valid_params)
        
        environmental_conditions = {
            'temperature': 35.0,  # Far above ideal range
            'food': 50.0          # Far below ideal range
        }
        
        result = predator._calculate_environmental_penalty(environmental_conditions)
        
        # Both conditions are poor, so penalty should be negative
        self.assertLess(result, 0.0)
    
    def test_calculate_environmental_penalty_invalid_input(self):
        """Test environmental penalty calculation with invalid input."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            predator._calculate_environmental_penalty("not a dict")
        self.assertIn("environmental_conditions must be an instance of dict", str(context.exception))
    
    def test_calculate_base_growth_rate(self):
        """Test base growth rate calculation."""
        predator = Predator(**self.valid_params)
        
        environmental_penalty = -0.4
        result = predator._calculate_base_growth_rate(environmental_penalty)
        
        # Expected: ideal_growth_rate * (1 + penalty) = 0.08 * (1 + (-0.4)) = 0.048
        expected = 0.048
        self.assertEqual(result, expected)
    
    def test_calculate_base_growth_rate_invalid_input(self):
        """Test base growth rate calculation with invalid input."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            predator._calculate_base_growth_rate("not a float")
        self.assertIn("environmental_penalty must be an instance of float", str(context.exception))
    
    def test_update_mass_from_growth(self):
        """Test updating mass from growth."""
        predator = Predator(**self.valid_params)
        
        # Set initial mass
        predator.set_total_mass(240.0)  # population * avg_mass = 3 * 80.0
        
        base_growth_rate = 0.05
        
        predator._update_mass_from_growth(base_growth_rate)
        
        # Expected: new_mass = 240 + 240 * 0.05 = 240 + 12 = 252
        expected = 252.0
        self.assertEqual(predator.get_total_mass(), expected)
    
    def test_update_mass_from_growth_invalid_input(self):
        """Test updating mass with invalid input."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            predator._update_mass_from_growth("not a float")
        self.assertIn("base_growth_rate must be an instance of float", str(context.exception))
    
    def test_capacity_penalty_base_implementation(self):
        """Test the base capacity penalty implementation."""
        predator = Predator(**self.valid_params)
        
        initial_mass = predator.get_total_mass()
        
        predator.capacity_penalty()  # Should not raise any exception
        
        self.assertEqual(predator.get_total_mass(), initial_mass)
    
    def test_capacity_penalty_with_plot_under_capacity(self):
        """Test capacity penalty when plot is under capacity for predators."""
        predator = Predator(**self.valid_params)
        
        initial_mass = predator.get_total_mass()
        
        self.mock_plot.over_predator_capacity = Mock(return_value=False)
        
        predator.capacity_penalty()
        
        self.assertEqual(predator.get_total_mass(), initial_mass)
    
    def test_capacity_penalty_multiple_calls(self):
        """Test that multiple calls to capacity penalty don't cause issues."""
        predator = Predator(**self.valid_params)
        
        # Set initial mass
        initial_mass = predator.get_total_mass()
        
        # Call capacity penalty multiple times
        predator.capacity_penalty()
        predator.capacity_penalty()
        predator.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(predator.get_total_mass(), initial_mass)
    
    def test_capacity_penalty_with_negative_mass(self):
        """Test capacity penalty when predator has negative mass (should be capped at 0)."""
        predator = Predator(**self.valid_params)
        
        # Set mass to negative value (should be capped at 0)
        predator.set_total_mass(-100.0)
        
        predator.capacity_penalty()
        
        # Mass should remain at 0 (capped)
        self.assertEqual(predator.get_total_mass(), 0.0)
    
    def test_capacity_penalty_with_high_mass(self):
        """Test capacity penalty when predator has very high mass."""
        predator = Predator(**self.valid_params)
        
        # Set mass to a very high value
        predator.set_total_mass(10000.0)
        
        predator.capacity_penalty()
        
        # Mass should remain unchanged since base implementation does nothing
        self.assertEqual(predator.get_total_mass(), 10000.0)
    
    def test_distance_from_ideal_ideal_value(self):
        """Test distance from ideal with ideal value."""
        predator = Predator(**self.valid_params)
        
        # Test with value at midpoint of ideal range
        result = predator.distance_from_ideal(15.0, (10.0, 20.0))
        self.assertEqual(result, 0.0)
    
    def test_distance_from_ideal_below_range(self):
        """Test distance from ideal with value below range."""
        predator = Predator(**self.valid_params)
        
        result = predator.distance_from_ideal(5.0, (10.0, 20.0))
        # Should be negative (penalty)
        self.assertLess(result, 0.0)
    
    def test_distance_from_ideal_above_range(self):
        """Test distance from ideal with value above range."""
        predator = Predator(**self.valid_params)
        
        result = predator.distance_from_ideal(25.0, (10.0, 20.0))
        # Should be negative (penalty)
        self.assertLess(result, 0.0)
    
    def test_distance_from_ideal_equal_min_max(self):
        """Test distance from ideal with equal min and max values."""
        predator = Predator(**self.valid_params)
        
        result = predator.distance_from_ideal(15.0, (15.0, 15.0))
        # Should return 0 to avoid division by zero
        self.assertEqual(result, 0.0)
    
    def test_distance_from_ideal_invalid_input(self):
        """Test distance from ideal with invalid input."""
        predator = Predator(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            predator.distance_from_ideal("not a float", (10.0, 20.0))
        self.assertIn("current_value must be an instance of float", str(context.exception))
        
        with self.assertRaises(TypeError) as context:
            predator.distance_from_ideal(15.0, "not a tuple")
        self.assertIn("ideal_range must be an instance of tuple", str(context.exception))


if __name__ == '__main__':
    unittest.main()
