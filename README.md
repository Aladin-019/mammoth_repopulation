# Mammoth Repopulation Simulator
With the advent of genetic cloning, mammoth repopulation of Siberia has been a new hot topic, not only for the novelty of it but also for its environmental benefits. This project aims at simulating how reintroducing mammoths into present day sibera would actually pan out. It also gives the user freedom to play around the different variables and initial conditions. Though this project is based on actual recorded Siberian data from the CDS, I am far from the cutting edge of research and experimentation on this subject. Nonetheless, it opens a doorway to this world in a fun and engaging way.

## Locations Covered for Climate Data
- Krasnoyarsk (southern taiga)
- Salekhard (northern taiga)
- Saskylakh (southern tundra)
- Cape Chelyuskin (northern tundra)

## Attribution
This project uses data from the **Copernicus Climate Data Store (CDS)**:
- Product: ERA5 hourly data on single levels
- Variable: 2 metre temperature (short name `2t`)
- License: [Copernicus Licence](https://cds.climate.copernicus.eu/disclaimer/licence)
- Data provider: © European Centre for Medium-Range Weather Forecasts (ECMWF)

Derived temperature statistics (not raw data) are shared in this repository.

## Requirements
- Python 3.8+
- `pygrib` (for GRIB file parsing)
- `pandas`
- `numpy`
