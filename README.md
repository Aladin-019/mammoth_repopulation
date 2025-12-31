# Mammoth Repopulation Simulator
With the advent of genetic cloning, mammoth repopulation of Siberia has been a new hot topic, not only for the novelty of it but also for its environmental benefits. This project aims at simulating how reintroducing mammoths into present day sibera would actually pan out. It also gives the user freedom to play around the different variables and initial conditions. Though this project is based on actual recorded Siberian data from the CDS, I am far from the cutting edge of research and experimentation on this subject. Nonetheless, it opens a doorway to this world in a fun and engaging way.

## Locations Covered for Climate Data
- Krasnoyarsk (southern taiga)
- Salekhard (northern taiga)
- Saskylakh (southern tundra)
- Cape Chelyuskin (northern tundra)

## Climate Data Attribution
This project uses data from the **Copernicus Climate Data Store (CDS)**:
- Product: ERA5 hourly data on single levels
- Variable: 2 metre temperature (short name `2t`)
- License: [Copernicus Licence](https://cds.climate.copernicus.eu/disclaimer/licence)
- Data provider: European Centre for Medium-Range Weather Forecasts (ECMWF)

Derived temperature statistics (not raw data) are shared in this repository.

### Map Data Attribution
The file `custom.geo.json` was generated from [https://geojson-maps.kyd.au](https://geojson-maps.kyd.au),
a public tool for generating simplified GeoJSON maps.

Underlying data is likely derived from either:
- [Natural Earth](https://www.naturalearthdata.com/) — public domain, or
- [OpenStreetMap](https://www.openstreetmap.org/) — Open Database License (ODbL)

If the source is OpenStreetMap, the following attribution applies:
OpenStreetMap contributors | www.openstreetmap.org | ODbL 1.0

## Testing

This project includes comprehensive test coverage with unit and integration tests. All tests include automatic coverage reporting.

- **Test Suite**: Unit tests for individual components and integration tests for end-to-end functionality
- **Coverage Reporting**: Automatic code coverage tracking (see `TESTING.md` for details)
- **Test Runner**: Run tests with `python run_tests.py`

For detailed testing information, see [TESTING.md](TESTING.md).

## Requirements
- Python 3.8+
- `pygrib` (for GRIB file parsing)
- `pandas`
- `numpy`
