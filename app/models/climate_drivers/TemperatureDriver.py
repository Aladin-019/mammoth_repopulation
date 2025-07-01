import numpy as np
import logging

class TemperatureDriver:
    """
        Simulates daily temperature using mean and variance data for each location and day.

        Attributes:
        temp_data (dict): { location: { day: (mean, variance) } }
        """
    def __init__ (self, temp_data):
        """
        temp_data (dict): Nested dict of temperature stats per location and day.
        """
        self.temp_data = temp_data

    def generate_daily_temp(self, location, day, biome_offset=0.0):
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        biome_offset (float): Mean temperature adjustment (default 0.0).

        returns:
            float: Simulated daily temperature for the given location and day.
        """
        if location not in self.temp_data:
            logging.error(f"Location {location} not found in temperature data")
            return None

        if day < 0 or day >= len(self.temp_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day    
        temp_data_tuple = self.temp_data[location][day]

        if temp_data_tuple is None:
            logging.error(f"Missing temperature data tuple (mean, var) for {location} on day {day}")
            return None
        
        # Unpack mean and variance
        mean, var = temp_data_tuple

        if mean is None or var is None:
            logging.error(f"Missing temperature data mean: {mean} or var: {var} for {location} on day {day}")
            return None
            
        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        return np.random.normal(mean + biome_offset, np.sqrt(var))