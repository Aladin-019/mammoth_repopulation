from app.models.Fauna import Fauna
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

    def total_consumption_rate(self) -> float:
        """
        Calculate the total consumption rate of all predators that depend on this flora.
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
