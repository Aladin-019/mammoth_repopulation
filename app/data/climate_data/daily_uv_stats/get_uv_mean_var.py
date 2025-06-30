# Original data from CDS was of hourly UV radiation in GRIB format.
# This script processes a GRIB file to extract daily mean and variance of UV radiation
# from specified locations and saves the results to CSV files.
# Daily mean and variance used to stochastically simulate daily UV variations
# in the mammoth repopulation simulator.

# Locations: Krasnoyarsk (south taiga), Salekhard (north taiga), 
#            Saskylakh (south tundra), and Cape Chelyuskin (north tundra).

# Locations span a gradient of the siberian biomes from taiga (warmer) to tundra (cooler). 
# This is to get a better mapping of the UV variations across siberia.

import pygrib
import pandas as pd
from collections import defaultdict


# Define coordinates for the locations
locations = {
    "krasnoyarsk": (56.0, 93.0),
    "salekhard": (66.5, 66.5),
    "saskylakh": (71.9, 114.1),
    "cape_chelyuskin": (77.7, 104.3),
}

# Data container
uv_data = {loc: defaultdict(list) for loc in locations}

# Path to the local GRIB file
grib_file_path = "C:/Users/aalad/Downloads/era5_uv_2024.grib"  # file does not exist anymore due to no space

print("Starting GRIB file processing for UV radiation.")

with pygrib.open(grib_file_path) as grbs:
    for i, grb in enumerate(grbs):
        if grb.name != "Surface downward UV radiation":
            continue

        date = grb.validDate
        data, lats, lons = grb.data()

        for loc, (target_lat, target_lon) in locations.items():
            try:
                lat_idx = (abs(lats[:, 0] - target_lat)).argmin()
                lon_idx = (abs(lons[0, :] - target_lon)).argmin()
                uv_value = data[lat_idx, lon_idx]
                uv_data[loc][date.date()].append(uv_value)
            except Exception as e:
                print(f"{loc} @ {date}: {e}")

        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1} messages...")

print("Computing daily mean and variance for UV radiation now.")

for loc, day_map in uv_data.items():
    rows = []
    for day, uv_values in sorted(day_map.items()):
        mean = sum(uv_values) / len(uv_values)
        var = sum((u - mean) ** 2 for u in uv_values) / len(uv_values)
        rows.append((day, mean, var))
        print(f"{loc}: {day} → Mean UV = {mean:.2f}, Variance = {var:.2f}")

    df = pd.DataFrame(rows, columns=["Date", "Mean_UV", "Variance_UV"])
    df.to_csv(f"{loc}_daily_uv_stats.csv", index=False)

print("\nFinished UV radiation processing.")
