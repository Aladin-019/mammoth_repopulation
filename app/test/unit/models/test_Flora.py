import unittest
from unittest.mock import MagicMock
from app.models.Flora import Flora
from app.models.Fauna import Fauna


class TestFlora(unittest.TestCase):
    def setUp(self):
        # Create a simple Fauna consumer mock
        self.consumer = MagicMock(spec=Fauna)
        self.consumer.get_name.return_value = "Deer"
        self.consumer.population = 5
        self.consumer.get_feeding_rate.return_value = 0.2   # 0.2 kg/day per individual

        # Create a mock plot
        self.plot = MagicMock()
        self.plot.get_all_fauna.return_value = [self.consumer]

        # Create Flora instance (SUT)
        self.flora = Flora(
            name="Grass",
            description="Tundra grass",
            total_mass=100.0,
            ideal_growth_rate=2.0,   #kg/day
            ideal_temp_range=(-70.0, 20.0),
            ideal_uv_range=(0.0, 8.0),
            ideal_hydration_range=(1.0, 5.0),
            ideal_soil_temp_range=(2.0, 12.0),
            consumers=[self.consumer],
            root_depth=1.0,
            plot=self.plot
        )

    def test_flora_creation(self):
        """Test that Flora is created with correct attributes"""
        self.assertEqual(self.flora.name, "Grass")
        self.assertEqual(self.flora.description, "Tundra grass")
        self.assertEqual(self.flora.total_mass, 100.0)
        self.assertEqual(self.flora.root_depth, 1.0)
        self.assertEqual(len(self.flora.consumers), 1)

    def test_get_name(self):
        """Test get_name method"""
        self.assertEqual(self.flora.get_name(), "Grass")

    def test_get_description(self):
        """Test get_description method"""
        self.assertEqual(self.flora.get_description(), "Tundra grass")

    def test_get_total_mass(self):
        """Test get_total_mass method"""
        self.assertEqual(self.flora.get_total_mass(), 100.0)

    def test_total_consumption_rate(self):
        """Test total consumption rate calculation"""
        expected = 5 * 0.2  # population * feeding_rate
        self.assertEqual(self.flora.total_consumption_rate(), expected)

    def test_total_consumption_rate_no_consumers_on_plot(self):
        """Test consumption rate when consumers are not on the plot"""
        # Mock plot with no fauna
        self.plot.get_all_fauna.return_value = []
        self.assertEqual(self.flora.total_consumption_rate(), 0.0)

    def test_distance_from_ideal_range(self):
        """Test distance calculation from ideal range"""
        # Test value within range
        distance = self.flora.distance_from_ideal(5.0, (0.0, 10.0))
        self.assertEqual(distance, 0.0)

        # Test value below range but below maximum penalty edge
        distance = self.flora.distance_from_ideal(-2.0, (0.0, 10.0))
        self.assertEqual(distance, -1.4)
        
        # Test value below range at maximum penalty edge
        distance = self.flora.distance_from_ideal(-5.0, (0.0, 10.0))
        self.assertEqual(distance, -2.0)
        
        # Test value above range at maximum penalty edge
        distance = self.flora.distance_from_ideal(15.0, (0.0, 10.0))
        self.assertEqual(distance, -2.0)

        # Test value above range and well above maximum penalty edge
        distance = self.flora.distance_from_ideal(100.0, (0.0, 10.0))
        self.assertEqual(distance, -2.0)

    def test_distance_from_ideal_single_value_range(self):
        """Test distance calculation when min equals max (single value range)"""
        distance = self.flora.distance_from_ideal(5.0, (5.0, 5.0))
        self.assertEqual(distance, 0.0)

    def test_update_flora_mass_improves_mass_under_ideal_conditions(self):
        """Test that flora mass increases under ideal conditions"""
        initial_mass = self.flora.total_mass
        self.flora.update_flora_mass(current_temp=0.0, current_uv=5.0,
                                     current_hydration=3.0, current_soil_temp=5.0)
        self.assertGreater(self.flora.total_mass, initial_mass)
        #print(f"1. Initial mass: {initial_mass}, New mass: {self.flora.total_mass}")

    def test_update_flora_mass_decreases_mass_under_bad_conditions(self):
        """Test that flora mass decreases under bad environmental conditions"""
        initial_mass = self.flora.total_mass
        self.flora.update_flora_mass(current_temp=-100.0, current_uv=20.0,
                                     current_hydration=0.0, current_soil_temp=-10.0)
        self.assertLess(self.flora.total_mass, initial_mass)
        #print(f"2. Initial mass: {initial_mass}, New mass: {self.flora.total_mass}")   

    def test_update_flora_mass_never_negative(self):
        """Test that flora mass never becomes negative"""
        self.flora.total_mass = 1.0
        self.flora.update_flora_mass(current_temp=-100.0, current_uv=20.0,
                                     current_hydration=0.0, current_soil_temp=-10.0)
        self.assertGreaterEqual(self.flora.total_mass, 0.0)
        #print(f"3. Final mass: {self.flora.total_mass}")

    def test_update_flora_mass_with_consumption(self):
        """Test that flora mass accounts for consumption by fauna"""
        # Set up high consumption rate
        self.consumer.population = 100
        self.consumer.get_feeding_rate.return_value = 1.0
        
        initial_mass = self.flora.total_mass
        self.flora.update_flora_mass(current_temp=0.0, current_uv=5.0,
                                     current_hydration=3.0, current_soil_temp=5.0)
        
        # Mass should decrease much due to high consumption, should be 0
        self.assertLess(self.flora.total_mass, initial_mass)
        #print(f"4. Initial mass: {initial_mass}, New mass: {self.flora.total_mass}")


if __name__ == "__main__":
    unittest.main()
