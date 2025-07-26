# Original data from CDS was of hourly surface solar radiation downward in GRIB format.
# Joules per square meter (J/m^2).
# This script processes a GRIB file to extract daily mean and variance of surface solar radiation downward
# from specified locations and saves the results to CSV files.
# Daily mean and variance used to stochastically simulate daily surface solar radiation variations
# in the mammoth repopulation simulator.

# Locations: Krasnoyarsk (south taiga), Salekhard (north taiga), 
#            Saskylakh (south tundra), and Cape Chelyuskin (north tundra).

# Locations span a gradient of the siberian biomes from taiga (warmer) to tundra (cooler). 
# This is to get a better mapping of the UV variations across siberia.

import pygrib
import pandas as pd
from collections import defaultdict

locations = {
    "krasnoyarsk": (56.0, 93.0),
    "salekhard": (66.5, 66.5),
    "saskylakh": (71.9, 114.1),
    "cape_chelyuskin": (77.7, 104.3),
}

solar_rad_data = {loc: defaultdict(list) for loc in locations}

grib_file_path = "C:/Users/aalad/Downloads/era5_SSRD_2024.grib" # file does not exist anymore due to space constraints

print("Starting GRIB file processing for surface solar radiation.")

with pygrib.open(grib_file_path) as grbs:
    for i, grb in enumerate(grbs):
        if "Surface short-wave (solar) radiation downwards" not in grb.name:
            continue

        date = grb.validDate
        data, lats, lons = grb.data()

        for loc, (target_lat, target_lon) in locations.items():
            lat_idx = (abs(lats[:, 0] - target_lat)).argmin()
            lon_idx = (abs(lons[0, :] - target_lon)).argmin()
            solar_rad = data[lat_idx, lon_idx]
            solar_rad_data[loc][date.date()].append(solar_rad)

        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1} messages...")

print("Computing daily mean and variance for surface solar radiation now.")

for loc, day_map in solar_rad_data.items():
    rows = []
    for day, solar_vals in sorted(day_map.items()):
        mean = sum(solar_vals) / len(solar_vals)
        var = sum((val - mean) ** 2 for val in solar_vals) / len(solar_vals)
        rows.append((day, mean, var))
        print(f"{loc}: {day} → Mean = {mean:.4f} J/m^2, Variance = {var:.4f}")

    df = pd.DataFrame(rows, columns=["Date", "Mean_Surface_Solar_Radiation_Jm2", "Variance_Surface_Solar_Radiation_Jm2"])
    df.to_csv(f"{loc}_daily_surface_solar_rad_stats.csv", index=False)

print("\nFinished.")
