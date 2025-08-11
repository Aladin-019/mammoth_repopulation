import pandas as pd
import logging

class SnowfallLoader:
    """
    SnowfallLoader is responsible for loading and organizing snowfall data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of snowfall
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        snowfall_data (dict): A nested dictionary for a location from load_snowfall_data
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.snowfall_data = self.load_snowfall_data(filepath)

    def load_snowfall_data(self, filepath):
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_snowfall, snow_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["Date"])
        except Exception as e:
            logging.error(f"SnowfallLoader Failed to read snowfall CSV: {e}")
            return {self.location: {}}

        if "Date" not in df.columns or "Mean_Snowfall_mm" not in df.columns or "Variance_Snowfall_mm" not in df.columns:
            logging.error("SnowfallLoader Required columns ('Date', 'Mean_Snowfall_mm', 'Variance_Snowfall_mm') missing.")
            return {self.location: {}}

        df["day_number"] = df["Date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["Mean_Snowfall_mm"]
            var = row["Variance_Snowfall_mm"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"SnowfallLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"SnowfallLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_snowfall_data(self):
        return self.snowfall_data