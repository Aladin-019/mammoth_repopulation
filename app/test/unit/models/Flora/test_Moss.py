import unittest
from unittest.mock import Mock
import sys
import os

# Add the app directory to the path to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Import directly from the modules to avoid circular imports
from app.models.Flora.Moss import Moss
from app.models.Fauna.Fauna import Fauna
from app.interfaces.flora_plot_info import FloraPlotInformation


class TestMoss(unittest.TestCase):
    """Test cases for the Moss class."""
    
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
            'name': 'Test Moss',
            'description': 'A test moss species',
            'total_mass': 100.0,
            'population': 50,
            'ideal_growth_rate': 5.0,
            'ideal_temp_range': (10.0, 30.0),
            'ideal_uv_range': (1.0, 10.0),
            'ideal_hydration_range': (5.0, 20.0),
            'ideal_soil_temp_range': (5.0, 25.0),
            'consumers': [self.mock_fauna],
            'root_depth': 1,
            'plot': self.mock_plot
        }
        
        self.moss = Moss(**self.valid_params)
    
    def test_init_valid_parameters(self):
        """Test Moss initialization with valid parameters."""
        moss = Moss(**self.valid_params)
        
        # Test that all parameters are set correctly
        self.assertEqual(moss.name, 'Test Moss')
        self.assertEqual(moss.description, 'A test moss species')
        self.assertEqual(moss.total_mass, 100.0)
        self.assertEqual(moss.ideal_growth_rate, 5.0)
        self.assertEqual(moss.ideal_temp_range, (10.0, 30.0))
        self.assertEqual(moss.ideal_uv_range, (1.0, 10.0))
        self.assertEqual(moss.ideal_hydration_range, (5.0, 20.0))
        self.assertEqual(moss.ideal_soil_temp_range, (5.0, 25.0))
        self.assertEqual(moss.consumers, [self.mock_fauna])
        self.assertEqual(moss.plot, self.mock_plot)
    
    def test_update_flora_mass_valid_day(self):
        """Test update_flora_mass with valid day parameter."""
        initial_mass = self.moss.total_mass
        self.moss.update_flora_mass(day=1)
        
        # Mass should have changed due to environmental conditions
        self.assertNotEqual(self.moss.total_mass, initial_mass)
    
    def test_update_flora_mass_invalid_day_type(self):
        """Test update_flora_mass with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.moss.update_flora_mass(day="invalid")
        self.assertIn("must be an instance of int", str(context.exception))
    
    def test_update_flora_mass_negative_day(self):
        """Test update_flora_mass with negative day."""
        with self.assertRaises(ValueError) as context:
            self.moss.update_flora_mass(day=-1)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_update_flora_mass_zero_day(self):
        """Test update_flora_mass with zero day (should be valid)."""
        initial_mass = self.moss.total_mass
        self.moss.update_flora_mass(day=0)
        
        # Should work without error
        self.assertNotEqual(self.moss.total_mass, initial_mass)
    
    def test_capacity_penalty_no_over_capacity(self):
        """Test capacity_penalty when not over moss capacity."""
        class MockPlotNoOverCapacity(FloraPlotInformation):
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
            def over_moss_capacity(self) -> bool:
                return False
        
        mock_plot_no_over = MockPlotNoOverCapacity()
        moss_no_over = Moss(**{**self.valid_params, 'plot': mock_plot_no_over})
        
        initial_mass = moss_no_over.total_mass
        moss_no_over.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(moss_no_over.total_mass, initial_mass)
    
    def test_capacity_penalty_over_capacity(self):
        """Test capacity_penalty when over moss capacity."""
        class MockPlotOverCapacity(FloraPlotInformation):
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
            def over_moss_capacity(self) -> bool:
                return True
        
        mock_plot_over = MockPlotOverCapacity()
        moss_over = Moss(**{**self.valid_params, 'plot': mock_plot_over})
        
        initial_mass = moss_over.total_mass
        moss_over.capacity_penalty()
        
        # Mass should be reduced by 10%
        expected_mass = initial_mass * 0.9
        self.assertEqual(moss_over.total_mass, expected_mass)
    
    def test_capacity_penalty_none_plot(self):
        """Test capacity_penalty with None plot."""
        moss_none_plot = Moss(**self.valid_params)
        moss_none_plot.plot = None
        
        with self.assertRaises(ValueError) as context:
            moss_none_plot.capacity_penalty()
        self.assertIn("must be provided", str(context.exception))
    
    def test_inherited_methods(self):
        """Test that Moss inherits and can use Flora methods."""
        self.assertEqual(self.moss.get_name(), 'Test Moss')
        self.assertEqual(self.moss.get_description(), 'A test moss species')
        self.assertEqual(self.moss.get_total_mass(), 100.0)

        conditions = self.moss._get_current_environmental_conditions(day=1)
        self.assertIsInstance(conditions, dict)
        self.assertIn('temperature', conditions)
        self.assertIn('uv', conditions)
        self.assertIn('hydration', conditions)
        self.assertIn('soil_temperature', conditions)
    
    def test_moss_specific_behavior(self):
        """Test that moss applies canopy shading."""
        conditions = {
            'temperature': 20.0,
            'uv': 10.0,
            'hydration': 15.0,
            'soil_temperature': 15.0
        }
        
        shaded_conditions = self.moss._apply_canopy_shading(conditions)
        
        # UV should be reduced by canopy shading
        self.assertLessEqual(shaded_conditions['uv'], conditions['uv'])
        
        # Other conditions should remain the same
        self.assertEqual(shaded_conditions['temperature'], conditions['temperature'])
        self.assertEqual(shaded_conditions['hydration'], conditions['hydration'])
        self.assertEqual(shaded_conditions['soil_temperature'], conditions['soil_temperature'])
    
    def test_moss_mass_update_with_canopy(self):
        """Test that moss mass updates consider canopy shading."""
        mock_tree = Mock()
        mock_tree.get_Tree_canopy_cover.return_value = 5.0
        
        class MockPlotWithTree(FloraPlotInformation):
            def get_current_temperature(self, day: int) -> float:
                return 20.0
            def get_current_uv(self, day: int) -> float:
                return 10.0  # High UV
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
        
        mock_plot_with_tree = MockPlotWithTree()
        moss_with_tree = Moss(**{**self.valid_params, 'plot': mock_plot_with_tree})
        
        initial_mass = moss_with_tree.total_mass
        moss_with_tree.update_flora_mass(day=1)
        
        # should change due to canopy shading effect
        self.assertNotEqual(moss_with_tree.total_mass, initial_mass)


if __name__ == '__main__':
    unittest.main() 