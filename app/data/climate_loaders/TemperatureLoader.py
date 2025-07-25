import pandas as pd
import numpy as np
import logging

class TemperatureLoader:
    """
    TemperatureLoader is responsible for loading and organizing temperature data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of temperature
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        temp_data (dict): A nested dictionary for a location from load_temp_data
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.temp_data = self.load_temp_data(filepath)

    def load_temp_data(self, filepath):
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_temp, temp_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["date"])
        except Exception as e:
            logging.error(f"TemperatureLoader Failed to read temperature CSV: {e}")
            return {self.location: {}}

        if "date" not in df.columns or "mean_temp" not in df.columns or "temp_var" not in df.columns:
            logging.error("TemperatureLoader Required columns ('date', 'mean_temp', 'temp_var') missing.")
            return {self.location: {}}

        df["day_number"] = df["date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["mean_temp"]
            var = row["temp_var"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"TemperatureLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"TemperatureLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_temp_data(self):
        return self.temp_data