import pandas as pd
import numpy as np

class UVLoader:
    """
    UVLoader is responsible for loading and organizing UV data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of UV
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        uv_data (dict): A nested dictionary for a location from load_uv_data
    """
    def __init__(self, filepath: str, location: str):
        """
        filepath (str): Path to the CSV file containing UV data.
        location (str): The label identifying the geographic location.
        """
        self.location = location
        self.uv_data = self.load_uv_data(filepath)

    def load_uv_data(self, filepath):
        """
        helper function for constructor that loads UV data from a CSV file.

        returns:
            dict: A nested dictionary mapping location to a dict
            of day numbers to a tuple of (mean_uv, uv_var).
        """
        df = pd.read_csv(filepath, parse_dates=["date"])
        df["day_number"] = df["date"].dt.dayofyear - 1

        return {
            self.location: {
                row["day_number"]: (row["mean_uv"], row["uv_var"])
                for _, row in df.iterrows()
            }
        }
    
    def get_uv_data(self):
        """
        Returns the UV data for the specified location.

        returns:
            dict: A nested dictionary mapping location to a dict
            of day numbers to a tuple of (mean_uv, uv_var).
        """
        return self.uv_data
