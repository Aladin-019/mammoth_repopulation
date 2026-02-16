import unittest
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.Plot import Plot

class TestWolfMammothIntegration(unittest.TestCase):
    def setUp(self):
        self.initializer = GridInitializer(lat_step=1.0, lon_step=1.0)
        self.plot = self.initializer.create_plot_from_biome('northern taiga')
        # Mock temperature to a safe value (10°C) to avoid climate data issues
        self.plot.get_current_temperature = lambda day: 10.0
        # Add one mammoth and one wolf
        self.mammoth = self.initializer.add_mammoth_to_plot(self.plot, population_per_km2=0.1)
        self.wolf = self.initializer.add_wolf_to_plot(self.plot, population_per_km2=0.05)
        # Ensure predator-prey lists are correct
        self.initializer._update_predator_prey_lists(self.plot)

    def print_wolf_food_penalty(self):
        current_food = self.wolf.plot.get_a_fauna('Mammoth').get_total_mass() if self.wolf.plot.get_a_fauna('Mammoth') else 0.0
        min_food = self.wolf.min_food_per_day
        penalty = self.wolf.distance_from_min_food(float(current_food))
        print(f"[DEBUG] Wolf current_food: {current_food}, min_food: {min_food}, penalty: {penalty}")

    def test_wolf_consumes_mammoth(self):
        self.print_wolf_food_penalty()
        # Print initial populations and masses
        print(f"[DEBUG] Initial mammoth population: {self.mammoth.get_population()}")
        print(f"[DEBUG] Initial wolf population: {self.wolf.get_population()}")
        print(f"[DEBUG] Initial mammoth mass: {self.mammoth.get_total_mass()}")
        print(f"[DEBUG] Initial wolf mass: {self.wolf.get_total_mass()}")
        print(f"[DEBUG] Wolf feeding rate: {self.wolf.get_feeding_rate()}")
        print(f"[DEBUG] Mammoth feeding rate: {self.mammoth.get_feeding_rate()}")
        # Record initial masses
        initial_mammoth_mass = self.mammoth.get_total_mass()
        initial_wolf_mass = self.wolf.get_total_mass()
        # Simulate one day where wolves eat mammoths
        day = 2  # Even day: prey update
        consumption_rate = self.mammoth.total_consumption_rate()
        print(f"[DEBUG] Prey update: day {day}, mammoth consumption_rate: {consumption_rate}")
        self.mammoth.update_prey_mass(day)
        print(f"[DEBUG] Mammoth mass after prey update: {self.mammoth.get_total_mass()}")
        day = 3  # Odd day: predator update
        self.wolf.update_predator_mass(day)
        print(f"[DEBUG] Wolf mass after predator update: {self.wolf.get_total_mass()}")
        self.print_wolf_food_penalty()
        # After update, mammoth mass should decrease, wolf mass should increase
        new_mammoth_mass = self.mammoth.get_total_mass()
        new_wolf_mass = self.wolf.get_total_mass()
        print(f"[DEBUG] Final mammoth mass: {new_mammoth_mass}")
        print(f"[DEBUG] Final wolf mass: {new_wolf_mass}")
        self.assertGreater(
            new_wolf_mass, initial_wolf_mass,
            f"New_wolf_mass ({new_wolf_mass}) <= initial_wolf_mass ({initial_wolf_mass})"
        )
if __name__ == '__main__':
    unittest.main()
