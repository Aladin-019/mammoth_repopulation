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

    def load_rainfall_data(self, filepath: str) -> dict:
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_rainfall, rain_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["Date"])
        except Exception as e:
            logging.error(f"RainfallLoader Failed to read rainfall CSV: {e}")
            return {self.location: {}}

        if "Date" not in df.columns or "Mean_Large_Scale_Rain_mmhr" not in df.columns or "Variance_Large_Scale_Rain_mmhr" not in df.columns:
            logging.error("RainfallLoader Required columns ('Date', 'Mean_Large_Scale_Rain_mmhr', 'Variance_Large_Scale_Rain_mmhr') missing.")
            return {self.location: {}}

        df["day_number"] = df["Date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["Mean_Large_Scale_Rain_mmhr"]
            var = row["Variance_Large_Scale_Rain_mmhr"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"RainfallLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"RainfallLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_rainfall_data(self) -> dict:
        return self.rainfall_data