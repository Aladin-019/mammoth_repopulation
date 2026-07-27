"""
Grid construction helpers for the mammoth repopulation simulation.
Builds a realistic Siberia grid from real geographic data.
"""

from typing import Tuple, List
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
import numpy as np


def latitude_to_biome(latitude: float) -> str:
    """
    Convert latitude to biome type based on Siberia's biome distribution.

    Based on climate data locations:
    - Krasnoyarsk (56.0°N) - southern taiga
    - Salekhard (66.5°N) - northern taiga
    - Saskylakh (71.9°N) - southern tundra
    - Cape Chelyuskin (77.7°N) - northern tundra

    Args:
        latitude: Latitude in degrees
    Returns:
        Biome name string
    """
    if latitude < 60.0:
        return 'southern taiga'
    elif latitude < 70.0:
        return 'northern taiga'
    elif latitude < 75.0:
        return 'southern tundra'
    else:
        return 'northern tundra'


def create_siberia_grid(resolution: float = 0.75, lon_min: float = 120.0, lon_max: float = 180.0) -> Tuple[PlotGrid, List[Tuple[float, float]], GridInitializer]:
    """
    Create a realistic Siberia grid using actual geography.
    Only creates plots for land cells (within Siberia polygon), not water.

    Args:
        resolution: Grid resolution in degrees (default: 0.75 for better detail)
        lon_min: Minimum longitude (default: 120.0 for eastern/right third)
        lon_max: Maximum longitude (default: 180.0 for eastern edge)

    Returns:
        Tuple of (PlotGrid, list of (lon, lat) coordinates, GridInitializer)
    """
    import geopandas as gp
    from shapely.geometry import Point, box
    import os

    # Generate grid with specified resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    geo_json_path = os.path.join(project_root, "app", "data", "geographical_data", "russia_borders_data", "custom.geo.json")

    # Load Russia GeoJSON
    gdf = gp.read_file(geo_json_path)
    russia = gdf[gdf["name"].str.contains("Russia", case=False)]
    minx, miny, maxx, maxy = russia.total_bounds
    # Use custom longitude range for eastern/right third
    clip_box = box(lon_min, miny, maxx, maxy)
    siberia_polyg = russia.geometry.iloc[0].intersection(clip_box)

    # Generate grid cells with specified resolution - ONLY for land (within polygon)
    # Focusing on eastern/right third of Siberia
    latitudes = np.arange(45.0, 80.1, resolution)
    longitudes = np.arange(lon_min, lon_max + resolution, resolution)
    grid_cells = []
    for lat in latitudes:
        for lon in longitudes:
            pt = Point(lon, lat)
            # Only include points that are within the Siberia polygon (land, not water)
            if siberia_polyg.contains(pt):
                grid_cells.append((lon, lat))

    print(f"Generated {len(grid_cells)} grid cells from eastern Siberia ({resolution}° resolution, {lon_min}°-{lon_max}°E)")

    # Initialize grid with matching resolution
    initializer = GridInitializer(lat_step=resolution, lon_step=resolution)
    plot_grid = initializer.get_plot_grid()

    # Convert lat/lon to row/col indices for the grid
    # Use the actual grid cell coordinates to maintain spatial relationships
    unique_lats = sorted(set(lat for lon, lat in grid_cells))
    unique_lons = sorted(set(lon for lon, lat in grid_cells))

    lat_to_row = {lat: row for row, lat in enumerate(unique_lats)}
    lon_to_col = {lon: col for col, lon in enumerate(unique_lons)}

    print("Creating plots from grid cells...")
    for lon, lat in grid_cells:
        row = lat_to_row[lat]
        col = lon_to_col[lon]
        biome = latitude_to_biome(lat)

        plot = initializer.create_plot_from_biome(biome)
        plot_grid.add_plot(row, col, plot)

    print(f"Created grid with {len(plot_grid.plots)} plots (land only)")
    return plot_grid, grid_cells, initializer