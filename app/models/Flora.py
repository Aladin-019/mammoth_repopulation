# Flora class represents a flora species within the plot.
# Each Plot will have all Flora classes that are present in the plot.
# A Flora class has ideal environmental ranges (i.e. temperature, UV index, etc)
# The health and survival of the flora will depend on the distance of the
# current environmental conditions to the ideal ranges.

from app.models.Fauna import Fauna
from typing import List, Tuple
from app.interfaces.flora_plot_info import FloraPlotInformation


class Flora():
    def __init__(self, name: str, description: str, total_mass: float,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List[Fauna], root_depth: int,
                 plot: FloraPlotInformation):
        """
        Represents a flora species.
        Ideal ranges for temperature, UV index, hydration, and soil temperature
        are to determine the conditions for optimal growth or potential death.
        """
        assert 1 <= root_depth <= 4, "root_depth must be between 1 and 4"
        assert total_mass >= 0, "total_mass must be non-negative"
        assert ideal_growth_rate >= 0, "ideal_growth_rate must be non-negative"
        assert 0 <= ideal_uv_range[0] <= 15 and 0 <= ideal_uv_range[1] <= 15, "UV index should be between 0 and 15"
        assert isinstance(consumers, list), "consumers must be a list"

        assert ideal_temp_range[0] <= ideal_temp_range[1], "ideal_temp_range must be in (min, max) order"
        assert ideal_uv_range[0] <= ideal_uv_range[1], "ideal_uv_range must be in (min, max) order"
        assert ideal_hydration_range[0] <= ideal_hydration_range[1], "ideal_hydration_range must be in (min, max) order"
        assert ideal_soil_temp_range[0] <= ideal_soil_temp_range[1], "ideal_soil_temp_range must be in (min, max) order"

        self.name = name
        self.description = description
        self.total_mass = total_mass                 # Total mass kg
        self.ideal_growth_rate = ideal_growth_rate   # kg/day
        self.ideal_temp_range = ideal_temp_range     # Celsius
        self.ideal_uv_range = ideal_uv_range         # UV index
        self.ideal_hydration_range = ideal_hydration_range  # kg/day
        self.ideal_soil_temp_range = ideal_soil_temp_range  # Celsius
        self.consumers = consumers                   # List of (Fauna) consumers that depend on this flora
        self.root_depth = root_depth                 # Depth of the roots by soil depth level (1-4)
        self.plot = plot                             # The plot this flora is associated with

    def get_name(self) -> str:
        """
        Returns the name of the flora species.
        """
        return self.name
    
    def get_description(self) -> str:
        """
        Returns the description of the flora species.
        """
        return self.description
    
    def get_total_mass(self) -> float:
        """
        Returns the total mass of the flora species.
        """
        return self.total_mass

    def update_flora_mass(self, current_temp: float, current_uv: float,
                             current_hydration: float, current_soil_temp: float) -> float:
        """
        Update the mass of the flora based on the current environmental conditions.
        The mass is adjusted
        based on the distance from the ideal ranges for temperature, UV index,
        hydration, and soil temperature.
        current_temp (float): Current temperature in Celsius
        current_uv (float): Current UV index
        current_hydration (float): Current hydration in kg/day
        current_soil_temp (float): Current soil temperature in Celsius
        """

         # Each returns a negative number or 0
        temp_factor = self.distance_from_ideal(current_temp, self.ideal_temp_range)
        uv_factor = self.distance_from_ideal(current_uv, self.ideal_uv_range)
        hydration_factor = self.distance_from_ideal(current_hydration, self.ideal_hydration_range)
        soil_temp_factor = self.distance_from_ideal(current_soil_temp, self.ideal_soil_temp_range)

        # Average penalty, it ranges from 0 (ideal) to -2 (bad)
        penalty_avg = (temp_factor + uv_factor + hydration_factor + soil_temp_factor) / 4

        # Modify ideal growth rate by penalty
        base_growth_rate = self.ideal_growth_rate * (1 + penalty_avg)

        # Consumption from consumers
        consumption_rate = self.total_consumption_rate()

        # Net growth
        actual_growth_rate = base_growth_rate - consumption_rate
        new_mass = self.total_mass + self.total_mass * actual_growth_rate

        self.total_mass = max(0, new_mass)  # Prevent negative mass

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
        min_val, max_val = ideal_range
        if min_val == max_val:
            return 0  # Avoid division by zero

        mid = (min_val + max_val) / 2
        width = (max_val - min_val) / 2

        if min_val <= current_value <= max_val:
            return 0.0  # Ideal

        # How far from center in units of "ideal range width"
        normalized_distance = (abs(current_value - mid) / width)
        return -min(normalized_distance, 2.0)  # Cap distance at 2.0
    

    def total_consumption_rate(self) -> float:
        """
        Calculate the total consumption rate of all consumers that depend on this flora.
        Only consumers present on the plot are considered.
        """
        total_rate = 0.0
        plot_fauna = self.plot.get_all_fauna()

        for consumer in self.consumers:
            for fauna in plot_fauna:
                if fauna.get_name() == consumer.get_name():
                    total_rate += fauna.population * fauna.get_feeding_rate()
                    break

        return total_rate
