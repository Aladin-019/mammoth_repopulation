import logging
from typing import List, Tuple, Union
from app.interfaces.plot_info import PlotInformation

logger = logging.getLogger(__name__)

class Fauna():
    """
    Represents a fauna species.
    Ideal ranges for temperature and food availability
    are to determine the conditions for optimal growth or potential death.
    """
    
    @staticmethod
    def _validate_string(value: str, name: str, allow_empty: bool = False) -> None:
        """
        Validate that a value is a non-empty string.
        
        Args:
            value: The value to validate
            name: The name of the parameter for error messages
            allow_empty: Whether empty strings are allowed
        Raises:
            ValueError: If value is not a valid string
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
            value: The value to validate.
            name: The name of the parameter for error messages.
            allow_zero: Whether zero is allowed.
        Raises:
            ValueError: If value is not a valid positive number.
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
            value: The value to validate.
            name: The name of the parameter for error messages.    
        Raises:
            ValueError: If value is None.
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
    
    def __init__(self, name: str, description: str, population: int, avg_mass: float,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 min_food_per_day: float, feeding_rate: float,
                 avg_steps_taken: float, avg_feet_area: float, plot: PlotInformation):
        """
        Represents a fauna species.
        
        Args:
            name (str): Name of the fauna species.
            description (str): Description of the fauna species.
            population (int): Population count.
            avg_mass (float): Average mass per individual in kg.
            ideal_growth_rate (float): Ideal growth rate in kg/day.
            ideal_temp_range (Tuple[float, float]): Ideal temperature range in Celsius.
            min_food_per_day (float): Minimum food required per individual per day in kg.
            feeding_rate (float): Feeding rate in kg/day.
            avg_steps_taken (float): Average number of steps taken per day.
            avg_feet_area (float): Average area of feet in m^2.
            plot (PlotInformation): The plot this fauna is associated with.
            
        Raises:
            ValueError: If any input parameters are invalid.
            TypeError: If any input parameters have incorrect types.
        """
        self._validate_string(name, "name")
        self._validate_string(description, "description", allow_empty=True)
        
        self._validate_instance(population, int, "population")
        self._validate_positive_number(population, "population")
        
        self._validate_instance(avg_mass, float, "avg_mass")
        self._validate_positive_number(avg_mass, "avg_mass", allow_zero=True)
        
        self._validate_instance(ideal_growth_rate, float, "ideal_growth_rate")
        self._validate_positive_number(ideal_growth_rate, "ideal_growth_rate")
        
        self._validate_instance(ideal_temp_range, tuple, "ideal_temp_range")
        self._validate_range_tuple(ideal_temp_range, "ideal_temp_range")
        
        self._validate_instance(min_food_per_day, float, "min_food_per_day")
        self._validate_positive_number(min_food_per_day, "min_food_per_day", allow_zero=False)
        
        self._validate_instance(feeding_rate, float, "feeding_rate")
        self._validate_positive_number(feeding_rate, "feeding_rate", allow_zero=False)
        
        self._validate_instance(avg_steps_taken, float, "avg_steps_taken")
        self._validate_positive_number(avg_steps_taken, "avg_steps_taken")
        
        self._validate_instance(avg_feet_area, float, "avg_feet_area")
        self._validate_positive_number(avg_feet_area, "avg_feet_area", allow_zero=False)
        
        self._validate_not_none(plot, "plot")
        self._validate_instance(plot, PlotInformation, "plot")
        
        try:
            self.name = name
            self.description = description
            self.population = population
            self.avg_mass = float(avg_mass)
            self._total_mass = self.population * self.avg_mass
            self.ideal_growth_rate = float(ideal_growth_rate)
            self.ideal_temp_range = ideal_temp_range
            self.min_food_per_day = float(min_food_per_day)
            self.feeding_rate = float(feeding_rate)
            self.avg_steps_taken = float(avg_steps_taken)
            self.avg_feet_area = float(avg_feet_area)
            self.plot = plot
                        
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Fauna {name}: {e}")
    
    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description

    def get_population(self) -> int:
        return self.population
    
    def get_total_mass(self) -> float:
        return self._total_mass
    
    def set_total_mass(self, value: float):
        # Cap negative mass at 0
        self._total_mass = max(0.0, float(value))
    
    def get_feeding_rate(self) -> float:
        return self.feeding_rate
    
    def get_avg_steps_taken(self) -> float:
        return self.avg_steps_taken
    
    def get_avg_feet_area(self) -> float:
        return self.avg_feet_area

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
        
        min_val, max_val = ideal_range
        if min_val == max_val:
            return 0  # Avoid division by zero 

        mid = (min_val + max_val) / 2
        width = (max_val - min_val) / 2
        
        if min_val <= current_value <= max_val:
            return 0.0  # Ideal

        normalized_distance = (abs(current_value - mid) / width)
        return -min(normalized_distance, 1.0)  # Cap distance at -1.0

    def distance_from_min_food(self, current_food: float) -> float:
        """
        Calculate the penalty for food availability below the minimum required.
        Returns 0 if current_food >= min_food_per_day, else returns negative value proportional to shortage.
        Args:
            current_food (float): The current available food
        Returns:
            float: 0 if enough food, else negative value capped at -1.0
        """
        self._validate_instance(current_food, float, "current_food")
        min_food = self.min_food_per_day
        if current_food >= min_food:
            return 0.0
        shortage = min_food - current_food
        # Normalize penalty: -1.0 means zero food, 0 means enough food
        penalty = -min(shortage / min_food, 1.0) if min_food > 0 else 0.0
        return penalty

    def capacity_penalty(self) -> None:
        """
        Apply penalty to the fauna's total mass if plot is over capacity
        """
        pass
    

