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

if __name__ == "__main__":
    unittest.main()
