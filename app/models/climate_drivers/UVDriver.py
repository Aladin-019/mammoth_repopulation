import numpy as np
import logging
from typing import Optional

class UVDriver:
    """
        Simulates daily UV index using mean and variance data for each location and day.

        Attributes:
        uv_data (dict): { location: { day: (mean, variance) } }
        """
    def __init__ (self, uv_data: dict):
        """
        uv_data (dict): Nested dict of UV stats per location and day.
        """
        self.uv_data = uv_data

    def generate_daily_uv(self, location: str, day: int, offset: float = 0.0) -> Optional[float]:
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        offset (float): Mean UV adjustment (default 0.0).

        returns:
            float: Simulated daily UV for the given location and day.
        """
        if location not in self.uv_data:
            logging.error(f"Location {location} not found in UV data")
            return None
            
        if day < 0 or day >= len(self.uv_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day    
        uv_data_tuple = self.uv_data[location][day]
        
        if uv_data_tuple is None:
            logging.error(f"Missing UV data tuple (mean, var) for {location} on day {day}")
            return None
        
        # Unpack mean and variance
        mean, var = uv_data_tuple
        
        if mean is None or var is None:
            logging.error(f"Missing UV data mean: {mean} or var: {var} for {location} on day {day}")
            return None
            
        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        result = np.random.normal(mean + offset, np.sqrt(var))
        
        # Ensure UV is never negative (UV index cannot be negative)
        return max(0.0, result)