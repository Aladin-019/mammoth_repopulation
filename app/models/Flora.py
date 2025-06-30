# Flora class represents a flora species within the plot.
# Each Plot will have all Flora classes that are present in the plot.
# A Flora class has ideal environmental ranges (i.e. temperature, UV index, etc)
# The health and survival of the flora will depend on the distance of the
# current environmental conditions to the ideal ranges.

from app.models.Fauna import Fauna
from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation
from app.interfaces.flora_plot_info import FloraPlotInformation


class Flora(FloraPlotInformation):
    def __init__(self, name: str, description: str, total_mass: float,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List[Fauna], root_depth: int):
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

    def get_name(self) -> str:
        """
        Returns the name of the flora species.
        """
        return self.name

    def update_flora_mass(self, current_temp: float, current_uv: float,
                             current_hydration: float, current_soil_temp: float) -> float:
        """
        Update the mass of the flora based on the current environmental conditions.
        The mass is adjusted
        """

        temp_distance = self.distance_from_ideal_range(current_temp, self.ideal_temp_range)
        uv_distance = self.distance_from_ideal_range(current_uv, self.ideal_uv_range)
        hydration_distance = self.distance_from_ideal_range(current_hydration, self.ideal_hydration_range)
        soil_temp_distance = self.distance_from_ideal_range(current_soil_temp, self.ideal_soil_temp_range)

        # When climate values are in ideal range, distances will be 0 and wont affect the growth rate.
        # Environmental flora decay factors acounted for here.
        base_growth_rate = (self.ideal_growth_rate *
                            (temp_distance + uv_distance + hydration_distance + soil_temp_distance))
        
        consumption_rate = self.total_consumption_rate()   
        actual_growth_rate = base_growth_rate - consumption_rate   #kg/km^2/day (kg/plot/day)
        new_mass = self.total_mass + self.total_mass * actual_growth_rate

        self.total_mass = new_mass

    def distance_from_ideal_range(self, current_value: float, ideal_range: tuple) -> float:
        """
        Calculate the distance of the current value from the ideal range.
        current_value (float): The current environmental value
        ideal_range (tuple): A tuple representing the ideal range (min, max)
        Returns:
            float: The distance from the ideal range
        """
        if current_value < ideal_range[0]:
            return ideal_range[0] - current_value
        elif current_value > ideal_range[1]:
            return current_value - ideal_range[1]
        else:
            return 0

    def get_consumer_population(self, consumer: Fauna) -> int:
        """
        Get the population of a specific consumer species that depends on this flora.
        consumer (Fauna): The consumer species to check.
        """
        # Check if the consumer is in our consumers list
        is_consumer = False
        for c in self.consumers:
            if c.get_name() == consumer.get_name():
                is_consumer = True
                break
        
        if not is_consumer:
            return 0
            
        # Check if the consumer exists on the plot using interface method
        plot_fauna = self.get_all_fauna()
        for fauna in plot_fauna:
            if fauna.get_name() == consumer.get_name():
                return consumer.population
        
        return 0

    def total_consumption_rate(self) -> float:
        """
        Calculate the total consumption rate of all consumers that depend on this flora.
        """
        if not self.consumers:
            return 0.0  
        total_rate = sum(consumer.population * consumer.get_feeding_rate() for consumer in self.consumers)
        return total_rate

    def get_total_mass(self) -> float:
        """
        Returns the total mass of the flora species.
        """
        return self.total_mass

    # Abstract method implementations required by PlotInformation
    def get_temp(self) -> float:
        """
        Returns the current temperature. This would need to be implemented
        to get the actual temperature from the plot.
        """
        # This is a placeholder - in a real implementation, this would get the temperature from the plot
        return 0.0

    def get_all_fauna(self) -> list:
        """
        Returns all fauna on the plot. This would need to be implemented
        to get the actual fauna from the plot.
        """
        # This is a placeholder - in a real implementation, this would get fauna from the plot
        return []

    def get_all_flora(self) -> list:
        """
        Returns all flora on the plot. This would need to be implemented
        to get the actual flora from the plot.
        """
        # This is a placeholder - in a real implementation, this would get flora from the plot
        return []

    # Abstract method implementations required by FloraPlotInformation
    def get_rainfall(self) -> float:
        """
        Returns the current rainfall. This would need to be implemented
        to get the actual rainfall from the plot.
        """
        # This is a placeholder - in a real implementation, this would get rainfall from the plot
        return 0.0

    def get_snowfall(self) -> float:
        """
        Returns the current snowfall. This would need to be implemented
        to get the actual snowfall from the plot.
        """
        # This is a placeholder - in a real implementation, this would get snowfall from the plot
        return 0.0

    def get_uv_index(self) -> float:
        """
        Returns the current UV index. This would need to be implemented
        to get the actual UV index from the plot.
        """
        # This is a placeholder - in a real implementation, this would get UV index from the plot
        return 0.0