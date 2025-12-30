"""
Main script to run the mammoth repopulation simulation.
This script initializes a grid based on real Siberia geography, runs the simulation, and visualizes the results.
"""

from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
import matplotlib.pyplot as plt


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


def create_siberia_grid(resolution=0.75, lon_min=120.0, lon_max=180.0):
    """
    Create a realistic Siberia grid using actual geography.
    Only creates plots for land cells (within Siberia polygon), not water.
    
    Args:
        resolution: Grid resolution in degrees (default: 0.75 for better detail)
        lon_min: Minimum longitude (default: 120.0 for eastern/right third)
        lon_max: Maximum longitude (default: 180.0 for eastern edge)
    
    Returns:
        Tuple of (PlotGrid, list of (lon, lat) coordinates)
    """
    # Use the original generate_siberia_grid function but with custom resolution and region
    import numpy as np
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
    
    # Create plots ONLY for valid land cells (already filtered by polygon check above)
    print("Creating plots from grid cells...")
    for lon, lat in grid_cells:
        row = lat_to_row[lat]
        col = lon_to_col[lon]
        biome = latitude_to_biome(lat)
        
        plot = initializer.create_plot_from_biome(biome)
        plot_grid.add_plot(row, col, plot)
    
    print(f"Created grid with {len(plot_grid.plots)} plots (land only)")
    return plot_grid, grid_cells


def run_simulation(plot_grid: PlotGrid, num_days: int = 10, visualize: bool = True):
    """
    Run the simulation for a specified number of days, with optional real-time visualization.
    
    Args:
        plot_grid: The PlotGrid to simulate
        num_days: Number of days to simulate (default: 10)
        visualize: Whether to visualize each day in real time (default: True)
    """
    print(f"\nRunning simulation for {num_days} days...")
    
    # Define biome colors for visualization
    biome_colors = {
        'southern taiga': '#228B22',      # Forest green
        'northern taiga': '#32CD32',      # Lime green
        'southern tundra': '#D3D3D3',     # Light gray
        'northern tundra': '#FFFFFF'      # White
    }
    
    # Setup visualization if requested
    ax = None
    if visualize:
        import matplotlib.pyplot as plt
        plt.ion()  # Turn on interactive mode
        # Show initial state (day 0)
        ax = plot_grid.visualize_biomes(biome_colors, figsize=(14, 10), save_path=None, ax=None, day=0)
        plt.pause(0.1)
    
    for day in range(1, num_days + 1):
        print(f"  Day {day}/{num_days}...", end=' ', flush=True)
        plot_grid.update_all_plots(day)
        print("✓")
        
        # Update visualization each day
        if visualize:
            plot_grid.visualize_biomes(biome_colors, figsize=(14, 10), save_path=None, ax=ax, day=day)
            plt.pause(0.5)  # Brief pause to see the update
    
    if visualize:
        print("\nSimulation complete! Close the plot window when done viewing.")
        import matplotlib.pyplot as plt
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Keep window open
    else:
        print("Simulation complete!")


def visualize_biomes_interactive(plot_grid: PlotGrid):
    """
    Visualize the biomes with interactive zoom capability.
    
    Args:
        plot_grid: The PlotGrid to visualize
    """
    # Define biome colors
    biome_colors = {
        'southern taiga': '#228B22',      # Forest green
        'northern taiga': '#32CD32',      # Lime green
        'southern tundra': '#D3D3D3',     # Light gray
        'northern tundra': '#FFFFFF'      # White
    }
    
    plot_grid.visualize_biomes(biome_colors, figsize=(14, 10))


def add_mammoths_to_location(plot_grid, initializer, row: int, col: int, population_per_km2: float = 0.01):
    """
    Add mammoths to a specific plot location.
    
    Args:
        plot_grid: The PlotGrid to add mammoths to
        initializer: The GridInitializer instance (needed for helper methods)
        row: Row coordinate of the plot
        col: Column coordinate of the plot
        population_per_km2: Population density in mammoths per km^2 (default: 0.01)
    
    Returns:
        The mammoth Prey object if successful, None otherwise
    """
    plot = plot_grid.get_plot(row, col)
    if plot is None:
        print(f"Warning: No plot found at row={row}, col={col}")
        return None
    
    mammoth = initializer.add_mammoth_to_plot(plot, population_per_km2=population_per_km2)
    if mammoth:
        print(f"Added mammoths to plot at row={row}, col={col} with population density {population_per_km2} per km^2")
        print(f"  Actual population: {mammoth.population} mammoths")
    return mammoth


def main():
    """Main function to run the simulation."""
    print("=" * 50)
    print("Mammoth Repopulation Simulator")
    print("=" * 50)
    
    # Create Siberia grid focused on eastern third with higher resolution
    plot_grid, grid_cells = create_siberia_grid(resolution=0.55, lon_min=130.0, lon_max=180.0)
    
    # Create initializer to use for adding mammoths (must match grid resolution)
    from app.setup.grid_initializer import GridInitializer
    initializer = GridInitializer(lat_step=0.55, lon_step=0.55)
    
    # Add mammoths to a specific location (use an actual plot coordinate, not the center)
    # Get all plot coordinates and pick one from the middle of the list
    plot_coords = plot_grid.get_plot_coordinates()
    if plot_coords:
        # Sort by row then col to get a consistent ordering
        plot_coords_sorted = sorted(plot_coords)
        # Pick a plot from the middle of the sorted list
        center_idx = len(plot_coords_sorted) // 2
        center_row, center_col = plot_coords_sorted[center_idx]
        
        # Add mammoths with population density of 0.01 per km^2 (adjust as needed)
        # You can change the location (row, col) and population_per_km2 as desired
        add_mammoths_to_location(plot_grid, initializer, center_row, center_col, population_per_km2=0.01)
    else:
        print("Warning: No plots found in the grid. Cannot add mammoths.")
    
    # Run simulation with real-time visualization (300 days for longer simulation)
    run_simulation(plot_grid, num_days=300, visualize=True)


if __name__ == "__main__":
    main()
