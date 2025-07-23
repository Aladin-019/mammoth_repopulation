from app.models.Fauna import Fauna
from app.models.Flora import Flora
from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation

class Prey(Fauna):
    """
    Represents a prey in the ecosystem.
    Inherits from Fauna and adds specific prey behaviors.
    """

    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_temp_range: Tuple[float, float], ideal_food_range: Tuple[float, float], ideal_growth_rate: float, 
                 feeding_rate: float, avg_steps_taken: int, avg_feet_area: float, plot: PlotInformation, predators: List['Fauna']):
        super().__init__(name, description, population, avg_mass, ideal_temp_range, ideal_food_range, 
                        ideal_growth_rate, feeding_rate, avg_steps_taken, avg_feet_area, plot)
        self.predators = predators  # predators of this prey
        self.consumable_flora = []  # flora that this prey consumes

    def total_consumption_rate(self) -> float:
        """
        Calculate the total consumption rate of all predators that depend on this prey.
        Only predators present on the plot are considered.
        """
        total_rate = 0.0
        plot_fauna = self.plot.get_all_fauna()

        for predator in self.predators:
            for fauna in plot_fauna:
                if fauna.get_name() == predator.get_name():
                    total_rate += fauna.population * fauna.get_feeding_rate()
                    break

        return total_rate

    def total_available_flora_mass(self) -> float:
        """
        Calculate the total available flora mass that this prey can consume.
        Only flora present on the plot are considered.
        """
        total_mass = 0.0
        plot_flora = self.plot.get_all_flora()

        for flora in self.consumable_flora:
            for plot_flora_item in plot_flora:
                if flora.get_name() == plot_flora_item.get_name():
                    total_mass += plot_flora_item.get_total_mass()
                    break

        return total_mass

    def update_prey_mass(self, current_temp: float, current_food: float) -> float:
        """
        Update the total mass of the prey based on current environmental conditions.
        Prey mass decreases due to being consumed by predators.
        current_temp (float): Current temperature in Celsius
        current_food (float): Current food intake in kg/day
        """
        current_temp = self.plot.get_temperature() if current_temp is None else current_temp
        current_food = self.total_available_flora_mass() if current_food is None else current_food

        # penalties range from 0 (ideal) to -2 (bad)
        penalty_temp = self.distance_from_ideal(current_temp, self.ideal_temp_range)
        penalty_food = self.distance_from_ideal(current_food, self.ideal_food_range)
        penalty_avg = (penalty_temp + penalty_food) / 2

        base_growth_rate = self.ideal_growth_rate * (1 + penalty_avg)
        consumption_rate = self.total_consumption_rate()  # How much predators consume
        actual_growth_rate = base_growth_rate - consumption_rate
        new_mass = self.total_mass + self.total_mass * actual_growth_rate
        self.total_mass = max(0, new_mass)  # Prevent negative mass
