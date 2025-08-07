import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the app directory to the path to handle imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

from app.models.Fauna.Prey import Prey
from app.models.Fauna.Fauna import Fauna
from app.interfaces.plot_info import PlotInformation


class TestPrey(unittest.TestCase):
    
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
            def over_prey_capacity(self) -> bool:
                return False
        
        self.mock_plot = MockPlot()
        
        class MockPredator(Fauna):
            def __init__(self, plot):
                super().__init__(
                    name="test_predator",
                    description="A test predator",
                    population=5,
                    avg_mass=100.0,
                    ideal_temp_range=(10.0, 25.0),
                    ideal_food_range=(50.0, 200.0),
                    ideal_growth_rate=0.1,
                    feeding_rate=2.0,
                    avg_steps_taken=10.0,
                    avg_feet_area=0.5,
                    plot=plot
                )
            
            def get_name(self):
                return "test_predator"
            
            def get_feeding_rate(self):
                return self.feeding_rate
        
        self.mock_predator = MockPredator(self.mock_plot)
        
        self.valid_params = {
            'name': "test_prey",
            'description': "A test prey species",
            'population': 20,
            'avg_mass': 50.0,
            'ideal_temp_range': (5.0, 20.0),
            'ideal_food_range': (10.0, 100.0),
            'ideal_growth_rate': 0.15,
            'feeding_rate': 1.5,
            'avg_steps_taken': 8.0,
            'avg_feet_area': 0.3,
            'plot': self.mock_plot,
            'predators': [self.mock_predator],
            'consumable_flora': []
        }
    
    def test_init_valid_parameters(self):
        """Test Prey initialization with valid parameters."""
        prey = Prey(**self.valid_params)
        
        self.assertEqual(prey.name, "test_prey")
        self.assertEqual(prey.description, "A test prey species")
        self.assertEqual(prey.population, 20)
        self.assertEqual(prey.avg_mass, 50.0)
        self.assertEqual(prey.ideal_temp_range, (5.0, 20.0))
        self.assertEqual(prey.ideal_food_range, (10.0, 100.0))
        self.assertEqual(prey.ideal_growth_rate, 0.15)
        self.assertEqual(prey.feeding_rate, 1.5)
        self.assertEqual(prey.avg_steps_taken, 8.0)
        self.assertEqual(prey.avg_feet_area, 0.3)
        self.assertEqual(prey.plot, self.mock_plot)
        self.assertEqual(prey.predators, [self.mock_predator])
        self.assertEqual(prey.consumable_flora, [])
    
    def test_init_invalid_predators_type(self):
        """Test Prey initialization with invalid predators type."""
        params = self.valid_params.copy()
        params['predators'] = "not a list"  # Invalid type
        
        with self.assertRaises(TypeError) as context:
            Prey(**params)
        self.assertIn("must be an instance of list", str(context.exception))
    
    def test_init_invalid_predators_element_type(self):
        """Test Prey initialization with invalid predators element type."""
        params = self.valid_params.copy()
        params['predators'] = ["not a Fauna object"]  # Invalid element type
        
        with self.assertRaises(ValueError) as context:
            Prey(**params)
        self.assertIn("must contain only Fauna objects", str(context.exception))
    
    def test_init_invalid_consumable_flora_type(self):
        """Test Prey initialization with invalid consumable_flora type."""
        params = self.valid_params.copy()
        params['consumable_flora'] = "not a list"  # Invalid type
        
        with self.assertRaises(TypeError) as context:
            Prey(**params)
        self.assertIn("must be an instance of list", str(context.exception))
    
    def test_init_invalid_consumable_flora_element_type(self):
        """Test Prey initialization with invalid consumable_flora element type."""
        params = self.valid_params.copy()
        params['consumable_flora'] = ["not a Flora object"]  # Invalid element type
        
        with self.assertRaises(ValueError) as context:
            Prey(**params)
        self.assertIn("must contain only Flora objects", str(context.exception))
    
    def test_total_consumption_rate_no_predators_on_plot(self):
        """Test total consumption rate when no predators are on the plot."""
        prey = Prey(**self.valid_params)
        
        # Mock plot to return empty fauna list
        self.mock_plot.get_all_fauna = Mock(return_value=[])
        
        result = prey.total_consumption_rate()
        self.assertEqual(result, 0.0)
    
    def test_total_consumption_rate_with_predators_on_plot(self):
        """Test total consumption rate when predators are on the plot."""
        prey = Prey(**self.valid_params)
        
        self.mock_plot.get_all_fauna = Mock(return_value=[self.mock_predator])
        
        result = prey.total_consumption_rate()
        # Expected: population * feeding_rate = 5 * 2.0 = 10.0
        self.assertEqual(result, 10.0)
    
    def test_total_consumption_rate_different_predators_on_plot(self):
        """Test total consumption rate when different predators are on the plot."""
        prey = Prey(**self.valid_params)
        
        # different predator that's not in prey's predator list
        class DifferentPredator(Fauna):
            def __init__(self, plot):
                super().__init__(
                    name="different_predator",
                    description="A different predator",
                    population=3,
                    avg_mass=80.0,
                    ideal_temp_range=(8.0, 22.0),
                    ideal_food_range=(40.0, 150.0),
                    ideal_growth_rate=0.08,
                    feeding_rate=1.8,
                    avg_steps_taken=12.0,
                    avg_feet_area=0.4,
                    plot=plot
                )
            
            def get_name(self):
                return "different_predator"
            
            def get_feeding_rate(self):
                return self.feeding_rate
        
        different_predator = DifferentPredator(self.mock_plot)
        
        self.mock_plot.get_all_fauna = Mock(return_value=[different_predator])
        
        result = prey.total_consumption_rate()
        # Should be 0.0
        self.assertEqual(result, 0.0)
    
    def test_total_available_flora_mass_no_flora_on_plot(self):
        """Test total available flora mass when no flora is on the plot."""
        prey = Prey(**self.valid_params)
        
        # Mock plot to return empty flora list
        self.mock_plot.get_all_flora = Mock(return_value=[])
        
        result = prey.total_available_flora_mass()
        self.assertEqual(result, 0.0)
    
    def test_total_available_flora_mass_with_flora_on_plot(self):
        """Test total available flora mass when flora is on the plot."""
        prey = Prey(**self.valid_params)
        
        mock_flora = Mock()
        mock_flora.get_name = Mock(return_value="grass")
        mock_flora.get_total_mass = Mock(return_value=100.0)
        
        # Add flora to prey's consumable_flora list
        prey.consumable_flora = [mock_flora]
        
        self.mock_plot.get_all_flora = Mock(return_value=[mock_flora])
        
        result = prey.total_available_flora_mass()
        self.assertEqual(result, 100.0)
    
    def test_total_available_flora_mass_different_flora_on_plot(self):
        """Test total available flora mass when different flora is on the plot."""
        prey = Prey(**self.valid_params)
        
        # Create mock flora that's not in prey's consumable_flora list
        mock_flora = Mock()
        mock_flora.get_name = Mock(return_value="different_grass")
        mock_flora.get_total_mass = Mock(return_value=150.0)
        
        self.mock_plot.get_all_flora = Mock(return_value=[mock_flora])
        
        result = prey.total_available_flora_mass()
        # Should be 0.0
        self.assertEqual(result, 0.0)
    
    def test_update_prey_mass_valid_day(self):
        """Test updating prey mass with valid day."""
        prey = Prey(**self.valid_params)
        
        prey._get_current_environmental_conditions = Mock(return_value={
            'temperature': 15.0,
            'food': 50.0
        })
        prey._calculate_environmental_penalty = Mock(return_value=-0.5)
        prey._calculate_base_growth_rate = Mock(return_value=0.075)
        prey.total_consumption_rate = Mock(return_value=5.0)
        prey._update_mass_from_growth_and_consumption = Mock()
        
        prey.update_prey_mass(1)
        
        # Verify the methods were called correctly
        prey._get_current_environmental_conditions.assert_called_once_with(1)
        prey._calculate_environmental_penalty.assert_called_once()
        prey._calculate_base_growth_rate.assert_called_once_with(-0.5)
        prey.total_consumption_rate.assert_called_once()
        prey._update_mass_from_growth_and_consumption.assert_called_once_with(0.075, 5.0)
    
    def test_update_prey_mass_invalid_day_type(self):
        """Test updating prey mass with invalid day type."""
        prey = Prey(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            prey.update_prey_mass("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_update_prey_mass_negative_day(self):
        """Test updating prey mass with negative day."""
        prey = Prey(**self.valid_params)
        
        with self.assertRaises(ValueError) as context:
            prey.update_prey_mass(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_environmental_conditions(self):
        """Test getting current environmental conditions."""
        prey = Prey(**self.valid_params)
        
        self.mock_plot.get_temperature = Mock(return_value=15.0)
        prey.total_available_flora_mass = Mock(return_value=75.0)
        
        result = prey._get_current_environmental_conditions(1)
        
        expected = {
            'temperature': 15.0,
            'food': 75.0
        }
        self.assertEqual(result, expected)
        self.mock_plot.get_temperature.assert_called_once_with(1)
        prey.total_available_flora_mass.assert_called_once()
    
    def test_calculate_environmental_penalty_ideal_conditions(self):
        """Test environmental penalty calculation with ideal conditions."""
        prey = Prey(**self.valid_params)
        
        environmental_conditions = {
            'temperature': 12.5,  # Midpoint of ideal range (5.0, 20.0)
            'food': 55.0          # Midpoint of ideal range (10.0, 100.0)
        }
        
        result = prey._calculate_environmental_penalty(environmental_conditions)
        
        # Both conditions are ideal, so penalty should be 0
        self.assertEqual(result, 0.0)
    
    def test_calculate_environmental_penalty_poor_conditions(self):
        """Test environmental penalty calculation with poor conditions."""
        prey = Prey(**self.valid_params)
        
        environmental_conditions = {
            'temperature': 30.0,  # Far above ideal range
            'food': 5.0           # Far below ideal range
        }
        
        result = prey._calculate_environmental_penalty(environmental_conditions)
        
        # Both conditions are not ideal, so penalty should be negative
        self.assertLess(result, 0.0)
    
    def test_calculate_environmental_penalty_invalid_input(self):
        """Test environmental penalty calculation with invalid input."""
        prey = Prey(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            prey._calculate_environmental_penalty("not a dict")
        self.assertIn("environmental_conditions must be an instance of dict", str(context.exception))
    
    def test_calculate_base_growth_rate(self):
        """Test base growth rate calculation."""
        prey = Prey(**self.valid_params)
        
        environmental_penalty = -0.5
        result = prey._calculate_base_growth_rate(environmental_penalty)
        
        # Expected: ideal_growth_rate * (1 + penalty) = 0.15 * (1 + (-0.5)) = 0.075
        expected = 0.075
        self.assertEqual(result, expected)
    
    def test_calculate_base_growth_rate_invalid_input(self):
        """Test base growth rate calculation with invalid input."""
        prey = Prey(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            prey._calculate_base_growth_rate("not a float")
        self.assertIn("environmental_penalty must be an instance of float", str(context.exception))
    
    def test_update_mass_from_growth_and_consumption(self):
        """Test updating mass from growth and consumption."""
        prey = Prey(**self.valid_params)
        
        prey.set_total_mass(1000.0) # initial mass
        
        base_growth_rate = 0.1
        consumption_rate = 5.0
        
        prey._update_mass_from_growth_and_consumption(base_growth_rate, consumption_rate)
        
        # Expected: new_mass = 1000 + 1000 * (0.1 - 5.0) = 1000 + 1000 * (-4.9) = -3900
        # But mass is capped at 0, so should be 0
        self.assertEqual(prey.get_total_mass(), 0.0)
    
    def test_update_mass_from_growth_and_consumption_invalid_input(self):
        """Test updating mass with invalid input."""
        prey = Prey(**self.valid_params)
        
        with self.assertRaises(TypeError) as context:
            prey._update_mass_from_growth_and_consumption("not a float", 5.0)
        self.assertIn("base_growth_rate must be an instance of float", str(context.exception))
        
        with self.assertRaises(TypeError) as context:
            prey._update_mass_from_growth_and_consumption(0.1, "not a float")
        self.assertIn("consumption_rate must be an instance of float", str(context.exception))
    
    def test_capacity_penalty_with_plot_over_capacity(self):
        """Test capacity penalty when plot is over capacity for prey."""
        prey = Prey(**self.valid_params)
        
        initial_mass = prey.get_total_mass()
        
        self.mock_plot.over_prey_capacity = Mock(return_value=True)
        
        prey.capacity_penalty()
        
        # Mass should be reduced by 10%
        expected_mass = initial_mass * 0.9
        self.assertEqual(prey.get_total_mass(), expected_mass)
    
    def test_capacity_penalty_with_plot_under_capacity(self):
        """Test capacity penalty when plot is under capacity for prey."""
        prey = Prey(**self.valid_params)
        
        initial_mass = prey.get_total_mass()
        
        self.mock_plot.over_prey_capacity = Mock(return_value=False)
        
        prey.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(prey.get_total_mass(), initial_mass)
    
    def test_capacity_penalty_multiple_calls(self):
        """Test that multiple calls to capacity penalty don't cause issues."""
        prey = Prey(**self.valid_params)
        
        initial_mass = prey.get_total_mass()
        
        prey.capacity_penalty()
        prey.capacity_penalty()
        prey.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(prey.get_total_mass(), initial_mass)
    
    def test_capacity_penalty_with_zero_mass(self):
        """Test capacity penalty when prey has zero mass."""
        prey = Prey(**self.valid_params)
        
        prey.set_total_mass(0.0)
        
        prey.capacity_penalty()
        
        # Mass should remain zero
        self.assertEqual(prey.get_total_mass(), 0.0)
    
    def test_capacity_penalty_with_negative_mass(self):
        """Test capacity penalty when prey has negative mass (should be capped at 0)."""
        prey = Prey(**self.valid_params)
        
        # Set mass to negative value (should be capped at 0)
        prey.set_total_mass(-100.0)
        
        prey.capacity_penalty()
        
        # Mass should remain at 0 (capped)
        self.assertEqual(prey.get_total_mass(), 0.0)


if __name__ == '__main__':
    unittest.main()
