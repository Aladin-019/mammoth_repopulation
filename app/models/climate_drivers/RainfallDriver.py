import numpy as np
import logging
from typing import Optional

class RainfallDriver:
    """
        Simulates daily rainfall using mean and variance data for each location and day.

        Attributes:
        rainfall_data (dict): { location: { day: (mean, variance) } }
        """
    def __init__ (self, rainfall_data: dict):
        """
        rainfall_data (dict): Nested dict of rainfall stats per location and day.
        """
        self.rainfall_data = rainfall_data

    def generate_daily_rainfall(self, location: str, day: int, offset: float = 0.0) -> Optional[float]:
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        offset (float): Mean rainfall adjustment (default 0.0).

        returns:
            float: Simulated daily rainfall for the given location and day.
        """
        if location not in self.rainfall_data:
            logging.error(f"Location {location} not found in rainfall data")
            return None

        if day < 0 or day >= len(self.rainfall_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day
        rainfall_data_tuple = self.rainfall_data[location][day]

        if rainfall_data_tuple is None:
            logging.error(f"Missing rainfall data tuple (mean, var) for {location} on day {day}")
            return None
        
        # Unpack mean and variance
        mean, var = rainfall_data_tuple

        if mean is None or var is None:
            logging.error(f"Missing rainfall data mean: {mean} or var: {var} for {location} on day {day}")
            return None
            
        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        result = np.random.normal(mean + offset, np.sqrt(var))
        
        # Ensure rainfall is never negative (rainfall cannot be negative)
        return max(0.0, result)