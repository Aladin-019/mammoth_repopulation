import numpy as np
import logging

class SnowfallDriver:
    """
        Simulates daily snowfall using mean and variance data for each location and day.

        Attributes:
        snowfall_data (dict): { location: { day: (mean, variance) } }
        """
    def __init__ (self, snowfall_data):
        """
        snowfall_data (dict): Nested dict of snowfall stats per location and day.
        """
        self.snowfall_data = snowfall_data

    def generate_daily_snowfall(self, location, day, offset=0.0):
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        offset (float): Mean snowfall adjustment (default 0.0).

        returns:
            float: Simulated daily snowfall for the given location and day.
        """
        if location not in self.snowfall_data:
            logging.error(f"Location {location} not found in snowfall data")
            return None

        if day < 0 or day >= len(self.snowfall_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day
        snowfall_data_tuple = self.snowfall_data[location][day]

        if snowfall_data_tuple is None:
            logging.error(f"Missing snowfall data tuple (mean, var) for {location} on day {day}")
            return None
        
        # Unpack mean and variance
        mean, var = snowfall_data_tuple

        if mean is None or var is None:
            logging.error(f"Missing snowfall data mean: {mean} or var: {var} for {location} on day {day}")
            return None
            
        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        return np.random.normal(mean + offset, np.sqrt(var))