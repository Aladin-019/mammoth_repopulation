# Original data from CDS was of hourly soil temp level 4 depth in GRIB format.
# This script processes a GRIB file to extract daily mean and variance of soil temperature
# from specified locations and saves the results to CSV files.
# Daily mean and variance used to stochastically simulate daily soil temperature variations
# in the mammoth repopulation simulator.

# Locations: Krasnoyarsk (south taiga), Salekhard (north taiga), 
#            Saskylakh (south tundra), and Cape Chelyuskin (north tundra).

# Locations span a gradient of the siberian biomes from taiga (warmer) to tundra (cooler). 
# This is to get a better mapping of the temperature variations across siberia.

import pygrib
import pandas as pd
from collections import defaultdict
import os

# Define coordinates for the locations
locations = {
    "krasnoyarsk": (56.0, 93.0),
    "salekhard": (66.5, 66.5),
    "saskylakh": (71.9, 114.1),
    "cape_chelyuskin": (77.7, 104.3),
}

# Data container
temperature_data = {loc: defaultdict(list) for loc in locations}

grib_file_path = "C:/Users/aalad/Downloads/era5_soil_temp4_2024.grib"  # file no longer exists due to lack of storage

with pygrib.open(grib_file_path) as grbs:
    for i, grb in enumerate(grbs):
        if grb.name.lower() != "soil temperature level 4":
            continue

        date = grb.validDate
        data, lats, lons = grb.data()

        for loc, (target_lat, target_lon) in locations.items():
            try:
                lat_idx = (abs(lats[:, 0] - target_lat)).argmin()
                lon_idx = (abs(lons[0, :] - target_lon)).argmin()
                temp_c = data[lat_idx, lon_idx] - 273.15
                temperature_data[loc][date.date()].append(temp_c)
            except Exception as e:
                print(f"{loc} @ {date}: {e}")

        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1} messages...")

print("Computing daily mean and variance now.")
for loc, day_map in temperature_data.items():
    rows = []
    for day, temps in sorted(day_map.items()):
        mean = sum(temps) / len(temps)
        var = sum((t - mean) ** 2 for t in temps) / len(temps)
        rows.append((day, mean, var))
        print(f"{loc}: {day} → Mean = {mean:.2f}°C, Variance = {var:.2f}")

    df = pd.DataFrame(rows, columns=["Date", "Mean_Temp_C", "Variance_Temp_C"])
    df.to_csv(f"{loc}_daily_temperature_stats.csv", index=False)

print("\nFinished")
