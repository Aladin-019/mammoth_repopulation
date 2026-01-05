import unittest
from unittest.mock import Mock
import sys
import os

# Add the app directory to the path to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

# Import directly from the modules to avoid circular imports
from app.models.Flora.Tree import Tree
from app.models.Fauna.Fauna import Fauna
from app.interfaces.flora_plot_info import FloraPlotInformation


class TestTree(unittest.TestCase):
    """Test cases for the Tree class."""
    
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
            def over_tree_capacity(self) -> bool:
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
            'name': 'Test Tree',
            'description': 'some test tree species',
            'avg_mass': 10.0,  # 100.0 total_mass / 10 population = 10.0 avg_mass
            'population': 10,
            'ideal_growth_rate': 5.0,
            'ideal_temp_range': (10.0, 30.0),
            'ideal_uv_range': (1.0, 10.0),
            'ideal_hydration_range': (5.0, 20.0),
            'ideal_soil_temp_range': (5.0, 25.0),
            'consumers': [self.mock_fauna],
            'root_depth': 3,
            'plot': self.mock_plot,
            'single_tree_canopy_cover': 15.0,
            'coniferous': True
        }
        
        self.tree = Tree(**self.valid_params)
    
    def test_init_valid_parameters(self):
        """Test Tree initialization with valid parameters."""
        tree = Tree(**self.valid_params)
        
        # Test that all parameters are set correctly
        self.assertEqual(tree.name, 'Test Tree')
        self.assertEqual(tree.description, 'some test tree species')
        self.assertEqual(tree.total_mass, 100.0)
        self.assertEqual(tree.ideal_growth_rate, 5.0)
        self.assertEqual(tree.ideal_temp_range, (10.0, 30.0))
        self.assertEqual(tree.ideal_uv_range, (1.0, 10.0))
        self.assertEqual(tree.ideal_hydration_range, (5.0, 20.0))
        self.assertEqual(tree.ideal_soil_temp_range, (5.0, 25.0))
        self.assertEqual(tree.consumers, [self.mock_fauna])
        self.assertEqual(tree.plot, self.mock_plot)
        self.assertEqual(tree.single_tree_canopy_cover, 15.0)
        self.assertEqual(tree.coniferous, True)
    
    def test_init_invalid_single_tree_canopy_cover(self):
        """Test Tree initialization with invalid single_tree_canopy_cover."""
        params = self.valid_params.copy()
        params['single_tree_canopy_cover'] = -1.0  # Negative canopy cover
        
        with self.assertRaises(ValueError) as context:
            Tree(**params)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_init_invalid_single_tree_canopy_cover_type(self):
        """Test Tree initialization with invalid single_tree_canopy_cover type."""
        params = self.valid_params.copy()
        params['single_tree_canopy_cover'] = "not a float"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Tree(**params)
        self.assertIn("must be an instance of float", str(context.exception))
    
    def test_init_invalid_coniferous_type(self):
        """Test Tree initialization with invalid coniferous type."""
        params = self.valid_params.copy()
        params['coniferous'] = "not a bool"  # Wrong type
        
        with self.assertRaises(TypeError) as context:
            Tree(**params)
        self.assertIn("must be an instance of bool", str(context.exception))
    
    def test_update_flora_mass_valid_day(self):
        """Test update_flora_mass with valid day parameter."""
        initial_mass = self.tree.total_mass
        self.tree.update_flora_mass(day=1)
        
        # Mass should have changed due to environmental conditions
        self.assertNotEqual(self.tree.total_mass, initial_mass)
    
    def test_update_flora_mass_invalid_day_type(self):
        """Test update_flora_mass with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.tree.update_flora_mass(day="invalid")
        self.assertIn("must be an instance of int", str(context.exception))
    
    def test_update_flora_mass_negative_day(self):
        """Test update_flora_mass with negative day."""
        with self.assertRaises(ValueError) as context:
            self.tree.update_flora_mass(day=-1)
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_update_flora_mass_zero_day(self):
        """Test update_flora_mass with zero day (should be valid)."""
        initial_mass = self.tree.total_mass
        self.tree.update_flora_mass(day=0)
        
        # Should work without error
        self.assertNotEqual(self.tree.total_mass, initial_mass)
    
    def test_get_tree_canopy_cover(self):
        """Test get_Tree_canopy_cover method."""
        # Test with default parameters
        expected_canopy = 10 * 15.0  # population * single_tree_canopy_cover
        self.assertEqual(self.tree.get_Tree_canopy_cover(), expected_canopy)
        
        # Test with different population
        tree_different_pop = Tree(**{**self.valid_params, 'population': 5})
        expected_canopy = 5 * 15.0
        self.assertEqual(tree_different_pop.get_Tree_canopy_cover(), expected_canopy)
        
        # Test with different canopy cover
        tree_different_canopy = Tree(**{**self.valid_params, 'single_tree_canopy_cover': 20.0})
        expected_canopy = 10 * 20.0
        self.assertEqual(tree_different_canopy.get_Tree_canopy_cover(), expected_canopy)
    
    def test_capacity_penalty_no_over_capacity(self):
        """Test capacity_penalty when not over tree capacity."""
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
            def over_tree_capacity(self) -> bool:
                return False
        
        mock_plot_no_over = MockPlotNoOverCapacity()
        tree_no_over = Tree(**{**self.valid_params, 'plot': mock_plot_no_over})
        
        initial_mass = tree_no_over.total_mass
        tree_no_over.capacity_penalty()
        
        # Mass should remain unchanged
        self.assertEqual(tree_no_over.total_mass, initial_mass)
    
    def test_capacity_penalty_over_capacity(self):
        """Test capacity_penalty when over tree capacity."""
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
            def over_tree_capacity(self) -> bool:
                return True
        
        mock_plot_over = MockPlotOverCapacity()
        tree_over = Tree(**{**self.valid_params, 'plot': mock_plot_over})
        
        initial_mass = tree_over.total_mass
        tree_over.capacity_penalty()
        
        # Mass should be reduced by 10%
        expected_mass = initial_mass * 0.9
        self.assertEqual(tree_over.total_mass, expected_mass)
    
    def test_capacity_penalty_none_plot(self):
        """Test capacity_penalty with None plot."""
        tree_none_plot = Tree(**self.valid_params)
        tree_none_plot.plot = None
        
        with self.assertRaises(ValueError) as context:
            tree_none_plot.capacity_penalty()
        self.assertIn("must be provided", str(context.exception))
    
    def test_inherited_methods(self):
        """Test that Tree inherits and can use Flora methods."""
        self.assertEqual(self.tree.get_name(), 'Test Tree')
        self.assertEqual(self.tree.get_description(), 'some test tree species')
        self.assertEqual(self.tree.get_total_mass(), 100.0)

        conditions = self.tree._get_current_environmental_conditions(day=1)
        self.assertIsInstance(conditions, dict)
        self.assertIn('temperature', conditions)
        self.assertIn('uv', conditions)
        self.assertIn('hydration', conditions)
        self.assertIn('soil_temperature', conditions)
    
    def test_coniferous_and_deciduous_trees(self):
        """Test coniferous and deciduous tree types."""
        # Test coniferous tree (default)
        coniferous_tree = Tree(**self.valid_params)
        self.assertTrue(coniferous_tree.coniferous)
        
        # Test deciduous tree
        deciduous_tree = Tree(**{**self.valid_params, 'coniferous': False})
        self.assertFalse(deciduous_tree.coniferous)
    
    def test_single_tree_canopy_cover_validation(self):
        """Test single_tree_canopy_cover validation."""
        # Test valid canopy covers
        valid_covers = [0.1, 1.0, 5.0, 10.0, 50.0]
        for cover in valid_covers:
            params = self.valid_params.copy()
            params['single_tree_canopy_cover'] = cover
            tree = Tree(**params)
            self.assertEqual(tree.single_tree_canopy_cover, cover)
        
        # Test invalid canopy covers
        invalid_covers = [-1.0, -0.5]
        for cover in invalid_covers:
            params = self.valid_params.copy()
            params['single_tree_canopy_cover'] = cover
            with self.assertRaises(ValueError) as context:
                Tree(**params)
            self.assertIn("must be non-negative", str(context.exception))
    
    def test_tree_specific_behavior(self):
        """Test tree-specific behavior like canopy cover calculation."""
        # Test that canopy cover is calculated correctly
        expected_canopy = self.tree.population * self.tree.single_tree_canopy_cover
        self.assertEqual(self.tree.get_Tree_canopy_cover(), expected_canopy)
        
        # Test that trees can provide canopy cover for other flora
        self.assertGreater(self.tree.get_Tree_canopy_cover(), 0.0)
    
    def test_tree_mass_update(self):
        """Test that tree mass updates work correctly."""
        initial_mass = self.tree.total_mass
        self.tree.update_flora_mass(day=1)
        
        # Mass should change due to environmental conditions
        self.assertNotEqual(self.tree.total_mass, initial_mass)
        
        # Mass should not go negative
        self.assertGreaterEqual(self.tree.total_mass, 0.0)


if __name__ == '__main__':
    unittest.main() 