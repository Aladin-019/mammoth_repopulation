import numpy as np

class TemperatureDriver:
    """
        Simulates daily temperatures using mean and variance data for each location and day.
    
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
        mean, var = self.temp_data[location][day]
        return np.random.normal(mean + biome_offset, var)