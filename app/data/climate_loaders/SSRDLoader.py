import pandas as pd
import logging

class SSRDLoader:
    """
    SSRDLoader is responsible for loading and organizing surface solar radiation downwards (SSRD) data 
    from a CSV file for a specific geographic location. It extracts the daily mean and variance of SSRD
    and stores them in a structured dictionary format that is optimized for lookup by day of year.

    Attributes:
        location (str): The label identifying the geographic location.
        srd_data (dict): A nested dictionary for a location from load_srd_data
    """

    def __init__(self, filepath: str, location: str):
        self.location = location
        self.srd_data = self.load_srd_data(filepath)

    def load_srd_data(self, filepath):
        """
        Reads a CSV file and loads a mapping of {day_number: (mean_srd, srd_var)}.

        Returns:
            dict: { location: { day_number: (mean, var) } }
        """
        try:
            df = pd.read_csv(filepath, parse_dates=["date"])
        except Exception as e:
            logging.error(f"SRDLoader Failed to read SSRD CSV: {e}")
            return {self.location: {}}

        if "date" not in df.columns or "mean_srd" not in df.columns or "srd_var" not in df.columns:
            logging.error("SRDLoader Required columns ('date', 'mean_srd', 'srd_var') missing.")
            return {self.location: {}}

        df["day_number"] = df["date"].dt.dayofyear - 1

        days_map = {}
        for _, row in df.iterrows():
            day = row["day_number"]
            mean = row["mean_srd"]
            var = row["srd_var"]

            if pd.isna(mean) or pd.isna(var):
                logging.warning(f"SRDLoader Skipping day {day}: missing mean: {mean} or variance: {var}")
                continue

            if var < 0:
                logging.warning(f"SRDLoader Skipping day {day}: negative variance ({var})")
                continue

            days_map[day] = (mean, var)

        return {self.location: days_map}

    def get_srd_data(self):
        return self.srd_data