import pandas as pd
import numpy as np

class TemperatureLoader:
    """
    ClimateLoader is responsible for loading and organizing temperature data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of temperature
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        temp_data (dict): A nested dictionary for a location from load_temp_data
    """
    def __init__(self, filepath: str, location: str):
        """
        filepath (str): Path to the CSV file containing temperature data.
        location (str): The label identifying the geographic location.
        """
        self.location = location
        self.temp_data = self.load_temp_data(filepath)

    def load_temp_data(self, filepath):
        """
        helper function for constructor that loads temperature data from a CSV file.

        returns:
            dict: A nested dictionary mapping location to a dict
            of day numbers to a tuple of (mean_temp, temp_var).
        """
        df = pd.read_csv(filepath, parse_dates=["date"])
        df["day_number"] = df["date"].dt.dayofyear - 1

        return {
            self.location: {
                row["day_number"]: (row["mean_temp"], row["temp_var"])
                for _, row in df.iterrows()
            }
        }
    
    def get_temp_data(self):
        return self.temp_data
