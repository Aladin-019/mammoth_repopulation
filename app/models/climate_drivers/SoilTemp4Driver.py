import numpy as np
import logging

class SoilTemp4Driver:
    """
        Simulates daily level 4 depth soil temperature using mean and variance data for each location and day.

        Attributes:
        soil_temp_data (dict): { location: { day: (mean, variance) } }
    """
    def __init__ (self, soil_temp_data):
        """
        soil_temp_data (dict): Nested dict of soil temperature stats per location and day.
        """
        self.soil_temp_data = soil_temp_data

    def generate_daily_soil_temp(self, location, day, offset=0.0):
        """
        location (str): Name of the location.
        day (int): Day of year (0-365).
        offset (float): Mean soil temperature adjustment (default 0.0).

        returns:
            float: Simulated daily soil temperature for the given location and day.
        """
        if location not in self.soil_temp_data:
            logging.error(f"Location {location} not found in soil temperature data")
            return None

        if day < 0 or day >= len(self.soil_temp_data[location]):
            logging.error(f"Day {day} out of range for location {location}")
            return None

        # Get the tuple (mean, variance) for the given location and day
        soil_temp_data_tuple = self.soil_temp_data[location][day]

        if soil_temp_data_tuple is None:
            logging.error(f"Missing soil temperature data tuple (mean, var) for {location} on day {day}")
            return None

        # Unpack mean and variance
        mean, var = soil_temp_data_tuple

        if mean is None or var is None:
            logging.error(f"Missing soil temperature data mean: {mean} or var: {var} for {location} on day {day}")
            return None

        if var < 0:
            logging.error(f"Variance {var} cannot be negative. Location {location}, Day {day}")
            return None

        # Random sample from normal distribution using mean and std deviation
        return np.random.normal(mean + offset, np.sqrt(var))

   