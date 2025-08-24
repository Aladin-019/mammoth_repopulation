import unittest
from unittest.mock import Mock, patch
from app.models.Plot.Plot import Plot
from app.models import Fauna, Climate
from app.models.Fauna import Prey, Predator


class TestPlot(unittest.TestCase):
    
    def setUp(self):
        """Fixtures before each test method."""
        self.mock_climate = Mock()
        self.mock_climate._get_current_temperature.return_value = 15.0
        self.mock_climate._get_current_soil_temp.return_value = 8.0
        self.mock_climate._get_current_snowfall.return_value = 0.1
        self.mock_climate._get_current_rainfall.return_value = 5.0
        self.mock_climate._get_current_uv.return_value = 3.0
        self.mock_climate._get_current_SSRD.return_value = 1000.0
        self.mock_climate.__class__.__name__ = "Climate"
        
        self.mock_plot = Mock()
        
        self.plot = Plot(
            Id=1,
            avg_snow_height=0.5,
            climate=self.mock_climate,
            plot_area=1.0
        )
    
    def test_init_valid_parameters(self):
        """Test Plot initialization with valid parameters."""
        plot = Plot(
            Id=1,
            avg_snow_height=0.5,
            climate=self.mock_climate,
            plot_area=1.0
        )
        
        self.assertEqual(plot.Id, 1)
        self.assertEqual(plot.avg_snow_height, 0.5)
        self.assertEqual(plot.climate, self.mock_climate)
        self.assertEqual(plot.plot_area, 1.0)
        self.assertEqual(plot.compaction_depth, 0.7)
        self.assertEqual(plot.previous_avg_snow_height, 0.5)
        self.assertEqual(len(plot.flora), 0)
        self.assertEqual(len(plot.fauna), 0)
    
    def test_init_invalid_id_type(self):
        """Test Plot initialization with invalid ID type."""
        with self.assertRaises(TypeError) as context:
            Plot(
                Id="1",  # Should be int
                avg_snow_height=0.5,
                climate=self.mock_climate,
                plot_area=1.0
            )
        self.assertIn("Id must be an instance of int", str(context.exception))
    
    def test_init_negative_id(self):
        """Test Plot initialization with negative ID."""
        with self.assertRaises(ValueError) as context:
            Plot(
                Id=-1,
                avg_snow_height=0.5,
                climate=self.mock_climate,
                plot_area=1.0
            )
        self.assertIn("Id must be non-negative", str(context.exception))
    
    def test_init_invalid_snow_height_type(self):
        """Test Plot initialization with invalid snow height type."""
        with self.assertRaises(TypeError) as context:
            Plot(
                Id=1,
                avg_snow_height="0.5",  # Should be float
                climate=self.mock_climate,
                plot_area=1.0
            )
        self.assertIn("avg_snow_height must be an instance of float", str(context.exception))
    
    def test_init_negative_snow_height(self):
        """Test Plot initialization with negative snow height."""
        with self.assertRaises(ValueError) as context:
            Plot(
                Id=1,
                avg_snow_height=-0.5,
                climate=self.mock_climate,
                plot_area=1.0
            )
        self.assertIn("avg_snow_height must be non-negative", str(context.exception))
    
    def test_init_zero_snow_height_allowed(self):
        """Test Plot initialization with zero snow height (should be allowed)."""
        plot = Plot(
            Id=1,
            avg_snow_height=0.0,
            climate=self.mock_climate,
            plot_area=1.0
        )
        self.assertEqual(plot.avg_snow_height, 0.0)
    
    def test_init_invalid_climate_type(self):
        """Test Plot initialization with invalid climate type."""
        with self.assertRaises(TypeError) as context:
            Plot(
                Id=1,
                avg_snow_height=0.5,
                climate="not_a_climate",  # Should be Climate
                plot_area=1.0
            )
        self.assertIn("climate must be an instance of Climate", str(context.exception))
    
    def test_init_none_climate(self):
        """Test Plot initialization with None climate."""
        with self.assertRaises(TypeError) as context:
            Plot(
                Id=1,
                avg_snow_height=0.5,
                climate=None,
                plot_area=1.0
            )
        self.assertIn("climate must be an instance of Climate", str(context.exception))
    
    def test_init_invalid_plot_area_type(self):
        """Test Plot initialization with invalid plot area type."""
        with self.assertRaises(TypeError) as context:
            Plot(
                Id=1,
                avg_snow_height=0.5,
                climate=self.mock_climate,
                plot_area="1.0"  # Should be float
            )
        self.assertIn("plot_area must be an instance of float", str(context.exception))
    
    def test_init_zero_plot_area_not_allowed(self):
        """Test Plot initialization with zero plot area (should not be allowed)."""
        with self.assertRaises(ValueError) as context:
            Plot(
                Id=1,
                avg_snow_height=0.5,
                climate=self.mock_climate,
                plot_area=0.0
            )
        self.assertIn("plot_area must be positive", str(context.exception))
    
    def test_init_negative_plot_area(self):
        """Test Plot initialization with negative plot area."""
        with self.assertRaises(ValueError) as context:
            Plot(
                Id=1,
                avg_snow_height=0.5,
                climate=self.mock_climate,
                plot_area=-1.0
            )
        self.assertIn("plot_area must be positive", str(context.exception))
    
    def test_add_flora_valid(self):
        """Test adding valid flora to plot."""
        mock_flora = Mock()
        mock_flora.name = "grass"
        mock_flora.__class__.__name__ = "Flora"
        
        self.plot.add_flora(mock_flora)
        
        self.assertEqual(len(self.plot.flora), 1)
        self.assertIn(mock_flora, self.plot.flora)

    def test_add_flora_none(self):
        """Test adding None flora to plot."""
        with self.assertRaises(ValueError) as context:
            self.plot.add_flora(None)
        self.assertIn("flora cannot be None", str(context.exception))
    
    def test_add_flora_invalid_type(self):
        """Test adding invalid flora type to plot."""
        with self.assertRaises(TypeError) as context:
            self.plot.add_flora("not_flora")
        self.assertIn("flora must be an instance of Flora", str(context.exception))
    
    def test_add_fauna_valid(self):
        """Test adding valid fauna to plot."""
        mock_fauna = Mock()
        mock_fauna.name = "mammoth"
        mock_fauna.__class__.__name__ = "Fauna"  # Set class name for validation
        
        self.plot.add_fauna(mock_fauna)
        
        self.assertEqual(len(self.plot.fauna), 1)
        self.assertIn(mock_fauna, self.plot.fauna)

    def test_add_fauna_none(self):
        """Test adding None fauna to plot."""
        with self.assertRaises(ValueError) as context:
            self.plot.add_fauna(None)
        self.assertIn("fauna cannot be None", str(context.exception))
    
    def test_add_fauna_invalid_type(self):
        """Test adding invalid fauna type to plot."""
        with self.assertRaises(TypeError) as context:
            self.plot.add_fauna("not_fauna")
        self.assertIn("fauna must be an instance of Fauna", str(context.exception))
    
    def test_add_flora_duplicate_name_raises(self):
        """Test that adding flora with a duplicate name raises ValueError and does not replace the original."""
        flora1 = Mock()
        flora1.name = "grass"
        flora1.__class__.__name__ = "Flora"
        flora2 = Mock()
        flora2.name = "grass"
        flora2.__class__.__name__ = "Flora"
        self.plot.add_flora(flora1)
        with self.assertRaises(ValueError) as context:
            self.plot.add_flora(flora2)
        self.assertIn("already exists", str(context.exception))
        self.assertEqual(len(self.plot.flora), 1)
        self.assertIn(flora1, self.plot.flora)
        self.assertNotIn(flora2, self.plot.flora)

    def test_add_fauna_duplicate_name_raises(self):
        """Test that adding fauna with a duplicate name raises ValueError and does not replace the original."""
        fauna1 = Mock()
        fauna1.name = "mammoth"
        fauna1.__class__.__name__ = "Fauna"
        fauna2 = Mock()
        fauna2.name = "mammoth"
        fauna2.__class__.__name__ = "Fauna"
        self.plot.add_fauna(fauna1)
        with self.assertRaises(ValueError) as context:
            self.plot.add_fauna(fauna2)
        self.assertIn("already exists", str(context.exception))
        self.assertEqual(len(self.plot.fauna), 1)
        self.assertIn(fauna1, self.plot.fauna)
        self.assertNotIn(fauna2, self.plot.fauna)

    def test_get_a_fauna_found(self):
        """Test getting fauna that exists in plot."""
        mock_fauna = Mock()
        mock_fauna.name = "mammoth"
        mock_fauna.__class__.__name__ = "Fauna"
        self.plot.fauna = [mock_fauna]
        
        result = self.plot.get_a_fauna("mammoth")
        
        self.assertEqual(result, mock_fauna)
    
    def test_get_a_fauna_not_found(self):
        """Test getting fauna that doesn't exist in plot."""
        result = self.plot.get_a_fauna("nonexistent")
        
        self.assertIsNone(result)
    
    def test_get_a_fauna_invalid_name_type(self):
        """Test getting fauna with invalid name type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_a_fauna(123)  # Should be string
        self.assertIn("name must be an instance of str", str(context.exception))
    
    def test_get_a_flora_found(self):
        """Test getting flora that exists in plot."""
        mock_flora = Mock()
        mock_flora.name = "grass"
        mock_flora.__class__.__name__ = "Flora"
        self.plot.flora = [mock_flora]
        
        result = self.plot.get_a_flora("grass")
        
        self.assertEqual(result, mock_flora)
    
    def test_get_a_flora_not_found(self):
        """Test getting flora that doesn't exist in plot."""
        result = self.plot.get_a_flora("nonexistent")
        
        self.assertIsNone(result)
    
    def test_get_a_flora_invalid_name_type(self):
        """Test getting flora with invalid name type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_a_flora(123)  # Should be string
        self.assertIn("name must be an instance of str", str(context.exception))
    
    def test_get_current_temperature_valid(self):
        """Test getting current temperature with valid day."""
        result = self.plot.get_current_temperature(1)
        
        self.assertEqual(result, 15.0)
        self.mock_climate._get_current_temperature.assert_called_once_with(1)
    
    def test_get_current_temperature_invalid_day_type(self):
        """Test getting current temperature with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_temperature("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_temperature_negative_day(self):
        """Test getting current temperature with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_temperature(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_soil_temp_valid(self):
        """Test getting current soil temperature with valid day."""
        result = self.plot.get_current_soil_temp(1)
        
        self.assertEqual(result, 8.0)
        self.mock_climate._get_current_soil_temp.assert_called_once_with(1)
    
    def test_get_current_soil_temp_invalid_day_type(self):
        """Test getting current soil temperature with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_soil_temp("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_soil_temp_negative_day(self):
        """Test getting current soil temperature with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_soil_temp(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_snowfall_valid(self):
        """Test getting current snowfall with valid day."""
        result = self.plot.get_current_snowfall(1)
        
        self.assertEqual(result, 0.1)
        self.mock_climate._get_current_snowfall.assert_called_once_with(1)
    
    def test_get_current_snowfall_invalid_day_type(self):
        """Test getting current snowfall with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_snowfall("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_snowfall_negative_day(self):
        """Test getting current snowfall with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_snowfall(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_rainfall_valid(self):
        """Test getting current rainfall with valid day."""
        result = self.plot.get_current_rainfall(1)
        
        self.assertEqual(result, 5.0)
        self.mock_climate._get_current_rainfall.assert_called_once_with(1)
    
    def test_get_current_rainfall_invalid_day_type(self):
        """Test getting current rainfall with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_rainfall("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_rainfall_negative_day(self):
        """Test getting current rainfall with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_rainfall(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_uv_valid(self):
        """Test getting current UV with valid day."""
        result = self.plot.get_current_uv(1)
        
        self.assertEqual(result, 3.0)
        self.mock_climate._get_current_uv.assert_called_once_with(1)
    
    def test_get_current_uv_invalid_day_type(self):
        """Test getting current UV with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_uv("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_uv_negative_day(self):
        """Test getting current UV with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_uv(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_get_current_SSRD_valid(self):
        """Test getting current SSRD with valid day."""
        result = self.plot.get_current_SSRD(1)
        
        self.assertEqual(result, 1000.0)
        self.mock_climate._get_current_SSRD.assert_called_once_with(1)
    
    def test_get_current_SSRD_invalid_day_type(self):
        """Test getting current SSRD with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_SSRD("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_get_current_SSRD_negative_day(self):
        """Test getting current SSRD with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.get_current_SSRD(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    
    def test_update_avg_snow_height_valid(self):
        """Test updating average snow height with valid parameters."""
        # Set up initial conditions
        self.plot.avg_snow_height = 1.0  # Start with 1 meter of snow
        self.plot.plot_area = 1.0
        
        # mock fauna to create trampling effect (20% of plot area)
        mock_fauna = Mock()
        mock_fauna.get_total_mass.return_value = 100.0  # Living fauna
        mock_fauna.get_avg_feet_area.return_value = 0.1  # 0.1 km² per individual
        mock_fauna.get_avg_steps_taken.return_value = 1000.0  # 1000 steps
        mock_fauna.get_population.return_value = 2  # 2 individuals
        mock_fauna.get_avg_feet_area.return_value = 0.0001  # 0.0001 km² per individual
        mock_fauna.get_avg_steps_taken.return_value = 1000.0  # 1000 steps  
        mock_fauna.get_population.return_value = 2  # 2 individuals
        
        self.plot.fauna = [mock_fauna]
        
        initial_height = self.plot.avg_snow_height
        
        self.plot.update_avg_snow_height(1)
        
        # Should store previous height
        self.assertEqual(self.plot.previous_avg_snow_height, initial_height)
        
        # Calculate expected result:
        # Initial: 1.0m
        # Add snowfall: +0.1m (from mock)
        # Subtract SSRD loss: -((0.35 * 1000.0) / 334000) / (300.0 * 1.0) ≈ -0.00035m
        # Subtract trampling: -0.7 * 0.2 * (1.0 + 0.1 - 0.00035) ≈ -0.154m
        # Final should be: 1.0 + 0.1 - 0.00035 - 0.154 ≈ 0.946m
        
        # Calculate expected values
        snowfall = 0.1  # from mock
        ssrd_loss = (0.35 * 1000.0) / 334000 / (300.0 * 1_000_000)  # meltwater_mass / (RHO_SNOW * plot_area_m2)
        trampled_percent = 0.2 / 1.0  # 20% trampled area
        
        snow_height_after_snowfall_and_ssrd = 1.0 + snowfall - ssrd_loss
        trampling_reduction = 0.7 * trampled_percent * snow_height_after_snowfall_and_ssrd
        
        expected_height = 1.0 + snowfall - ssrd_loss - trampling_reduction
        
        self.assertAlmostEqual(self.plot.avg_snow_height, expected_height, places=6)
    
    def test_update_avg_snow_height_invalid_day_type(self):
        """Test updating snow height with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.update_avg_snow_height("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_update_avg_snow_height_negative_day(self):
        """Test updating snow height with negative day."""
        with self.assertRaises(ValueError) as context:
            self.plot.update_avg_snow_height(-1)
        self.assertIn("day must be non-negative", str(context.exception))
    

    

    
    def test_get_current_melt_water_mass_valid(self):
        """Test calculating meltwater mass from SSRD with valid day."""
        result = self.plot.get_current_melt_water_mass(1)
        
        # (ETA * SSRD) / LF = (0.75 * 1000.0) / 100_000
        ETA = 0.75
        SSRD = 1000.0
        LF = 100_000
        expected = (ETA * SSRD) / LF
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_get_current_melt_water_mass_invalid_day_type(self):
        """Test calculating meltwater mass with invalid day type."""
        with self.assertRaises(TypeError) as context:
            self.plot.get_current_melt_water_mass("1")  # Should be int
        self.assertIn("day must be an instance of int", str(context.exception))
    
    def test_snow_height_loss_from_ssrd_valid(self):
        """Test calculating snow height loss from SSRD with valid day."""
        result = self.plot.snow_height_loss_from_ssrd(1)
        
        # Use constants from Plot.py
        ETA = 0.75
        RHO_SNOW = 100.0
        LF = 100_000
        SSRD = 1000.0
        plot_area_m2 = 1.0 * 1_000_000
        meltwater_mass = (ETA * SSRD) / LF
        expected = meltwater_mass / (RHO_SNOW * plot_area_m2)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_calculate_flora_masses_empty(self):
        """Test calculating flora masses with no flora."""
        self.plot.calculate_flora_masses()
        
        # Check that instance variables were set to 0
        self.assertEqual(self.plot.grass_mass, 0.0)
        self.assertEqual(self.plot.shrub_mass, 0.0)
        self.assertEqual(self.plot.tree_mass, 0.0)
        self.assertEqual(self.plot.moss_mass, 0.0)
    
    def test_calculate_flora_masses_with_flora(self):
        """Test calculating flora masses with some flora."""
        # Create mock flora subtypes with proper class configuration
        grass = Mock()
        grass.name = "grass"
        grass.total_mass = 100.0
        grass.get_total_mass.return_value = 100.0
        grass.ideal_growth_rate = 0.1
        grass.ideal_temp_range = (10.0, 25.0)
        grass.ideal_uv_range = (1.0, 5.0)
        grass.ideal_hydration_range = (0.3, 0.8)
        grass.ideal_soil_temp_range = (5.0, 15.0)
        grass.consumers = []
        grass.plot = self.mock_plot
        grass.__class__.__name__ = "Grass"
        
        shrub = Mock()
        shrub.name = "shrub"
        shrub.total_mass = 50.0
        shrub.get_total_mass.return_value = 50.0
        shrub.ideal_growth_rate = 0.05
        shrub.ideal_temp_range = (5.0, 20.0)
        shrub.ideal_uv_range = (2.0, 6.0)
        shrub.ideal_hydration_range = (0.4, 0.9)
        shrub.ideal_soil_temp_range = (3.0, 12.0)
        shrub.consumers = []
        shrub.plot = self.mock_plot
        shrub.__class__.__name__ = "Shrub"
        
        tree = Mock()
        tree.name = "tree"
        tree.total_mass = 200.0
        tree.get_total_mass.return_value = 200.0
        tree.ideal_growth_rate = 0.02
        tree.ideal_temp_range = (0.0, 15.0)
        tree.ideal_uv_range = (3.0, 7.0)
        tree.ideal_hydration_range = (0.5, 1.0)
        tree.ideal_soil_temp_range = (1.0, 10.0)
        tree.consumers = []
        tree.plot = self.mock_plot
        tree.__class__.__name__ = "Tree"
        
        moss = Mock()
        moss.name = "moss"
        moss.total_mass = 25.0
        moss.get_total_mass.return_value = 25.0
        moss.ideal_growth_rate = 0.08
        moss.ideal_temp_range = (2.0, 18.0)
        moss.ideal_uv_range = (0.5, 4.0)
        moss.ideal_hydration_range = (0.6, 0.8)
        moss.ideal_soil_temp_range = (2.0, 8.0)
        moss.consumers = []
        moss.plot = self.mock_plot
        moss.__class__.__name__ = "Moss"
        
        self.plot.flora = [grass, shrub, tree, moss]
        
        self.plot.calculate_flora_masses()
        
        # Check that instance variables were set correctly
        self.assertEqual(self.plot.grass_mass, 100.0)
        self.assertEqual(self.plot.shrub_mass, 50.0)
        self.assertEqual(self.plot.tree_mass, 200.0)
        self.assertEqual(self.plot.moss_mass, 25.0)
    
    def test_get_flora_masses_instance_variables(self):
        """Test that get_flora_masses returns stored instance variables."""
        # Set instance variables directly
        self.plot.grass_mass = 100.0
        self.plot.shrub_mass = 50.0
        self.plot.tree_mass = 200.0
        self.plot.moss_mass = 25.0
        
        result = self.plot.get_flora_masses()
        
        self.assertEqual(result, (100.0, 50.0, 200.0, 25.0))
    
    def test_get_flora_mass_composition_empty(self):
        """Test getting flora mass composition with no flora."""
        # Need to calculate flora masses first
        self.plot.calculate_flora_masses()
        
        result = self.plot.get_flora_mass_composition()
        
        self.assertEqual(result, (0.0, 0.0, 0.0, 0.0))
    
    def test_get_flora_mass_composition_with_flora(self):
        """Test getting flora mass composition with some flora."""
        # Create mock flora subtypes with proper class configuration
        grass = Mock()
        grass.name = "grass"
        grass.total_mass = 100.0
        grass.get_total_mass.return_value = 100.0
        grass.ideal_growth_rate = 0.1
        grass.ideal_temp_range = (10.0, 25.0)
        grass.ideal_uv_range = (1.0, 5.0)
        grass.ideal_hydration_range = (0.3, 0.8)
        grass.ideal_soil_temp_range = (5.0, 15.0)
        grass.consumers = []
        grass.plot = self.mock_plot
        grass.__class__.__name__ = "Grass"
        
        shrub = Mock()
        shrub.name = "shrub"
        shrub.total_mass = 50.0
        shrub.get_total_mass.return_value = 50.0
        shrub.ideal_growth_rate = 0.05
        shrub.ideal_temp_range = (5.0, 20.0)
        shrub.ideal_uv_range = (2.0, 6.0)
        shrub.ideal_hydration_range = (0.4, 0.9)
        shrub.ideal_soil_temp_range = (3.0, 12.0)
        shrub.consumers = []
        shrub.plot = self.mock_plot
        shrub.__class__.__name__ = "Shrub"
        
        tree = Mock()
        tree.name = "tree"
        tree.total_mass = 200.0
        tree.get_total_mass.return_value = 200.0
        tree.ideal_growth_rate = 0.02
        tree.ideal_temp_range = (0.0, 15.0)
        tree.ideal_uv_range = (3.0, 7.0)
        tree.ideal_hydration_range = (0.5, 1.0)
        tree.ideal_soil_temp_range = (1.0, 10.0)
        tree.consumers = []
        tree.plot = self.mock_plot
        tree.__class__.__name__ = "Tree"
        
        moss = Mock()
        moss.name = "moss"
        moss.total_mass = 25.0
        moss.get_total_mass.return_value = 25.0
        moss.ideal_growth_rate = 0.08
        moss.ideal_temp_range = (2.0, 18.0)
        moss.ideal_uv_range = (0.5, 4.0)
        moss.ideal_hydration_range = (0.6, 1.0)
        moss.ideal_soil_temp_range = (2.0, 8.0)
        moss.consumers = []
        moss.plot = self.mock_plot
        moss.__class__.__name__ = "Moss"
        
        self.plot.flora = [grass, shrub, tree, moss]
        
        # Calculate flora masses first
        self.plot.calculate_flora_masses()
        
        result = self.plot.get_flora_mass_composition()
        
        # Total mass = 375, so ratios should be:
        # grass: 100/375 = 0.2667, shrub: 50/375 = 0.1333
        # tree: 200/375 = 0.5333, moss: 25/375 = 0.0667
        self.assertAlmostEqual(result[0], 0.26666666666666666, places=10)  # grass
        self.assertAlmostEqual(result[1], 0.13333333333333333, places=10)  # shrub
        self.assertAlmostEqual(result[2], 0.53333333333333333, places=10)  # tree
        self.assertAlmostEqual(result[3], 0.06666666666666667, places=10)  # moss

    # Capacity management tests
    
    def test_over_grass_capacity_under_limit(self):
        """Test over_grass_capacity when under the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 2000.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_grass_capacity()
        
        self.assertFalse(result)
    
    def test_over_grass_capacity_at_limit(self):
        """Test over_grass_capacity when at the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 3000.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_grass_capacity()
        
        self.assertFalse(result)  # Should be False when exactly at limit
    
    def test_over_grass_capacity_over_limit(self):
        """Test over_grass_capacity when over the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 100_000_001.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_grass_capacity()
        
        self.assertTrue(result)
    
    def test_over_shrub_capacity_under_limit(self):
        """Test over_shrub_capacity when under the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 1000.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_shrub_capacity()
        
        self.assertFalse(result)
    
    def test_over_shrub_capacity_over_limit(self):
        """Test over_shrub_capacity when over the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 100_000_001.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_shrub_capacity()
        
        self.assertTrue(result)
    
    def test_over_tree_capacity_under_limit(self):
        """Test over_tree_capacity when under the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 500.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_tree_capacity()
        
        self.assertFalse(result)
    
    def test_over_tree_capacity_over_limit(self):
        """Test over_tree_capacity when over the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 100_000_001.0
        self.plot.moss_mass = 0.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_tree_capacity()
        
        self.assertTrue(result)
    
    def test_over_moss_capacity_under_limit(self):
        """Test over_moss_capacity when under the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 100.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_moss_capacity()
        
        self.assertFalse(result)
    
    def test_over_moss_capacity_over_limit(self):
        """Test over_moss_capacity when over the limit."""
        # Initialize flora mass attributes
        self.plot.grass_mass = 0.0
        self.plot.shrub_mass = 0.0
        self.plot.tree_mass = 0.0
        self.plot.moss_mass = 100_000_001.0
        self.plot.plot_area = 1.0
        
        result = self.plot.over_moss_capacity()
        
        self.assertTrue(result)
    
    def test_over_prey_capacity_no_prey(self):
        """Test over_prey_capacity when no prey exists."""
        self.plot.fauna = []
        
        result = self.plot.over_prey_capacity()
        
        self.assertFalse(result)
    
    def test_over_prey_capacity_under_limit(self):
        """Test over_prey_capacity when under the limit."""
        # Create mock prey with total mass below limit (10 kg/km^2 * 1.0 km^2 = 10 kg)
        mock_prey1 = Mock()
        mock_prey1.total_mass = 6.0
        mock_prey1.get_total_mass.return_value = 6.0
        mock_prey1.__class__.__name__ = "Prey"

        mock_prey2 = Mock()
        mock_prey2.total_mass = 3.0
        mock_prey2.get_total_mass.return_value = 3.0
        mock_prey2.__class__.__name__ = "Prey"

        # Add a predator to ensure it's not counted
        mock_predator = Mock()
        mock_predator.total_mass = 100.0
        mock_predator.get_total_mass.return_value = 100.0
        mock_predator.__class__.__name__ = "Predator"

        self.plot.fauna = [mock_prey1, mock_prey2, mock_predator]
        self.plot.plot_area = 1.0

        result = self.plot.over_prey_capacity()

        self.assertFalse(result)  # 6 + 3 = 9 kg, under 10 kg limit
    
    def test_over_prey_capacity_over_limit(self):
        """Test over_prey_capacity when over the limit."""
        # Create mock prey with total mass above limit (10 kg/km^2 * 1.0 km^2 = 10 kg)
        mock_prey1 = Mock()
        mock_prey1.total_mass = 6.0
        mock_prey1.get_total_mass.return_value = 6.0
        mock_prey1.__class__.__name__ = "Prey"

        mock_prey2 = Mock()
        mock_prey2.total_mass = 7.0
        mock_prey2.get_total_mass.return_value = 7.0
        mock_prey2.__class__.__name__ = "Prey"

        self.plot.fauna = [mock_prey1, mock_prey2]
        self.plot.plot_area = 1.0
        result = self.plot.over_prey_capacity()
        self.assertTrue(result)  # 6 + 7 = 13 kg, over 10 kg limit
    
    def test_over_predator_capacity_under_limit(self):
        """Test over_predator_capacity when under the limit."""
        # Create mock predators with total mass below limit (10 kg/km^2 * 1.0 km^2 = 10 kg)
        mock_predator1 = Mock()
        mock_predator1.total_mass = 6.0
        mock_predator1.get_total_mass.return_value = 6.0
        mock_predator1.__class__.__name__ = "Predator"

        mock_predator2 = Mock()
        mock_predator2.total_mass = 3.0
        mock_predator2.get_total_mass.return_value = 3.0
        mock_predator2.__class__.__name__ = "Predator"

        # Add prey to ensure it's not counted
        mock_prey = Mock()
        mock_prey.total_mass = 100.0
        mock_prey.get_total_mass.return_value = 100.0
        mock_prey.__class__.__name__ = "Prey"

        self.plot.fauna = [mock_predator1, mock_predator2, mock_prey]
        self.plot.plot_area = 1.0

        result = self.plot.over_predator_capacity()

        self.assertFalse(result)  # 6 + 3 = 9 kg, under 10 kg limit
    
    def test_over_predator_capacity_over_limit(self):
        """Test over_predator_capacity when over the limit."""
        # Create mock predators with total mass above limit (10 kg/km^2 * 1.0 km^2 = 10 kg)
        mock_predator1 = Mock()
        mock_predator1.total_mass = 6.0
        mock_predator1.get_total_mass.return_value = 6.0
        mock_predator1.__class__.__name__ = "Predator"

        mock_predator2 = Mock()
        mock_predator2.total_mass = 7.0
        mock_predator2.get_total_mass.return_value = 7.0
        mock_predator2.__class__.__name__ = "Predator"

        self.plot.fauna = [mock_predator1, mock_predator2]
        self.plot.plot_area = 1.0
        result = self.plot.over_predator_capacity()
        self.assertTrue(result)  # 6 + 7 = 13 kg, over 10 kg limit

if __name__ == '__main__':
    unittest.main()