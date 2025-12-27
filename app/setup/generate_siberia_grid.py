import geopandas as gp
from shapely.ops import unary_union
from shapely.geometry import Point
from shapely.geometry import box
import matplotlib.pyplot as plt
import numpy as np
import os


def generate_siberia_grid():
    """
    Generate Siberia grid using actual Russian border data from GeoJSON.
    """
    # Get the path to the GeoJSON file relative to the project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    geo_json_path = os.path.join(project_root, "app", "data", "geographical_data", "russia_borders_data", "custom.geo.json")
    
    # Load Europe (including asian russia) GeoJSON  
    gdf = gp.read_file(geo_json_path)

    # Filter Russia
    russia = gdf[gdf["name"].str.contains("Russia", case=False)]

    minx, miny, maxx, maxy = russia.total_bounds
    # Define a bounding box for Eastern Russia (Siberia) longitude (keep only East of ~60E).
    # Make polygon of approximate Siberia
    clip_box = box(60.0, miny, maxx, maxy)
    siberia_polyg = russia.geometry.iloc[0].intersection(clip_box)

    # Siberia 8000km across east-west.
    # At average latitude (45+80)/2 = 62.5 degrees, the longitude per degree distance is about 60km per degree.

    # 180 - 60 = 120 degrees of longitude
    # Siberia is 8000km across so we need 8000 lines
    # 8000 lines = 120 degrees * 1/X resolution
    # So X = 120/8000 = 0.015 degrees per line
    # 0.015*5 = 0.074 = grid is 5km^2

    # Reduced resolution from 1.0 to 0.25 degrees for more realistic plot sizes
    # This creates smaller plots (more total plots) but makes trampling effects visible
    # Resolution change: 1.0 -> 0.25 degrees = ~16x more plots for better simulation detail
    latitudes = np.arange(45.0, 80.1, 0.25)
    longitudes = np.arange(60.0, 180.1, 0.25)
    grid_cells = []
    for lat in latitudes:
        for lon in longitudes:  # 60E to 180E = Siberia
            pt = Point(lon, lat)
            if siberia_polyg.contains(pt):
                grid_cells.append((lon, lat))
    
    return grid_cells


if __name__ == "__main__":
    # Test the grid generation
    grid_cells = generate_siberia_grid()
    print(f"Generated {len(grid_cells)} grid cells")
    
    # Show some sample coordinates
    print("Sample coordinates:")
    for i, (lon, lat) in enumerate(grid_cells[:10]):
        print(f"  {i+1}: ({lon:.2f}, {lat:.2f})")
    
    # Visualize plot
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf = gp.read_file(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "data", "geographical_data", "russia_borders_data", "custom.geo.json"))
    russia = gdf[gdf["name"].str.contains("Russia", case=False)]
    russia.plot(ax=ax, color="lightgray", edgecolor="black")
    xs, ys = zip(*grid_cells)
    ax.scatter(xs, ys, s=0.8, color="green")
    ax.set_xlim(60, 180)
    ax.set_ylim(45, 80)
    plt.title("Siberia Simulation Grid")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.show()
