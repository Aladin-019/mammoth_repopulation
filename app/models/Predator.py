
from app.models.Fauna import Fauna
from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation

class Predator(Fauna):
    """
    Represents a predator in the ecosystem.
    Inherits from Fauna and adds specific predator behaviors.
    """

    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_temp_range: Tuple[float, float], ideal_food_range: Tuple[float, float], ideal_growth_rate: float, 
                 feeding_rate: float, avg_steps_taken: int, avg_feet_area: float, plot: PlotInformation, prey: List['Fauna']):
        super().__init__(name, description, population, avg_mass, ideal_temp_range, ideal_food_range, 
                        ideal_growth_rate, feeding_rate, avg_steps_taken, avg_feet_area, plot)
        self.prey = prey  # prey that this predator consumes

    def total_available_prey_mass(self) -> float:
        """
        Calculate the total available mass of all prey that this predator consumes.
        Only prey present on the plot are considered.
        """
        total_mass = 0.0
        plot_fauna = self.plot.get_all_fauna()

        for prey in self.prey:
            for fauna in plot_fauna:
                if prey.get_name() == fauna.get_name():
                    total_mass += fauna.get_total_mass()

        return total_mass

    def update_predator_mass(self, current_temp: float, current_food: float) -> float:
        """
        Update the total mass of the predator based on current environmental conditions.
        Predator mass changes based on available prey and environmental conditions.
        current_temp (float): Current temperature in Celsius
        current_food (float): Current food intake in kg/day (can be None to use available prey)
        """
        current_temp = self.plot.get_temperature() if current_temp is None else current_temp
        current_food = self.total_available_prey_mass() if current_food is None else current_food

        # penalties range from 0 (ideal) to -2 (bad)
        penalty_temp = self.distance_from_ideal(current_temp, self.ideal_temp_range)
        penalty_food = self.distance_from_ideal(current_food, self.ideal_food_range)
        penalty_avg = (penalty_temp + penalty_food) / 2

        base_growth_rate = self.ideal_growth_rate * (1 + penalty_avg)
        # Predators don't have consumption_rate like prey - they just grow or shrink based on conditions
        actual_growth_rate = base_growth_rate
        new_mass = self.total_mass + self.total_mass * actual_growth_rate
        self.total_mass = max(0, new_mass)  # Prevent negative mass
