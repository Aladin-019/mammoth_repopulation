import pandas as pd
import logging

class UVLoader:
    """
    UVLoader is responsible for loading and organizing UV data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of UV
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        uv_data (dict): A nested dictionary mapping day numbers to a tuple of (mean_uv, uv_var).
                        Example: { "location": { day_number: (mean_uv, uv_var) } }
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.uv_data = self.load_uv_data(filepath)

    def load_uv_data(self, filepath):
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_uv, uv_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["date"])
        except Exception as e:
            logging.error(f"UVLoader Failed to read UV CSV: {e}")
            return {self.location: {}}

        if "date" not in df.columns or "mean_uv" not in df.columns or "uv_var" not in df.columns:
            logging.error("UVLoader Required columns ('date', 'mean_uv', 'uv_var') missing.")
            return {self.location: {}}

        df["day_number"] = df["date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["mean_uv"]
            var = row["uv_var"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"UVLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"UVLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_uv_data(self):
        return self.uv_data
