
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

    def total_available_food(self) -> float:
        """
        Calculate the total available food from all prey that this predator consumes.
        Only prey present on the plot are considered.
        """
        total_food = 0.0
        plot_fauna = self.plot.get_all_fauna()

        for prey in self.prey:
            for fauna in plot_fauna:
                if prey.get_name() == fauna.get_name():
                    total_food += fauna.get_total_mass()

        return total_food
