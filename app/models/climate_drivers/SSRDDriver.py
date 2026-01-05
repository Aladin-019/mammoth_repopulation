import numpy as np
import logging
from typing import Optional

class SSRDDriver:
    """
        Simulates daily surface solar radiation downwards (SSRD) using mean and variance data 
        for each location and day.

        Attributes:
        srd_data (dict): { location: { day: (mean, variance) } }
        """
    def __init__ (self, srd_data: dict):
        """
        srd_data (dict): Nested dict of srd stats per location and day.
        """
        self.srd_data = srd_data

    def generate_daily_srd(self, location: str, day: int, offset: float = 0.0) -> Optional[float]:
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        offset (float): Mean srd adjustment (default 0.0).

        returns:
            float: Simulated daily srd for the given location and day.
        """
        if location not in self.srd_data:
            logging.error(f"Location {location} not found in srd data")
            return None

        if day < 0 or day >= len(self.srd_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day
        srd_data_tuple = self.srd_data[location][day]

        if srd_data_tuple is None:
            logging.error(f"Missing srd data tuple (mean, var) for {location} on day {day}")
            return None
        
        # Unpack mean and variance
        mean, var = srd_data_tuple

        if mean is None or var is None:
            logging.error(f"Missing srd data mean: {mean} or var: {var} for {location} on day {day}")
            return None
            
        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        result = np.random.normal(mean + offset, np.sqrt(var))
        
        # Ensure SSRD is never negative (solar radiation cannot be negative)
        return max(0.0, result)