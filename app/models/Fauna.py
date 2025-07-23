# Fauna class represents a flora species within the plot.
# Each Plot will have all Fauna classes that are present in the plot.
# A Fauna class has ideal environmental ranges (i.e. temperature, food, etc)
# The health and survival of the fauna will depend on the distance of the
# current environmental conditions to the ideal ranges.

from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation

class Fauna:
    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_temp_range: Tuple[float, float], ideal_food_range: Tuple[float, float], ideal_growth_rate: float, 
                 feeding_rate: float, avg_steps_taken: int, avg_feet_area: float, plot: PlotInformation):
        """
        Represents a fauna species.
        Ideal ranges for temperature, hydration, and food intake
        are to determine the conditions for optimal growth or potential death.
        """
        self.name = name
        self.description = description
        self.population = population                   # Number of individuals in the species
        self.avg_mass = avg_mass                       # One animal mass in kg
        self.total_mass = avg_mass * population        # Total mass kg
        self.ideal_growth_rate = ideal_growth_rate     # kg/day
        self.feeding_rate = feeding_rate               # kg/day
        self.ideal_temp_range = ideal_temp_range       # Celsius
        self.ideal_food_range = ideal_food_range       # Food consumption kg/day
        self.avg_steps_taken = avg_steps_taken         # Average steps taken per day
        self.avg_feet_area = avg_feet_area             # Average area of feet in cm^2
        self.plot = plot                               # The plot this fauna is associated with

        assert population >= 0, "population must be non-negative"
        assert avg_mass > 0, "avg_mass must be positive"
        assert ideal_growth_rate >= 0, "ideal_growth_rate must be non-negative"
        assert plot is not None, "plot must be provided"
        assert isinstance(plot, PlotInformation), "plot must be an instance of PlotInformation"
        assert feeding_rate > 0, "feeding_rate must be positive"
        assert avg_steps_taken >= 0, "avg_steps_taken must be non-negative"
        assert avg_feet_area > 0, "avg_feet_area must be positive"

        assert ideal_temp_range[0] <= ideal_temp_range[1], "ideal_temp_range must be in (min, max) order"
        assert ideal_food_range[0] <= ideal_food_range[1], "ideal_food_range must be in (min, max) order"
        
    def get_name(self) -> str:
        """
        Returns the name of the fauna species.
        """
        return self.name
    
    def get_description(self) -> str:
        """
        Returns the description of the fauna species.
        """
        return self.description

    def get_population(self) -> int:
        """
        Returns the population of the fauna species.
        """
        return self.population
    
    def get_total_mass(self) -> float:
        """
        Returns the total mass of the fauna species.
        """
        return self.total_mass
    
    def get_feeding_rate(self) -> float:
        """
        Returns the feeding rate of the fauna species.
        """
        return self.feeding_rate

    def distance_from_ideal(self, current_value: float, ideal_range: tuple) -> float:
        """
        Calculate the distance of the current value from the ideal range.
        current_value (float): The current environmental value
        ideal_range (tuple): A tuple representing the ideal range (min, max)
        Returns:
            float: The distance from the ideal range (-2 - 0), 0 being ideal, -2 being farthest from ideal.

        The reason for capping at -2 is to satisfy a (-1, 1) range for the penalty applied to ideal growth rate
        in the following formula of Flora.update_flora_mass():
        base_growth_rate = self.ideal_growth_rate * (1 + penalty_avg)
        """
        min, max = ideal_range
        if min == max:
            return 0  # Avoid division by zero 

        mid = (min + max) / 2
        width = (max - min) / 2

        if min <= current_value <= max:
            return 0.0  # Ideal

        # How far from center in units of "ideal range width"
        normalized_distance = (abs(current_value - mid) / width)
        return -min(normalized_distance, 2.0)  # Cap distance at 2.0



    
    