import pandas as pd
import logging

class SoilTemp4Loader:
    """
    SoilTemp4Loader is responsible for loading and organizing level 4 soil temperature data from a CSV file
    for a specific geographic location. It extracts the daily mean and variance of soil temperature
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        soil_temp4_data (dict): A nested dictionary for a location from soil_temp4_data
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.soil_temp4_data = self.load_soil_temp4_data(filepath)

    def load_soil_temp4_data(self, filepath: str) -> dict:
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_soil_temp, soil_temp_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["Date"])
        except Exception as e:
            logging.error(f"SoilTemp4Loader Failed to read soil temperature CSV: {e}")
            return {self.location: {}}

        if "Date" not in df.columns or "Mean_Temp_C" not in df.columns or "Variance_Temp_C" not in df.columns:
            logging.error("SoilTemp4Loader Required columns ('Date', 'Mean_Temp_C', 'Variance_Temp_C') missing.")
            return {self.location: {}}

        df["day_number"] = df["Date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["Mean_Temp_C"]
            var = row["Variance_Temp_C"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"SoilTemp4Loader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"SoilTemp4Loader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_soil_temp4_data(self) -> dict:
        return self.soil_temp4_data