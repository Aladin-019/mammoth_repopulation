#!/usr/bin/env python3
"""
Main simulation runner for the Mammoth Repopulation Simulator.
This script initializes the simulation grid and runs the main simulation loop.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from app.setup.grid_initializer import GridInitializer
from app.setup.generate_siberia_grid import generate_siberia_grid

class SimulationVisualizer:
    """Handles the visual display of the simulation."""
    
    def __init__(self, plot_grid, mammoth_plot_id):
        self.plot_grid = plot_grid
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.day = 0
        self.debugged_biomes = set()  # Track which biomes we've debugged each day
        self.mammoth_plot_id = mammoth_plot_id # Store mammoth plot ID
        
        # Define colors for different biomes
        self.biome_colors = {
            'unknown': '#000000',
            'northern tundra': '#E6F3FF',      # Light blue
            'southern tundra': '#87CEEB',      # Sky blue
            'northern taiga': '#228B22',       # Forest green
            'southern taiga': '#32CD32',       # Lime green
        }
        
        # Color for steppe conditions (when met)
        self.steppe_color = '#FFD700'  # Gold
        
        # Create colormap
        self.cmap = ListedColormap(list(self.biome_colors.values()))
        
    def setup_display(self):
        """Set up the initial display."""
        self.ax.set_title(f'Day {self.day}: Mammoth Repopulation Simulation')
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        
    def update_display(self, climate_day=None):
        """Update the display for the current day."""
        # Use climate_day if provided, otherwise fall back to self.day
        if climate_day is None:
            climate_day = self.day
        self.ax.clear()
        self.setup_display()
        
        # Reset debug tracking for new day
        self.debugged_biomes.clear()
        
        # Get the grid dimensions (min_row, max_row, min_col, max_col)
        min_row, max_row, min_col, max_col = self.plot_grid.get_grid_dimensions()
        
        # Calculate actual grid size
        rows = max_row - min_row + 1
        cols = max_col - min_col + 1
        
        # Create biome display grid
        biome_grid = np.zeros((rows, cols), dtype=object)
        steppe_conditions = np.zeros((rows, cols), dtype=bool)
        
        # Fill the grids
        for row in range(rows):
            for col in range(cols):
                # Convert display grid coordinates to actual plot coordinates
                actual_row = min_row + row
                actual_col = min_col + col
                plot = self.plot_grid.get_plot(actual_row, actual_col)
                if plot:
                    biome = plot.get_climate().get_biome()
                    biome_grid[row, col] = biome
                    
                    # Check if steppe conditions are met
                    if self._check_steppe_conditions(plot):
                        steppe_conditions[row, col] = True
                        # No more debug prints from visualizer
                     
                     # Note: Mammoth plot debug prints are now handled in the main simulation loop for days 1-5 only
        
        # Display biomes
        self._display_biomes(biome_grid)
        
        # Overlay steppe conditions
        self._overlay_steppe_conditions(steppe_conditions)
        
        # No more debug prints from visualizer
        
        # Add legend
        self._add_legend()
        
        plt.tight_layout()
        
    def _check_steppe_conditions(self, plot):
        """Check if a plot meets steppe conditions using Climate's is_steppe method."""
        is_steppe = plot.get_climate().is_steppe()
        # No more debug prints from visualizer
        return is_steppe
    
    def _display_biomes(self, biome_grid):
        """Display the biome grid."""
        rows, cols = biome_grid.shape
        
        # Convert biome names to color indices
        biome_to_index = {biome: idx for idx, biome in enumerate(self.biome_colors.keys())}
        color_grid = np.zeros((rows, cols))
        
        for row in range(rows):
            for col in range(cols):
                biome = biome_grid[row, col]
                if biome in biome_to_index:
                    color_grid[row, col] = biome_to_index[biome]
                else:
                    color_grid[row, col] = 0
        
        # Display with custom colormap
        # Flip the grid vertically so that northern latitudes (tundra) appear at the top
        # and southern latitudes (taiga) appear at the bottom
        flipped_color_grid = np.flipud(color_grid)
        im = self.ax.imshow(flipped_color_grid, cmap=self.cmap, aspect='auto', 
                           extent=[60, 180, 45, 80])  # Siberia coordinates (normal order)
        
        # Add grid lines
        self.ax.grid(True, alpha=0.3)
        
    def _overlay_steppe_conditions(self, steppe_conditions):
        """Overlay steppe conditions on the display."""
        rows, cols = steppe_conditions.shape
        
        # Find where steppe conditions are met
        steppe_rows, steppe_cols = np.where(steppe_conditions)
        
        # Convert to longitude/latitude coordinates
        # Note: biome_grid is created with lat_range from south to north (increasing)
        # So Row 0 = lowest latitude (south), Row N = highest latitude (north)
        lons = np.linspace(60, 180, cols)
        lats = np.linspace(45, 80, rows)  # Fixed: match biome grid creation order
        
        # Plot steppe areas
        for row, col in zip(steppe_rows, steppe_cols):
            lon = lons[col]
            lat = lats[row]
            self.ax.scatter(lon, lat, c=self.steppe_color, s=50, 
                           marker='s', alpha=0.7, edgecolors='black', linewidth=0.5)
    
    def _add_legend(self):
        """Add a legend to the plot."""
        legend_elements = []
        
        # Biome legend
        for biome, color in self.biome_colors.items():
            legend_elements.append(plt.Rectangle((0, 0), 1, 1, facecolor=color, 
                                              label=biome.replace('_', ' ').title()))
        
        # Steppe conditions legend
        legend_elements.append(plt.Line2D([0], [0], marker='s', color='w', 
                                        markerfacecolor=self.steppe_color, 
                                        markersize=10, label='Steppe Conditions Met'))
        
        self.ax.legend(handles=legend_elements, loc='upper right', 
                      title='Biomes & Conditions')

