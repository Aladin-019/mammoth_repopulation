import unittest
from unittest.mock import Mock
import sys
import os

# Add the app directory to the path to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Import directly from the modules to avoid circular imports
from app.models.Flora.Shrub import Shrub
from app.models.Fauna.Fauna import Fauna
from app.interfaces.flora_plot_info import FloraPlotInformation


class TestShrub(unittest.TestCase):
    """Test cases for the Shrub class."""
    
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
            def get_area_trampled_ratio(self) -> float:
                return 0.1  # 10% trampled
            def over_shrub_capacity(self) -> bool:
                return False
        
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
            'name': 'Test Shrub',
            'description': 'some test shrub species',
            'avg_mass': 2.0,  # 100.0 total_mass / 50 population = 2.0 avg_mass
            'population': 50,
            'ideal_growth_rate': 5.0,
            'ideal_temp_range': (10.0, 30.0),
            'ideal_uv_range': (1.0, 10.0),
            'ideal_hydration_range': (5.0, 20.0),
            'ideal_soil_temp_range': (5.0, 25.0),
            'consumers': [self.mock_fauna],
            'root_depth': 2,
            'plot': self.mock_plot,
            'shrub_area': 2.0
        }
        
        self.shrub = Shrub(**self.valid_params)
    
    def test_init_valid_parameters(self):
        """Test Shrub initialization with valid parameters."""
        shrub = Shrub(**self.valid_params)
        
        # Test that all parameters are set correctly
        self.assertEqual(shrub.name, 'Test Shrub')
        self.assertEqual(shrub.description, 'some test shrub species')
        self.assertEqual(shrub.total_mass, 100.0)
        self.assertEqual(shrub.ideal_growth_rate, 5.0)
        self.assertEqual(shrub.ideal_temp_range, (10.0, 30.0))
        self.assertEqual(shrub.ideal_uv_range, (1.0, 10.0))
        self.assertEqual(shrub.ideal_hydration_range, (5.0, 20.0))
        self.assertEqual(shrub.ideal_soil_temp_range, (5.0, 25.0))
        self.assertEqual(shrub.consumers, [self.mock_fauna])
        self.assertEqual(shrub.plot, self.mock_plot)
        self.assertEqual(shrub.shrub_area, 2.0)
    
    def test_init_invalid_shrub_area(self):
        """Test Shrub initialization with invalid shrub_area."""
        params = self.valid_params.copy()
        params['shrub_area'] = -1.0  # Negative area
        
        with self.assertRaises(ValueError) as context:
            Shrub(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_update_flora_mass_valid_day(self):
        """Test update_flora_mass with valid day parameter."""
        initial_mass = self.shrub.total_mass
        self.shrub.update_flora_mass(day=1)
        
        # Mass should have changed due to environmental conditions and trampling
        self.assertNotEqual(self.shrub.total_mass, initial_mass)
    
    def test_update_flora_mass_invalid_day_type(self):
        """Test update_flora_mass with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.shrub.update_flora_mass(day="invalid")
        self.assertIn("must be an instance of int", str(context.exception))
    
    def test_update_flora_mass_negative_day(self):
        """Test update_flora_mass with negative day."""
        with self.assertRaises(ValueError) as context:
            self.shrub.update_flora_mass(day=-1)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_update_flora_mass_zero_day(self):
        """Test update_flora_mass with zero day (should be valid)."""
        initial_mass = self.shrub.total_mass
        self.shrub.update_flora_mass(day=0)
        
        # Should work without error
        self.assertNotEqual(self.shrub.total_mass, initial_mass)
    
    def test_apply_trampling_reduction(self):
        """Test _apply_trampling_reduction method."""
        initial_mass = self.shrub.total_mass
        initial_population = self.shrub.population
        
        self.shrub._apply_trampling_reduction()
        
        # Mass and population should be reduced due to trampling
        self.assertLess(self.shrub.total_mass, initial_mass)
        self.assertLessEqual(self.shrub.population, initial_population)
    
    def test_apply_trampling_reduction_none_plot(self):
        """Test _apply_trampling_reduction with None plot."""
        shrub_none_plot = Shrub(**self.valid_params)
        shrub_none_plot.plot = None
        
        with self.assertRaises(ValueError) as context:
            shrub_none_plot._apply_trampling_reduction()
        self.assertIn("must be provided", str(context.exception))
    
    def test_apply_trampling_reduction_no_trampling(self):
        """Test _apply_trampling_reduction with no trampling."""
        class MockPlotNoTrampling(FloraPlotInformation):
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
            def get_area_trampled_ratio(self) -> float:
                return 0.0  # No trampling
            def over_shrub_capacity(self) -> bool:
                return False
        
        mock_plot_no_trampling = MockPlotNoTrampling()
        shrub_no_trampling = Shrub(**{**self.valid_params, 'plot': mock_plot_no_trampling})
        
        initial_mass = shrub_no_trampling.total_mass
        initial_population = shrub_no_trampling.population
        
        shrub_no_trampling._apply_trampling_reduction()
        
        # Mass and population should remain unchanged
        self.assertEqual(shrub_no_trampling.total_mass, initial_mass)
        self.assertEqual(shrub_no_trampling.population, initial_population)
    
    def test_capacity_penalty_no_over_capacity(self):
        """Test capacity_penalty when not over shrub capacity."""
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
            def get_area_trampled_ratio(self) -> float:
                return 0.1
            def over_shrub_capacity(self) -> bool:
                return False
        
        mock_plot_no_over = MockPlotNoOverCapacity()
        shrub_no_over = Shrub(**{**self.valid_params, 'plot': mock_plot_no_over})
        
        initial_mass = shrub_no_over.total_mass
        shrub_no_over.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(shrub_no_over.total_mass, initial_mass)
    
    def test_capacity_penalty_over_capacity(self):
        """Test capacity_penalty when over shrub capacity."""
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
            def get_area_trampled_ratio(self) -> float:
                return 0.1
            def over_shrub_capacity(self) -> bool:
                return True
        
        mock_plot_over = MockPlotOverCapacity()
        shrub_over = Shrub(**{**self.valid_params, 'plot': mock_plot_over})
        
        initial_mass = shrub_over.total_mass
        shrub_over.capacity_penalty()
        
        # Mass should be reduced by 10%
        expected_mass = initial_mass * 0.9
        self.assertEqual(shrub_over.total_mass, expected_mass)
    
    def test_capacity_penalty_none_plot(self):
        """Test capacity_penalty with None plot."""
        shrub_none_plot = Shrub(**self.valid_params)
        shrub_none_plot.plot = None
        
        with self.assertRaises(ValueError) as context:
            shrub_none_plot.capacity_penalty()
        self.assertIn("must be provided", str(context.exception))
    
    def test_inherited_methods(self):
        """Test that Shrub inherits and can use Flora methods."""
        self.assertEqual(self.shrub.get_name(), 'Test Shrub')
        self.assertEqual(self.shrub.get_description(), 'some test shrub species')
        self.assertEqual(self.shrub.get_total_mass(), 100.0)

        conditions = self.shrub._get_current_environmental_conditions(day=1)
        self.assertIsInstance(conditions, dict)
        self.assertIn('temperature', conditions)
        self.assertIn('uv', conditions)
        self.assertIn('hydration', conditions)
        # Shrub has root_depth=2, so it doesn't include soil_temperature
        self.assertNotIn('soil_temperature', conditions)
    
    def test_shrub_specific_behavior(self):
        """Test that shrub applies canopy shading."""
        conditions = {
            'temperature': 20.0,
            'uv': 10.0,
            'hydration': 15.0,
            'soil_temperature': 15.0
        }
        
        shaded_conditions = self.shrub._apply_canopy_shading(conditions)
        
        # UV should be reduced by canopy shading
        self.assertLessEqual(shaded_conditions['uv'], conditions['uv'])
        
        # Other conditions should remain the same
        self.assertEqual(shaded_conditions['temperature'], conditions['temperature'])
        self.assertEqual(shaded_conditions['hydration'], conditions['hydration'])
        self.assertEqual(shaded_conditions['soil_temperature'], conditions['soil_temperature'])
    
    def test_shrub_mass_update_with_canopy_and_trampling(self):
        """Test that shrub mass updates consider both canopy shading and trampling."""
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
            def get_area_trampled_ratio(self) -> float:
                return 0.2  # 20% trampled
            def over_shrub_capacity(self) -> bool:
                return False
        
        mock_plot_with_tree = MockPlotWithTree()
        shrub_with_tree = Shrub(**{**self.valid_params, 'plot': mock_plot_with_tree})
        
        initial_mass = shrub_with_tree.total_mass
        shrub_with_tree.update_flora_mass(day=1)
        
        # should change due to canopy shading and trampling effects
        self.assertNotEqual(shrub_with_tree.total_mass, initial_mass)
    
    def test_stomping_rate_class_variable(self):
        """Test that STOMPING_RATE class variable is accessible."""
        self.assertEqual(Shrub.STOMPING_RATE, 0.08)
    
    def test_shrub_area_validation(self):
        """Test shrub_area validation."""
        # Test valid shrub_area
        valid_areas = [0.1, 1.0, 5.0, 10.0]
        for area in valid_areas:
            params = self.valid_params.copy()
            params['shrub_area'] = area
            shrub = Shrub(**params)
            self.assertEqual(shrub.shrub_area, area)
        
        # Test invalid shrub_area
        invalid_areas = [-1.0, -0.5]
        for area in invalid_areas:
            params = self.valid_params.copy()
            params['shrub_area'] = area
            with self.assertRaises(ValueError) as context:
                Shrub(**params)
            self.assertIn("must be non-negative", str(context.exception))


if __name__ == '__main__':
    unittest.main() 