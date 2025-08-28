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

if __name__ == "__main__":
    unittest.main()
