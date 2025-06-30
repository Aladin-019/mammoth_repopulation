import unittest
from unittest.mock import MagicMock
from app.models.Flora import Flora
from app.models.Fauna import Fauna


class TestFlora(unittest.TestCase):
    def setUp(self):
        # Create a simple Fauna consumer
        self.consumer = MagicMock(spec=Fauna)
        self.consumer.get_name.return_value = "Deer"
        self.consumer.population = 5
        self.consumer.get_feeding_rate.return_value = 0.2

        # Create Flora instance
        self.flora = Flora(
            name="Grass",
            description="Tundra grass",
            total_mass=100.0,
            ideal_growth_rate=0.01,
            ideal_temp_range=(-70.0, 20.0),
            ideal_uv_range=(0.0, 8.0),
            ideal_hydration_range=(1.0, 5.0),
            ideal_soil_temp_range=(2.0, 12.0),
            consumers=[self.consumer],
            root_depth=1.0,
            plot=MagicMock()  # Mock the FloraPlotInformation interface
        )

    def test_flora_creation(self):
        """Test that Flora is created with correct attributes"""
        self.assertEqual(self.flora.name, "Grass")
        self.assertEqual(self.flora.total_mass, 100.0)
        self.assertEqual(self.flora.root_depth, 1.0)

    def test_get_name(self):
        """Test get_name method"""
        self.assertEqual(self.flora.get_name(), "Grass")

    def test_get_total_mass(self):
        """Test get_total_mass method"""
        self.assertEqual(self.flora.get_total_mass(), 100.0)

    def test_total_consumption_rate(self):
        """Test total consumption rate calculation"""
        expected = 5 * 0.2  # population * feeding_rate
        self.assertEqual(self.flora.total_consumption_rate(), expected)

    def test_get_consumer_population_consumer_found(self):
        """Test get_consumer_population when consumer is in consumers list"""
        # Mock the interface method to return the consumer
        self.flora.get_all_fauna = MagicMock(return_value=[self.consumer])
        
        population = self.flora.get_consumer_population(self.consumer)
        self.assertEqual(population, 5)

    def test_get_consumer_population_consumer_not_found(self):
        """Test get_consumer_population when consumer is not in consumers list"""
        other_consumer = MagicMock(spec=Fauna)
        other_consumer.get_name.return_value = "Wolf"
        other_consumer.population = 3
        
        population = self.flora.get_consumer_population(other_consumer)
        self.assertEqual(population, 0)

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


if __name__ == "__main__":
    unittest.main()