def run_simulation(days=30):
    """Run the main simulation."""
    print("Initializing simulation...")
    
    # Generate real Siberia grid using actual Russian border data
    print("Generating Siberia grid from real geographical data...")
    grid_cells = generate_siberia_grid()
    
    # Convert grid cells to biome grid format
    # Extract unique coordinates and create a proper grid
    lats = [cell[1] for cell in grid_cells]
    lons = [cell[0] for cell in grid_cells]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Create a grid that covers the actual Siberia area
    # Initialize grid with reduced resolution for better performance
    lat_step = 0.75  # Reduced from 0.75° for even better performance
    lon_step = 0.75  # Reduced from 0.75° for even better performance
    
    lat_range = np.arange(min_lat, max_lat + lat_step, lat_step)
    lon_range = np.arange(min_lon, max_lon + lon_step, lon_step)
    
    rows, cols = len(lat_range), len(lon_range)
    print(f"Grid dimensions: {rows} rows × {cols} columns")
    print(f"Latitude range: {min_lat:.2f}° to {max_lat:.2f}° (step: {lat_step}°)")
    print(f"Longitude range: {min_lon:.2f}° to {max_lon:.2f}° (step: {lon_step}°)")
    
    biome_grid = np.full((rows, cols), 'unknown', dtype=object)
    
    # Create a set of valid grid cells for fast lookup
    valid_cells = set(grid_cells)
    print(f"Total valid grid cells: {len(valid_cells)}")
    
    # Fill the biome grid based on real geography
    valid_plots_created = 0
    for row, lat in enumerate(lat_range):
        for col, lon in enumerate(lon_range):
            if (lon, lat) in valid_cells:
                valid_plots_created += 1
                # Assign biomes based on real latitude/longitude
                # Since imshow displays from top to bottom, we need to flip the latitude logic
                # Order: northern tundra (highest latitude) -> southern tundra -> northern taiga -> southern taiga (lowest latitude)
                # New distribution: ~10% northern tundra, ~15% southern tundra, ~75% taiga (northern + southern)
                # Adjusted boundaries to give taiga regions much more vertical space
                if lat > 72:  # Arctic regions (highest latitude) - very small area
                    biome_grid[row, col] = 'northern tundra'
                elif lat > 68:  # High latitude regions - small area
                    biome_grid[row, col] = 'southern tundra'
                elif lat > 58:  # Mid latitude regions - large area
                    biome_grid[row, col] = 'northern taiga'
                elif lat > 45:  # Southern regions (lowest latitude) - large area
                    biome_grid[row, col] = 'southern taiga'
                else:
                    biome_grid[row, col] = 'unknown'
            else:
                biome_grid[row, col] = 'unknown'
    
    print(f"Valid plots found in biome grid: {valid_plots_created}")
    
    # Initialize the plot grid
    initializer = GridInitializer(lat_step=lat_step, lon_step=lon_step)
    plot_grid = initializer.initialize_from_biome_grid(biome_grid)
    
    # Add mammoths to the central northern taiga plot after all plots are created
    mammoth_plot_id = initializer.add_mammoths_to_central_plot()
    
    print(f"Created {len(plot_grid.get_all_plots())} plots")
    if mammoth_plot_id is not None:
        print(f"Mammoths will start on plot ID: {mammoth_plot_id}")
    else:
        print("No northern taiga plot found for mammoths!")
    
    # Create visualizer
    visualizer = SimulationVisualizer(plot_grid, mammoth_plot_id)
    
    # Simulation loop
    for day in range(1, days + 1):
        # Cycle through days 1-365 for longer simulations
        climate_day = ((day - 1) % 365) + 1
        
        # Update all plots with the cycled climate day
        plot_grid.update_all_plots(climate_day)
        
        # Update display
        visualizer.day = day
        visualizer.update_display(climate_day)
        
        # Pause to show the update
        plt.pause(0.1)  # Reduced for faster simulation
    
    print("Simulation complete!")
    plt.show()

def main():
    """Main entry point."""
    print("Mammoth Repopulation Simulator")
    print("=" * 40)
    
    # Run simulation with real Russian border data
    run_simulation(days=28)

if __name__ == "__main__":
    main()