import unittest
from app.setup.grid_initializer import GridInitializer

class TestGridInitializer(unittest.TestCase):
    def test_default_resolution_and_area(self):
        gi = GridInitializer()
        self.assertAlmostEqual(gi.plot_area_km2, 1304.25, places=2)
        self.assertAlmostEqual(gi.standardization_factor, 1304.25, places=2)

    def test_custom_resolution_and_area(self):
        gi = GridInitializer(lat_step=1.0, lon_step=1.0)
        expected_area = (1.0 * 111.0) * (1.0 * 47.0)
        self.assertAlmostEqual(gi.plot_area_km2, expected_area, places=2)
        self.assertAlmostEqual(gi.standardization_factor, expected_area, places=2)

    def test_biome_defaults_keys(self):
        gi = GridInitializer()
        expected_biomes = {'southern taiga', 'northern taiga', 'southern tundra', 'northern tundra'}
        self.assertEqual(set(gi.biome_defaults.keys()), expected_biomes)

    def test_biome_defaults_structure(self):
        gi = GridInitializer()
        for biome, defaults in gi.biome_defaults.items():
            self.assertIn('flora', defaults)
            self.assertIn('prey', defaults)
            self.assertIn('predators', defaults)
            self.assertIsInstance(defaults['flora'], list)
            self.assertIsInstance(defaults['prey'], list)
            self.assertIsInstance(defaults['predators'], list)

    def test_update_resolution(self):
        gi = GridInitializer()
        gi.update_resolution(1.0, 1.0)
        self.assertAlmostEqual(gi.plot_area_km2, 111.0 * 47.0, places=2)
        self.assertAlmostEqual(gi.standardization_factor, 111.0 * 47.0, places=2)

    def test_get_resolution_info(self):
        gi = GridInitializer(lat_step=0.5, lon_step=0.5)
        info = gi.get_resolution_info()
        self.assertIn('plot_area_km2', info)
        self.assertIn('standardization_factor', info)
        self.assertEqual(info['base_resolution_km2'], 1.0)
        self.assertAlmostEqual(info['plot_area_km2'], gi.plot_area_km2, places=2)
        self.assertAlmostEqual(info['standardization_factor'], gi.standardization_factor, places=2)

    def test_get_plot_grid_returns_plotgrid(self):
        gi = GridInitializer()
        grid = gi.get_plot_grid()
        from app.models.Plot.PlotGrid import PlotGrid
        self.assertIsInstance(grid, PlotGrid)

    def test_create_plot_from_biome(self):
        gi = GridInitializer()
        plot = gi.create_plot_from_biome('southern taiga')
        from app.models.Plot.Plot import Plot
        self.assertIsInstance(plot, Plot)
        self.assertEqual(plot.climate.get_biome(), 'southern taiga')
        self.assertEqual(plot.plot_area, gi.plot_area_km2)

    def test_create_plot_from_biome_invalid_biome(self):
        gi = GridInitializer()
        with self.assertRaises(ValueError) as cm:
            gi.create_plot_from_biome('not_a_biome')
        self.assertIn("Unknown biome", str(cm.exception))

    def test_create_plot_from_biome_non_string(self):
        gi = GridInitializer()
        with self.assertRaises(TypeError):
            gi.create_plot_from_biome(123)

    def test_create_plot_from_biome_negative_plot_counter(self):
        gi = GridInitializer()
        gi.plot_counter = -1
        with self.assertRaises(ValueError) as cm:
            gi.create_plot_from_biome('southern taiga')
        self.assertIn("cannot be negative", str(cm.exception))

    def test__add_default_flora_adds_flora(self):
        gi = GridInitializer()
        class DummyFlora:
            pass
        class DummyPlot:
            def __init__(self):
                self.flora = []
            def add_flora(self, flora):
                self.flora.append(flora)
        # Patch _create_flora_for_biome to return DummyFlora
        gi._create_flora_for_biome = lambda name, biome, plot: DummyFlora()
        plot = DummyPlot()
        gi._add_default_flora(plot, 'southern taiga')
        self.assertEqual(len(plot.flora), len(gi.biome_defaults['southern taiga']['flora']))

    def test__add_default_fauna_adds_prey_and_predators(self):
        gi = GridInitializer()
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
        gi._create_prey_for_biome = lambda name, biome, plot: DummyPrey(name)
        gi._create_predator_for_biome = lambda name, biome, prey_list, plot: DummyPredator(name)
        gi._establish_food_chain_relationships = lambda plot: None
        gi._update_predator_prey_lists = lambda plot: None
        plot = DummyPlot()
        gi._add_default_fauna(plot, 'southern taiga')
        prey_names = [n for n in gi.biome_defaults['southern taiga']['prey'] if n != 'mammoth']
        predator_names = gi.biome_defaults['southern taiga']['predators']
        prey_count = sum(isinstance(f, DummyPrey) for f in plot.fauna)
        predator_count = sum(isinstance(f, DummyPredator) for f in plot.fauna)
        self.assertEqual(prey_count, len(prey_names))
        self.assertEqual(predator_count, len(predator_names))
        # Check names
        self.assertSetEqual(set(f.name for f in plot.fauna), set(prey_names + predator_names))

    def test__add_default_fauna_excludes_mammoth(self):
        gi = GridInitializer()
        class DummyPrey:
            def __init__(self, name):
                self.name = name
        class DummyPlot:
            def __init__(self):
                self.fauna = []
            def add_fauna(self, fauna):
                self.fauna.append(fauna)
        gi._create_prey_for_biome = lambda name, biome, plot: DummyPrey(name)
        gi._create_predator_for_biome = lambda name, biome, prey_list, plot: None
        gi._establish_food_chain_relationships = lambda plot: None
        gi._update_predator_prey_lists = lambda plot: None
        plot = DummyPlot()
        gi._add_default_fauna(plot, 'southern taiga')
        names = [f.name for f in plot.fauna]
        self.assertNotIn('mammoth', names)

if __name__ == "__main__":
    unittest.main()
