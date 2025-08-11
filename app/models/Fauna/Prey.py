from .Fauna import Fauna
from typing import List, Tuple
from app.interfaces.plot_info import PlotInformation

class Prey(Fauna):
    """
    Represents a prey in the ecosystem.
    Inherits from Fauna and has prey specific update mass calculations.
    """

    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_temp_range: Tuple[float, float], ideal_food_range: Tuple[float, float], ideal_growth_rate: float, 
                 feeding_rate: float, avg_steps_taken: int, avg_feet_area: float, plot: PlotInformation, predators: List['Fauna'],
                 consumable_flora: List['Flora']):
        
        super().__init__(name, description, population, avg_mass, ideal_growth_rate, ideal_temp_range, 
                        ideal_food_range, feeding_rate, avg_steps_taken, avg_feet_area, plot)
        
        self._validate_instance(predators, list, "predators")
        self._validate_list(predators, "predators", Fauna)

        self._validate_instance(consumable_flora, list, "consumable_flora")
        from app.models.Flora.Flora import Flora
        self._validate_list(consumable_flora, "consumable_flora", Flora)
        
        self.predators = predators  # predators of this prey
        self.consumable_flora = consumable_flora  # flora that this prey consumes

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

    def update_prey_mass(self, day: int) -> float:
        """
        Update the total mass of the prey based on current environmental conditions.
        Prey mass decreases due to being consumed by predators.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")

        try:
            environmental_conditions = self._get_current_environmental_conditions(day)
            
            environmental_penalty = self._calculate_environmental_penalty(environmental_conditions)
            
            base_growth_rate = self._calculate_base_growth_rate(environmental_penalty)
            consumption_rate = self.total_consumption_rate()
            
            self._update_mass_from_growth_and_consumption(base_growth_rate, consumption_rate)

            self.capacity_penalty()

        except Exception as e:
            raise RuntimeError(f"Failed to update prey mass: {e}")

    def _get_current_environmental_conditions(self, day: int) -> dict:
        """
        Get current environmental conditions from the plot.
        
        Args:
            day (int): The day to get environmental conditions for
        Returns:
            dict: Dictionary containing current environmental values
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        current_temp = self.plot.get_current_temperature(day)
        current_food = self.total_available_flora_mass()
        
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
            self.ideal_temp_range
        )
        penalty_food = self.distance_from_ideal(
            environmental_conditions['food'], 
            self.ideal_food_range
        )
        
        penalty_avg = (penalty_temp + penalty_food) / 2
        return penalty_avg

    def _calculate_base_growth_rate(self, environmental_penalty: float) -> float:
        """
        Calculate the base growth rate adjusted for environmental conditions.
        
        Args:
            environmental_penalty (float): Environmental penalty from 0 to -2
        Returns:
            float: Adjusted base growth rate
        """
        self._validate_instance(environmental_penalty, float, "environmental_penalty")
        
        return self.ideal_growth_rate * (1 + environmental_penalty)

    def _update_mass_from_growth_and_consumption(self, base_growth_rate: float, consumption_rate: float) -> None:
        """
        Update mass based on growth rate and consumption rate.
        
        Args:
            base_growth_rate (float): The base growth rate to apply
            consumption_rate (float): The consumption rate to apply
        """
        self._validate_instance(base_growth_rate, float, "base_growth_rate")
        self._validate_instance(consumption_rate, float, "consumption_rate")
        
        actual_growth_rate = base_growth_rate - consumption_rate
        new_mass = self.get_total_mass() + self.get_total_mass() * actual_growth_rate
        self.set_total_mass(new_mass)  # Setter will cap at 0

    def capacity_penalty(self) -> None:
        """
        Apply a penalty to prey mass if the plot is over prey capacity.
        Prey populations are limited by available food and space.
        
        Precondition: calculate_fauna_masses() must be called first (for current timestep)
        """
        if self.plot.over_prey_capacity():
            self.set_total_mass(self.get_total_mass() * 0.9)    # Reduce mass by 10% if over prey capacity
    

