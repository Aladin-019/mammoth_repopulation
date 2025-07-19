# Original data from CDS was of hourly snowfall rate in GRIB format.
# Millimeters (mm).
# This script processes a GRIB file to extract daily mean and variance of snowfall
# from specified locations and saves the results to CSV files.
# Daily mean and variance used to stochastically simulate daily large scale snowfall variations
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

snow_data = {loc: defaultdict(list) for loc in locations}

grib_file_path = "C:/Users/aalad/Downloads/era5_snowfall_2024.grib" # file does not exist anymore due to space constraints

print("Starting GRIB file processing for snowfall.")

with pygrib.open(grib_file_path) as grbs:
    for i, grb in enumerate(grbs):
        if grb.name.lower() != "snowfall":
            continue

        date = grb.validDate
        data, lats, lons = grb.data()

        for loc, (target_lat, target_lon) in locations.items():
            try:
                lat_idx = (abs(lats[:, 0] - target_lat)).argmin()
                lon_idx = (abs(lons[0, :] - target_lon)).argmin()
                snowfall_mm = data[lat_idx, lon_idx]
                snow_data[loc][date.date()].append(snowfall_mm)
            except Exception as e:
                print(f"{loc} @ {date}: {e}")

        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1} messages...")

print("Computing daily mean and variance for snowfall now.")

for loc, day_map in snow_data.items():
    rows = []
    for day, snow_vals in sorted(day_map.items()):
        mean = sum(snow_vals) / len(snow_vals)
        var = sum((val - mean) ** 2 for val in snow_vals) / len(snow_vals)
        rows.append((day, mean, var))
        print(f"{loc}: {day} → Mean = {mean:.2f} mm, Variance = {var:.2f}")

    df = pd.DataFrame(rows, columns=["Date", "Mean_Snowfall_mm", "Variance_Snowfall_mm"])
    df.to_csv(f"{loc}_daily_snowfall_stats.csv", index=False)

print("\nFinished processing snowfall.")
