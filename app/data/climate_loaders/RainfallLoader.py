import pandas as pd
import logging

class RainfallLoader:
    """
    RainfallLoader is responsible for loading and organizing rainfall data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of rainfall
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        rainfall_data (dict): A nested dictionary for a location from load_rainfall_data
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.rainfall_data = self.load_rainfall_data(filepath)

    def load_rainfall_data(self, filepath):
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_rainfall, rain_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["date"])
        except Exception as e:
            logging.error(f"RainfallLoader Failed to read rainfall CSV: {e}")
            return {self.location: {}}

        if "date" not in df.columns or "mean_rainfall" not in df.columns or "rain_var" not in df.columns:
            logging.error("RainfallLoader Required columns ('date', 'mean_rainfall', 'rain_var') missing.")
            return {self.location: {}}

        df["day_number"] = df["date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["mean_rainfall"]
            var = row["rain_var"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"RainfallLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"RainfallLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_rainfall_data(self):
        return self.rainfall_data