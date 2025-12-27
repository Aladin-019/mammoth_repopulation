import unittest
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.Plot import Plot
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Fauna.Prey import Prey
from app.models.Fauna.Predator import Predator
from unittest.mock import Mock

class TestGridInitializer(unittest.TestCase):
    def setUp(self):
        self.gi = GridInitializer()

    def test_default_resolution_and_area(self):
        self.assertAlmostEqual(self.gi.plot_area_km2, 1304.25, places=2)
        self.assertAlmostEqual(self.gi.standardization_factor, 1304.25, places=2)

    def test_custom_resolution_and_area(self):
        gi = GridInitializer(lat_step=1.0, lon_step=1.0)
        expected_area = (1.0 * 111.0) * (1.0 * 47.0)
        self.assertAlmostEqual(gi.plot_area_km2, expected_area, places=2)
        self.assertAlmostEqual(gi.standardization_factor, expected_area, places=2)

    def test_biome_defaults_keys(self):
        expected_biomes = {'southern taiga', 'northern taiga', 'southern tundra', 'northern tundra'}
        self.assertEqual(set(self.gi.biome_defaults.keys()), expected_biomes)

    def test_biome_defaults_structure(self):
        for biome, defaults in self.gi.biome_defaults.items():
            self.assertIn('flora', defaults)
            self.assertIn('prey', defaults)
            self.assertIn('predators', defaults)
            self.assertIsInstance(defaults['flora'], list)
            self.assertIsInstance(defaults['prey'], list)
            self.assertIsInstance(defaults['predators'], list)

    def test_update_resolution(self):
        self.gi.update_resolution(1.0, 1.0)
        self.assertAlmostEqual(self.gi.plot_area_km2, 111.0 * 47.0, places=2)
        self.assertAlmostEqual(self.gi.standardization_factor, 111.0 * 47.0, places=2)

    def test_get_resolution_info(self):
        gi = GridInitializer(lat_step=0.5, lon_step=0.5)
        info = gi.get_resolution_info()
        self.assertIn('plot_area_km2', info)
        self.assertIn('standardization_factor', info)
        self.assertEqual(info['base_resolution_km2'], 1.0)
        self.assertAlmostEqual(info['plot_area_km2'], gi.plot_area_km2, places=2)
        self.assertAlmostEqual(info['standardization_factor'], gi.standardization_factor, places=2)

    def test_get_plot_grid_returns_plotgrid(self):
        grid = self.gi.get_plot_grid()
        self.assertIsInstance(grid, PlotGrid)

    def test_create_plot_from_biome(self):
        plot = self.gi.create_plot_from_biome('southern taiga')
        self.assertIsInstance(plot, Plot)
        self.assertEqual(plot.climate.get_biome(), 'southern taiga')
        self.assertEqual(plot.plot_area, self.gi.plot_area_km2)

    def test_create_plot_from_biome_invalid_biome(self):
        with self.assertRaises(ValueError) as cm:
            self.gi.create_plot_from_biome('not_a_biome')
        self.assertIn("Unknown biome", str(cm.exception))

    def test_create_plot_from_biome_non_string(self):
        with self.assertRaises(TypeError):
            self.gi.create_plot_from_biome(123)

    def test_create_plot_from_biome_negative_plot_counter(self):
        self.gi.plot_counter = -1
        with self.assertRaises(ValueError) as cm:
            self.gi.create_plot_from_biome('southern taiga')
        self.assertIn("cannot be negative", str(cm.exception))

    def test__add_default_flora_adds_flora(self):
        class DummyFlora:
            pass
        class DummyPlot:
            def __init__(self):
                self.flora = []
            def add_flora(self, flora):
                self.flora.append(flora)
        # Patch _create_flora_for_biome to return DummyFlora
        self.gi._create_flora_for_biome = lambda name, biome, plot: DummyFlora()
        plot = DummyPlot()
        self.gi._add_default_flora(plot, 'southern taiga')
        self.assertEqual(len(plot.flora), len(self.gi.biome_defaults['southern taiga']['flora']))

    def test__add_default_fauna_adds_prey_and_predators(self):
        class DummyPrey:
            def __init__(self, name):
                self.name = name
                self.plot = None
        class DummyPredator:
            def __init__(self, name):
                self.name = name
                self.plot = None
        class DummyPlot:
            def __init__(self):
                self.fauna = []
            def add_fauna(self, fauna):
                self.fauna.append(fauna)
        # Patch creation methods
        self.gi._create_prey = lambda name, plot: DummyPrey(name)
        self.gi._create_predator = lambda name, prey_list, plot: DummyPredator(name)
        self.gi._establish_food_chain_relationships = lambda plot: None
        self.gi._update_predator_prey_lists = lambda plot: None
        plot = DummyPlot()
        self.gi._add_default_fauna(plot, 'southern taiga')
        prey_names = [n for n in self.gi.biome_defaults['southern taiga']['prey'] if n != 'mammoth']
        predator_names = self.gi.biome_defaults['southern taiga']['predators']
        prey_count = sum(isinstance(f, DummyPrey) for f in plot.fauna)
        predator_count = sum(isinstance(f, DummyPredator) for f in plot.fauna)
        self.assertEqual(prey_count, len(prey_names))
        self.assertEqual(predator_count, len(predator_names))
        # Check names
        self.assertSetEqual(set(f.name for f in plot.fauna), set(prey_names + predator_names))

    def test__add_default_fauna_excludes_mammoth(self):
        class DummyPrey:
            def __init__(self, name):
                self.name = name
        class DummyPlot:
            def __init__(self):
                self.fauna = []
            def add_fauna(self, fauna):
                self.fauna.append(fauna)
        self.gi._create_prey = lambda name, plot: DummyPrey(name)
        self.gi._create_predator = lambda name, prey_list, plot: None
        self.gi._establish_food_chain_relationships = lambda plot: None
        self.gi._update_predator_prey_lists = lambda plot: None
        plot = DummyPlot()
        self.gi._add_default_fauna(plot, 'southern taiga')
        names = [f.name for f in plot.fauna]
        self.assertNotIn('mammoth', names)

    def test__get_standardized_float(self):
        gi = GridInitializer(lat_step=2.0, lon_step=2.0)
        # plot_area_km2 = 2*111 * 2*47 = 20868
        # standardization_factor = 20868
        self.assertAlmostEqual(gi._get_standardized_float(1.5), 1.5 * gi.standardization_factor)
        self.assertAlmostEqual(gi._get_standardized_float(0), 0)
        self.assertAlmostEqual(gi._get_standardized_float(-2), -2 * gi.standardization_factor)

    def test__get_standardized_population(self):
        gi = GridInitializer(lat_step=2.0, lon_step=2.0)
        # plot_area_km2 = 20868, standardization_factor = 20868
        # Should round down and never return negative
        self.assertEqual(gi._get_standardized_population(1.5), int(1.5 * gi.standardization_factor))
        self.assertEqual(gi._get_standardized_population(0), 0)
        self.assertEqual(gi._get_standardized_population(-2), 0)

    def test__m2_to_km2(self):
        self.assertAlmostEqual(self.gi._m2_to_km2(1_000_000), 1.0)
        self.assertAlmostEqual(self.gi._m2_to_km2(500_000), 0.5)
        self.assertAlmostEqual(self.gi._m2_to_km2(0), 0.0)
        self.assertAlmostEqual(self.gi._m2_to_km2(-1_000_000), -1.0)

    def test__add_random_variation_within_bounds(self):
        base = 100.0
        percent = 15.0
        for _ in range(20):
            varied = self.gi._add_random_variation(base, percent)
            self.assertGreaterEqual(varied, base * (1 - percent/100.0))
            self.assertLessEqual(varied, base * (1 + percent/100.0))

    def test__add_random_variation_zero_percent(self):
        base = 100.0
        for _ in range(10):
            self.assertAlmostEqual(self.gi._add_random_variation(base, 0), base)

    def test__create_flora_for_biome_all_types(self):
        # Patch random and standardization methods for deterministic output
        self.gi._add_random_variation = lambda base, percent=15.0: base
        self.gi._get_standardized_float = lambda base: base * self.gi.standardization_factor
        self.gi._get_standardized_population = lambda base: int(base * self.gi.standardization_factor)
        self.gi._m2_to_km2 = lambda area: area / 1_000_000
        mock_climate = Mock()
        mock_climate.__class__.__name__ = "Climate"
        class DummyPlot(Plot):
            def __init__(self):
                super().__init__(Id=0, avg_snow_height=0.1, climate=mock_climate, plot_area=1.0)
        plot = DummyPlot()
        flora_types = ['grass', 'shrub', 'tree', 'moss']
        biomes = ['southern taiga', 'northern taiga', 'southern tundra', 'northern tundra']
        for flora_type in flora_types:
            for biome in biomes:
                flora = self.gi._create_flora_for_biome(flora_type, biome, plot)
                self.assertIsNotNone(flora, f"Expected flora for {flora_type} in {biome}")
                self.assertTrue(hasattr(flora, 'name'))
                self.assertTrue(isinstance(flora.name, str))
                self.assertTrue(hasattr(flora, 'description'))
                self.assertTrue(isinstance(flora.description, str))
                self.assertTrue(len(flora.description) > 0)
                # Check population and mass attributes
                self.assertIsInstance(flora.population, int)
                self.assertGreaterEqual(flora.population, 0)
                if flora_type == 'grass' or flora_type == 'moss':
                    self.assertTrue(hasattr(flora, 'total_mass'))
                    self.assertGreaterEqual(flora.total_mass, 0)
                if flora_type == 'shrub' or flora_type == 'tree':
                    self.assertTrue(hasattr(flora, 'avg_mass'))
                    self.assertGreater(flora.avg_mass, 0)
                # Check growth and ideal ranges
                self.assertTrue(hasattr(flora, 'ideal_growth_rate'))
                self.assertGreater(flora.ideal_growth_rate, 0)
                self.assertTrue(hasattr(flora, 'ideal_temp_range'))
                self.assertIsInstance(flora.ideal_temp_range, tuple)
                self.assertEqual(len(flora.ideal_temp_range), 2)
                self.assertTrue(hasattr(flora, 'ideal_uv_range'))
                self.assertIsInstance(flora.ideal_uv_range, tuple)
                self.assertEqual(len(flora.ideal_uv_range), 2)
                self.assertTrue(hasattr(flora, 'ideal_hydration_range'))
                self.assertIsInstance(flora.ideal_hydration_range, tuple)
                self.assertEqual(len(flora.ideal_hydration_range), 2)
                self.assertTrue(hasattr(flora, 'ideal_soil_temp_range'))
                self.assertIsInstance(flora.ideal_soil_temp_range, tuple)
                self.assertEqual(len(flora.ideal_soil_temp_range), 2)
                # Check consumers list
                self.assertTrue(hasattr(flora, 'consumers'))
                self.assertIsInstance(flora.consumers, list)
                self.assertEqual(len(flora.consumers), 0) # No consumers at creation
                # Check Plot
                self.assertTrue(hasattr(flora, 'plot'))
                self.assertEqual(flora.plot, plot)
                # Check root depth
                self.assertTrue(hasattr(flora, 'root_depth'))
                if flora_type == 'tree':
                    self.assertEqual(flora.root_depth, 3)
                else:
                    self.assertEqual(flora.root_depth, 1)
                # Check Tree specific attributes
                if flora_type == 'tree':
                    self.assertGreaterEqual(flora.single_tree_canopy_cover, 0)
                    self.assertEqual(flora.coniferous, True)

    def test__create_flora_for_biome_invalid_type(self):
        plot = object()
        flora = self.gi._create_flora_for_biome('not_a_flora', 'southern taiga', plot)
        self.assertIsNone(flora)

    def test__create_prey_all_types(self):
        # Patch random and standardization methods for deterministic output
        self.gi._add_random_variation = lambda base, percent=15.0: float(base)
        self.gi._get_standardized_float = lambda base: float(base * self.gi.standardization_factor)
        self.gi._get_standardized_population = lambda base: int(base * self.gi.standardization_factor)
        self.gi._m2_to_km2 = lambda area: float(area) / 1_000_000
        mock_climate = Mock()
        mock_climate.__class__.__name__ = "Climate"
        class DummyPlot(Plot):
            def __init__(self):
                super().__init__(Id=0, avg_snow_height=0.1, climate=mock_climate, plot_area=1.0)
        plot = DummyPlot()
        prey_types = ['deer', 'mammoth']
        for prey_type in prey_types:
            prey = self.gi._create_prey(prey_type, plot)
            self.assertIsNotNone(prey, f"Expected prey: {prey_type}")
            self.assertIsInstance(prey, Prey)
            self.assertTrue(hasattr(prey, 'name'))
            self.assertTrue(hasattr(prey, 'description'))
            self.assertIsInstance(prey.description, str)
            self.assertTrue(len(prey.description) > 0)
            # Check population and mass attributes
            self.assertTrue(hasattr(prey, 'population'))
            self.assertIsInstance(prey.population, int)
            self.assertGreaterEqual(prey.population, 0)
            self.assertTrue(hasattr(prey, 'avg_mass'))
            self.assertGreater(prey.avg_mass, 0)
            # Check ideal growth rate and ranges
            self.assertTrue(hasattr(prey, 'ideal_growth_rate'))
            self.assertIsInstance(prey.ideal_growth_rate, float)
            self.assertTrue(hasattr(prey, 'ideal_temp_range'))
            self.assertIsInstance(prey.ideal_temp_range, tuple)
            self.assertEqual(len(prey.ideal_temp_range), 2)
            self.assertTrue(hasattr(prey, 'min_food_per_day'))
            self.assertIsInstance(prey.min_food_per_day, float)
            self.assertGreater(prey.min_food_per_day, 0)
            # Check feeding rate
            self.assertTrue(hasattr(prey, 'feeding_rate'))
            self.assertIsInstance(prey.feeding_rate, float)
            self.assertGreater(prey.feeding_rate, 0)
            # Check steps and foot area
            self.assertTrue(hasattr(prey, 'avg_steps_taken'))
            self.assertIsInstance(prey.avg_steps_taken, float)
            self.assertGreater(prey.avg_steps_taken, 0)
            self.assertTrue(hasattr(prey, 'avg_foot_area'))
            self.assertIsInstance(prey.avg_foot_area, float)
            self.assertGreater(prey.avg_foot_area, 0)
            # Check Plot
            self.assertTrue(hasattr(prey, 'plot'))
            self.assertEqual(prey.plot, plot)
            # Check predators and consumable flora lists
            self.assertTrue(hasattr(prey, 'predators'))
            self.assertIsInstance(prey.predators, list)
            self.assertEqual(len(prey.predators), 0) # No predators at creation
            self.assertTrue(hasattr(prey, 'consumable_flora'))
            self.assertIsInstance(prey.consumable_flora, list)
            self.assertEqual(len(prey.consumable_flora), 0) # No consumable flora at creation

    def test__create_prey_invalid_type(self):
        gi = GridInitializer()
        mock_climate = Mock()
        mock_climate.__class__.__name__ = "Climate"
        class DummyPlot(Plot):
            def __init__(self):
                super().__init__(Id=0, avg_snow_height=0.1, climate=mock_climate, plot_area=1.0)
        plot = DummyPlot()
        prey = gi._create_prey('not_a_prey', plot)
        self.assertIsNone(prey)

    def test_create_predator_wolf_returns_predator(self):
        gi = GridInitializer()
        gi._add_random_variation = lambda base, percent=15.0: float(base)
        gi._get_standardized_float = lambda base: float(base * gi.standardization_factor)
        gi._get_standardized_population = lambda base: int(base * gi.standardization_factor)
        gi._m2_to_km2 = lambda area: float(area) / 1_000_000
        mock_climate = Mock()
        mock_climate.__class__.__name__ = "Climate"
        plot = Plot(Id=0, avg_snow_height=0.1, climate=mock_climate, plot_area=1.0)
        predator = gi._create_predator('wolf', plot)
        self.assertIsNotNone(predator)
        self.assertIsInstance(predator, Predator)
        self.assertTrue(hasattr(predator, 'name'))
        self.assertEqual(predator.name, 'Wolf')
        self.assertTrue(hasattr(predator, 'description'))
        self.assertIsInstance(predator.description, str)
        self.assertTrue(len(predator.description) > 0)
        # Check population and mass attributes
        self.assertTrue(hasattr(predator, 'population'))
        self.assertIsInstance(predator.population, int)
        self.assertGreater(predator.population, 0)
        self.assertTrue(hasattr(predator, 'avg_mass'))
        self.assertIsInstance(predator.avg_mass, float)
        self.assertGreater(predator.avg_mass, 0)
        # Check ideal growth rate and ranges
        self.assertTrue(hasattr(predator, 'ideal_growth_rate'))
        self.assertIsInstance(predator.ideal_growth_rate, float)
        self.assertGreater(predator.ideal_growth_rate, 0)
        self.assertTrue(hasattr(predator, 'min_food_per_day'))
        self.assertIsInstance(predator.min_food_per_day, float)
        self.assertGreater(predator.min_food_per_day, 0)
        self.assertTrue(hasattr(predator, 'feeding_rate'))
        self.assertIsInstance(predator.feeding_rate, float)
        self.assertGreater(predator.feeding_rate, 0)
        # Check steps and foot area
        self.assertTrue(hasattr(predator, 'avg_steps_taken'))
        self.assertIsInstance(predator.avg_steps_taken, float)
        self.assertGreater(predator.avg_steps_taken, 0)
        self.assertTrue(hasattr(predator, 'avg_foot_area'))
        self.assertIsInstance(predator.avg_foot_area, float)
        self.assertGreater(predator.avg_foot_area, 0)
        # Check Plot
        self.assertTrue(hasattr(predator, 'plot'))
        self.assertEqual(predator.plot, plot)
        # Check prey list
        self.assertTrue(hasattr(predator, 'prey'))
        self.assertIsInstance(predator.prey, list)
        self.assertEqual(predator.prey, [])

    def test_create_predator_unknown_returns_none(self):
        gi = GridInitializer()
        gi._add_random_variation = lambda base, percent=15.0: float(base)
        gi._get_standardized_float = lambda base: float(base)
        gi._get_standardized_population = lambda base: int(base)
        gi._m2_to_km2 = lambda area: float(area) / 1_000_000
        mock_climate = Mock()
        mock_climate.__class__.__name__ = "Climate"
        plot = Plot(Id=0, avg_snow_height=0.1, climate=mock_climate, plot_area=1.0)
        predator = gi._create_predator('unknown', [], plot)
        self.assertIsNone(predator)


if __name__ == "__main__":
    unittest.main()
