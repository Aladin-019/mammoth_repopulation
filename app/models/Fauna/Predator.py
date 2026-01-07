from .Fauna import Fauna
from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation

class Predator(Fauna):
    """
    Represents a predator in the ecosystem.
    Inherits from Fauna and adds predator specific update mass calculations.
    """

    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_temp_range: Tuple[float, float], min_food_per_day: float, ideal_growth_rate: float, 
                 feeding_rate: float, avg_steps_taken: float, avg_foot_area: float, plot: PlotInformation, prey: List['Fauna']):
        
        super().__init__(name, description, population, avg_mass, ideal_growth_rate, ideal_temp_range, 
                        min_food_per_day, feeding_rate, avg_steps_taken, avg_foot_area, plot)
        
        self._validate_instance(prey, list, "prey")
        self._validate_list(prey, "prey", Fauna)
        
        self.prey = prey  # prey that this predator consumes

    def total_available_prey_mass(self) -> float:
        """
        Calculate the total available mass of all prey that this predator consumes.
        Only prey present on the plot are considered. Assumes only one of each kind of fauna on the plot.
        """
        total_mass = 0.0
        plot_fauna = self.plot.get_all_fauna()
        # Build a lookup for plot fauna by name (assume only one of each kind)
        fauna_by_name = {fauna.get_name(): fauna for fauna in plot_fauna}
        for prey in self.prey:
            prey_name = prey.get_name()
            if prey_name in fauna_by_name:
                plot_prey = fauna_by_name[prey_name]
                total_mass += plot_prey.get_total_mass()
        return total_mass

    def update_predator_mass(self, day: int) -> float:
        """
        Update the total mass of the predator based on current environmental conditions.
        Predator mass changes based on available prey and environmental conditions.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        try:
            environmental_conditions = self._get_current_environmental_conditions(day)
            
            environmental_penalty = self._calculate_environmental_penalty(environmental_conditions)
            
            base_growth_rate = self._calculate_base_growth_rate(environmental_penalty)
            
            self._update_mass_from_growth(base_growth_rate)

            self.capacity_penalty()

        except Exception as e:
            raise RuntimeError(f"Error updating predator mass: {e}")

    def _get_current_environmental_conditions(self, day: int) -> dict:
        """
        Get current environmental conditions from the plot.
        
        Returns:
            dict: Dictionary containing current environmental values
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        current_temp = self.plot.get_current_temperature(day)
        current_food = self.total_available_prey_mass()
        
        return {
            'temperature': current_temp,
            'food': current_food
        }

    def _calculate_environmental_penalty(self, environmental_conditions: dict) -> float:
        """
        Calculate the average environmental penalty based on current conditions.
        
        Args:
            environmental_conditions (dict): Current environmental values
        Returns:
            float: Average penalty from 0 (ideal) to -2 (worst)
        """
        self._validate_instance(environmental_conditions, dict, "environmental_conditions")
        self._validate_not_none(environmental_conditions, "environmental_conditions")
        
        penalty_temp = self.distance_from_ideal(
            environmental_conditions['temperature'],
            self.ideal_temp_range)
        penalty_food = self.distance_from_min_food(
            environmental_conditions['food'])

        penalty_avg = (penalty_temp + penalty_food) / 2
        
        return penalty_avg

    def _calculate_base_growth_rate(self, environmental_penalty: float) -> float:
        """
        Calculate the base growth rate adjusted for environmental conditions.
        
        Args:
            environmental_penalty (float): Environmental penalty from 0 to -1
        Returns:
            float: Adjusted base growth rate
        """
        self._validate_instance(environmental_penalty, float, "environmental_penalty")
        
        return self.ideal_growth_rate * (1 + environmental_penalty/2)

    def _update_mass_from_growth(self, base_growth_rate: float) -> None:
        """
        Update the predator mass based on growth rate.
        Predators don't have consumption_rate like prey - they just grow or shrink based on conditions.
        
        Args:
            base_growth_rate (float): The base growth rate
        """
        self._validate_instance(base_growth_rate, float, "base_growth_rate")

        actual_growth_rate = base_growth_rate
        current_mass = self.get_total_mass()
        new_mass = current_mass + current_mass * actual_growth_rate
        
        self.set_total_mass(max(0, new_mass))  # Prevent negative mass
        
        # Update population
        if self.avg_mass > 0:
            new_population = int(new_mass / self.avg_mass)
            self.population = max(0, new_population)

    def capacity_penalty(self) -> None:
        """
        Apply a penalty to predator mass if the plot is over predator capacity.
        Predator populations are limited by available prey and space.
        
        Precondition: calculate_fauna_masses() must be called first (for current timestep)
        """
        if self.plot.over_predator_capacity():
            self.set_total_mass(self.get_total_mass() * 0.8)    # Reduce mass by 20% if over predator capacity


