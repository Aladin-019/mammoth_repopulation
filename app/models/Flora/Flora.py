import logging
from ..Fauna import Fauna
from typing import List, Tuple, Union
from app.interfaces.flora_plot_info import FloraPlotInformation

logger = logging.getLogger(__name__)

class Flora():
    """
    Represents a flora species.
    Ideal ranges for temperature, UV index, hydration, and soil temperature
    are to determine the conditions for optimal growth or potential death.
    """
    
    @staticmethod
    def _validate_string(value: str, name: str, allow_empty: bool = False) -> None:
        """
        Validate that a value is a non-empty string.
        
        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.
            allow_empty: Whether empty strings are allowed.
        Raises:
            ValueError: If value is not a valid string.
        """
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string, got: {type(value)}")
        
        if not allow_empty and not value.strip():
            raise ValueError(f"{name} cannot be empty")
    
    @staticmethod
    def _validate_positive_number(value: Union[int, float], name: str, allow_zero: bool = True) -> None:
        """
        Validate that a value is a positive number.
        
        Args:
            value: The value to validate
            name: The name of the parameter for error messages
            allow_zero: Whether zero is allowed
        Raises:
            ValueError: If value is not a valid positive number
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got: {type(value)}")
        
        if allow_zero and value < 0:
            raise ValueError(f"{name} must be non-negative, got: {value}")
        elif not allow_zero and value <= 0:
            raise ValueError(f"{name} must be positive, got: {value}")
    
    @staticmethod
    def _validate_range_tuple(value: Tuple[float, float], name: str) -> None:
        """
        Validate that a value is a properly ordered range tuple.
        
        Args:
            value: The tuple to validate.
            name: The name of the parameter for error messages.
        Raises:
            ValueError: If value is not a valid range tuple.
        """
        if not isinstance(value, tuple) or len(value) != 2:
            raise TypeError(f"{name} must be a tuple of 2 values, got: {value}")
        
        if not all(isinstance(x, (int, float)) for x in value):
            raise ValueError(f"{name} must contain only numbers, got: {value}")
        
        if value[0] > value[1]:
            raise ValueError(f"{name} must be in (min, max) order, got: {value}")
    
    @staticmethod
    def _validate_integer_range(value: int, name: str, min_val: int, max_val: int) -> None:
        """
        Validate that a value is an integer within a specified range.
        
        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.
            min_val: Minimum allowed value
            max_val: Maximum allowed value
        Raises:
            ValueError: If value is not a valid integer in range.
        """
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer, got: {type(value)}")
        
        if value < min_val or value > max_val:     # inclusive range
            raise ValueError(f"{name} must be between {min_val} and {max_val}, got: {value}")
    
    @staticmethod
    def _validate_list(value: List, name: str, element_type: type = None) -> None:
        """
        Validate that a value is a list with optional element type checking.
        
        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.
            element_type: Expected type for list elements (optional).
        Raises:
            ValueError: If value is not a valid list.
        """
        if not isinstance(value, list):
            raise TypeError(f"{name} must be a list, got: {type(value)}")
        
        if element_type and not all(isinstance(item, element_type) for item in value):
            raise ValueError(f"{name} must contain only {element_type.__name__} objects")
    
    @staticmethod
    def _validate_not_none(value, name: str) -> None:
        """
        Validate that a value is not None.
        
        Args:
            value: The value to validate
            name: The name of the parameter for error messages
        Raises:
            ValueError: If value is None
        """
        if value is None:
            raise ValueError(f"{name} must be provided")
    
    @staticmethod
    def _validate_instance(value, expected_type: type, name: str) -> None:
        """
        Validate that a value is an instance of the expected type.
        
        Args:
            value: The value to validate.
            expected_type: The expected type.
            name: The name of the parameter for error messages.
        Raises:
            TypeError: If value is not the expected type.
        """
        if not isinstance(value, expected_type):
            raise TypeError(f"{name} must be an instance of {expected_type.__name__}, got: {type(value)}")
    
    def __init__(self, name: str, description: str, total_mass: float, population: int,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List[Fauna], root_depth: int,
                 plot: FloraPlotInformation):
        """
        Represents a flora species.
        Ideal ranges for temperature, UV index, hydration, and soil temperature
        are to determine the conditions for optimal growth or potential death.
        
        Args:
            name (str): Name of the flora species.
            description (str): Description of the flora species.
            total_mass (float): Total mass in kg.
            population (int): Population count.
            ideal_growth_rate (float): Ideal growth rate in kg/day.
            ideal_temp_range (Tuple[float, float]): Ideal temperature range in Celsius.
            ideal_uv_range (Tuple[float, float]): Ideal UV index range.
            ideal_hydration_range (Tuple[float, float]): Ideal hydration range in kg/day.
            ideal_soil_temp_range (Tuple[float, float]): Ideal soil temperature range in Celsius.
            consumers (List[Fauna]): List of fauna that consume this flora.
            root_depth (int): Root depth level (1-4).
            plot (FloraPlotInformation): The plot this flora is associated with.
            
        Raises:
            ValueError: If any input parameters are invalid.
            TypeError: If any input parameters have incorrect types.
        """
        self._validate_instance(name, str, "name")
        self._validate_string(name, "name")
        
        self._validate_instance(description, str, "description")
        self._validate_string(description, "description", allow_empty=True)
        
        self._validate_instance(total_mass, float, "total_mass")
        self._validate_positive_number(total_mass, "total_mass")
        
        self._validate_instance(population, int, "population")
        self._validate_positive_number(population, "population")
        
        self._validate_instance(ideal_growth_rate, float, "ideal_growth_rate")
        self._validate_positive_number(ideal_growth_rate, "ideal_growth_rate")
        
        self._validate_instance(ideal_temp_range, tuple, "ideal_temp_range")
        self._validate_range_tuple(ideal_temp_range, "ideal_temp_range")
        
        self._validate_instance(ideal_uv_range, tuple, "ideal_uv_range")
        self._validate_range_tuple(ideal_uv_range, "ideal_uv_range")
        
        self._validate_instance(ideal_hydration_range, tuple, "ideal_hydration_range")
        self._validate_range_tuple(ideal_hydration_range, "ideal_hydration_range")
        
        self._validate_instance(ideal_soil_temp_range, tuple, "ideal_soil_temp_range")
        self._validate_range_tuple(ideal_soil_temp_range, "ideal_soil_temp_range")
        
        self._validate_instance(consumers, list, "consumers")
        self._validate_list(consumers, "consumers", Fauna)
        
        self._validate_instance(root_depth, int, "root_depth")
        self._validate_integer_range(root_depth, "root_depth", 1, 4)
        
        self._validate_not_none(plot, "plot")
        self._validate_instance(plot, FloraPlotInformation, "plot")
        
        try:
            self.name = name
            self.description = description
            self.total_mass = float(total_mass)             
            self.population = population                 
            self.ideal_growth_rate = float(ideal_growth_rate)   
            self.ideal_temp_range = ideal_temp_range     
            self.ideal_uv_range = ideal_uv_range         
            self.ideal_hydration_range = ideal_hydration_range 
            self.ideal_soil_temp_range = ideal_soil_temp_range 
            self.consumers = consumers                   
            self.root_depth = root_depth                 
            self.plot = plot                             
                        
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Flora {name}: {e}")

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description

    def get_total_mass(self) -> float:
        return self.total_mass
    
    def update_flora_mass(self, day: int) -> None:
        """
        Update the mass of the flora based on the current environmental conditions.
        The mass is adjusted based on the distance from the ideal ranges for temperature, UV index,
        hydration, and soil temperature.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        environmental_conditions = self._get_current_environmental_conditions(day)

        environmental_penalty = self._calculate_environmental_penalty(environmental_conditions)
        
        base_growth_rate = self._calculate_base_growth_rate(environmental_penalty)
        consumption_rate = self.total_consumption_rate()
        
        # update mass for this timestep
        self._update_mass_from_growth_and_consumption(base_growth_rate, consumption_rate)

    def _get_current_environmental_conditions(self, day: int) -> dict:
        """
        Get current environmental conditions from the plot.
        
        Returns:
            dict: Dictionary containing current environmental values
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        current_temp = self.plot.get_current_temperature(day)
        current_uv = self.plot.get_current_uv(day)
        current_rainfall = self.plot.get_current_rainfall(day)
        current_melt_water_mass = self.plot.get_current_melt_water_mass(day)
        current_hydration = current_rainfall + current_melt_water_mass
        current_soil_temp = self.plot.get_current_soil_temp(day)

        return {
            'temperature': current_temp,
            'uv': current_uv,
            'hydration': current_hydration,
            'soil_temperature': current_soil_temp
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
        penalty_uv = self.distance_from_ideal(
            environmental_conditions['uv'], 
            self.ideal_uv_range
        )
        penalty_hydration = self.distance_from_ideal(
            environmental_conditions['hydration'], 
            self.ideal_hydration_range
        )
        penalty_soil_temp = self.distance_from_ideal(
            environmental_conditions['soil_temperature'], 
            self.ideal_soil_temp_range
        )
        
        # average penalty
        penalty_avg = (penalty_temp + penalty_uv + penalty_hydration + penalty_soil_temp) / 4
        return penalty_avg

    def _calculate_base_growth_rate(self, environmental_penalty: float) -> float:
        """
        Calculate the base growth rate adjusted for environmental conditions in kg/day.
        
        Args:
            environmental_penalty (float): Environmental penalty from 0 to -2,
                which is used to adjust ideal growth rate between -1 and 1.
        Returns:
            float: Adjusted base growth rate in kg/day
        """
        self._validate_instance(environmental_penalty, float, "environmental_penalty")
        
        return self.ideal_growth_rate * (1 + environmental_penalty)

    def _update_mass_from_growth_and_consumption(self, base_growth_rate: float, consumption_rate: float) -> None:
        """
        Update the flora mass in kg based on growth and consumption rates in kg/day.
        
        Args:
            base_growth_rate (float): The base growth rate
            consumption_rate (float): The consumption rate by fauna
        """
        self._validate_instance(base_growth_rate, float, "base_growth_rate")
        self._validate_instance(consumption_rate, float, "consumption_rate")
        
        actual_growth_rate = base_growth_rate - consumption_rate
        new_mass = self.total_mass + self.total_mass * actual_growth_rate
        self.total_mass = max(0, new_mass)  # Prevent negative mass

    def _apply_canopy_shading(self, environmental_conditions: dict) -> dict:
        """
        Apply canopy shading effect to reduce UV available to flora.
        Trees override this method to return unmodified conditions.
        
        Args:
            environmental_conditions (dict): Current environmental values   
        Returns:
            dict: Environmental conditions with reduced UV due to canopy shading
        """
        self._validate_instance(environmental_conditions, dict, "environmental_conditions")
        self._validate_not_none(environmental_conditions, "environmental_conditions")
        
        total_canopy_cover = self._get_total_plot_canopy_cover()
        plot_area = self.plot.get_plot_area()
        
        canopy_coverage_ratio = min(total_canopy_cover / plot_area, 1.0)
        
        new_uv = environmental_conditions['uv'] * canopy_coverage_ratio
        
        shaded_conditions = environmental_conditions.copy()
        shaded_conditions['uv'] = new_uv
        
        return shaded_conditions

    def _get_total_plot_canopy_cover(self) -> float:
        """
        Calculate the total canopy cover from all trees on the plot in km^2.
        
        Returns:
            float: Total canopy cover in square kilometers
        """
        total_canopy_cover = 0.0
        all_flora = self.plot.get_all_flora()
        
        for flora in all_flora:
            if hasattr(flora, 'get_Tree_canopy_cover'):  # Is a tree
                total_canopy_cover += flora.get_Tree_canopy_cover()
        
        return total_canopy_cover

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
        self._validate_instance(current_value, float, "current_value")
        self._validate_instance(ideal_range, tuple, "ideal_range")
        self._validate_range_tuple(ideal_range, "ideal_range")
        
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
        Calculate the total consumption rate of all consumers that depend on this flora in kg/day.
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
    
    def capacity_penalty(self) -> None:
        """
        Apply a penalty to the flora mass if the plot is over capacity for this specific flora type.
        This method should be overridden by flora subtypes to implement type-specific capacity checks.
        """
        # subclasses should override this
        pass
    

