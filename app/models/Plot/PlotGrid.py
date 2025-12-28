from typing import Dict, Tuple, List, Optional
from .Plot import Plot
from app.interfaces.flora_plot_info import PlotInformation
import numpy as np
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    mcolors = None


# Migration probabilities
P_PREY_MIGRATION = 0.5
P_PREDATOR_MIGRATION = 0.2

# Migration mass ratios
PREY_MIGRATION_RATIO = 0.3
PREDATOR_MIGRATION_RATIO = 0.3


class PlotGrid:
    """
    A grid-based storage system for managing hundreds to thousands of plots.
    Provides fast lookup, efficient iteration, and visualization capabilities.
    
    Attributes:
        plots (Dict[Tuple[int, int], Plot]): Dictionary mapping (row, col) to Plot objects
        min_row, max_row, min_col, max_col (int): Grid boundaries
    """
    
    def __init__(self):
        self.plots: Dict[Tuple[int, int], Plot] = {}
        self.min_row = float('inf')
        self.max_row = float('-inf')
        self.min_col = float('inf')
        self.max_col = float('-inf')
        self._initial_blended_grid: Optional[np.ndarray] = None  # Store the initial blended grid
        self._initial_biomes: Dict[Tuple[int, int], str] = {}  # Store initial biome for each plot
    
    def add_plot(self, row: int, col: int, plot: Plot) -> None:
        """
        Add a plot to the grid at the specified position.
        
        Args:
            row (int): Row coordinate
            col (int): Column coordinate
            plot (Plot): The plot object to add
        """
        if not isinstance(plot, Plot):
            raise TypeError("plot must be an instance of Plot")

        self.plots[(row, col)] = plot
        
        # Update grid boundaries
        self.min_row = min(self.min_row, row)
        self.max_row = max(self.max_row, row)
        self.min_col = min(self.min_col, col)
        self.max_col = max(self.max_col, col)
    
    def get_plot(self, row: int, col: int) -> Optional[Plot]:
        """
        Get a plot at the specified position.
        
        Args:
            row (int): Row coordinate
            col (int): Column coordinate
        Returns:
            Plot or None if no plot exists at that position
        """
        return self.plots.get((row, col))

    def get_all_plots(self) -> List[Plot]:
        """
        Get all plots in the grid.
        
        Returns:
            List of all Plot objects
        """
        return list(self.plots.values())

    def get_plot_coordinates(self) -> List[Tuple[int, int]]:
        """
        Get all plot coordinates.
        
        Returns:
            List of (row, col) tuples
        """
        return list(self.plots.keys())

    def get_grid_dimensions(self) -> Tuple[int, int, int, int]:
        """
        Get the grid dimensions.
        
        Returns:
            Tuple of (min_row, max_row, min_col, max_col)
        """
        return (self.min_row, self.max_row, self.min_col, self.max_col)


    def get_neighbors(self, row: int, col: int) -> List[Plot]:
        """
        Get all neighboring plots (diagonal plots included)
        
        Args:
            row (int): Row coordinate
            col (int): Column coordinate
        Returns:
            List of neighboring Plot objects
        """
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the center plot
                neighbor = self.get_plot(row + dr, col + dc)
                if neighbor is not None:
                    neighbors.append(neighbor)
        return neighbors

    def _migrate_fauna(self, fauna, target_plot, capacity_check, migration_percent):
        """
        Helper to migrate fauna between plots.
        Args:
            fauna: The fauna instance to migrate
            target_plot: The target Plot instance
            capacity_check (str): Method name to check capacity on target plot
            migration_percent (float): Percentage of mass to migrate
        """
        # Only migrate to target plot if its not over capacity (has space)
        if not getattr(target_plot, capacity_check)():
            migration_mass = fauna.get_total_mass() * migration_percent
            if migration_mass > 0:
                target_fauna = target_plot.get_a_fauna(fauna.name)
                if target_fauna:
                    # Add migration mass to existing fauna and subtract from source
                    existing_mass = target_fauna.get_total_mass()
                    target_fauna.set_total_mass(existing_mass + migration_mass)
                    fauna.set_total_mass(fauna.get_total_mass() - migration_mass)
                else:
                    # Create a new fauna instance in the target plot
                    try:
                        new_fauna = fauna.__class__.from_existing_with_mass(fauna, migration_mass, plot=target_plot)
                        target_plot.add_fauna(new_fauna)
                        fauna.set_total_mass(fauna.get_total_mass() - migration_mass)
                    except Exception:
                        # If cannot construct, skip migration and do not subtract mass
                        pass

    # FAUNA TEMPORARILY DISABLED - migration requires fauna
    def migrate_species(self) -> None:
        """
        Simulate species migration between neighboring plots.
        DISABLED - fauna not currently used.
        """
        # FAUNA TEMPORARILY DISABLED
        # for (row, col), plot in self.plots.items():
        #     neighbors = self.get_neighbors(row, col)
        #     for fauna in plot.get_all_fauna()[:]:
        #         if fauna.get_total_mass() > 0 and neighbors:
        #             target_plot = np.random.choice(neighbors)
        #             if hasattr(fauna, 'update_prey_mass'):
        #                 if np.random.random() < P_PREY_MIGRATION:
        #                     self._migrate_fauna(fauna, target_plot, 'over_prey_capacity', PREY_MIGRATION_RATIO)
        #             elif hasattr(fauna, 'update_predator_mass'):
        #                 if np.random.random() < P_PREDATOR_MIGRATION:
        #                     self._migrate_fauna(fauna, target_plot, 'over_predator_capacity', PREDATOR_MIGRATION_RATIO)
        pass  # Stub - fauna not currently used

    def update_all_plots(self, day: int) -> None:
        """
        Daily update of all plots in the grid with staggered updates to handle dependencies.
        Flora depends on climate and plot changes only, 
        prey lags flora by one day, and predators lag prey by one day.
        
        Update schedule:
        - Day 1: Flora updates (depends on climate)
        - Day 2: Prey updates (depends on flora from day 1)
        - Day 3: Flora updates (depends on climate) 
                + Predator updates (depends on prey from day 2)
        - Day 4: Prey updates (depends on flora from day 3)
        - Day 5: Flora updates (depends on climate) 
                + Predator updates (depends on prey from day 4)
        - Repeat...
        
        Args:
            day (int): The current simulation day (beginning at 1)
        """
        if not isinstance(day, int) or day < 1:
            raise ValueError("day must be a positive integer starting from 1")

        # Update snow heights of all plots first (needed for climate calculations)
        for plot in self.plots.values():
            plot.update_avg_snow_height(day)
        
        # Now process flora and fauna updates for each plot
        for plot in self.plots.values():
            if day % 2 == 1:
                for flora in plot.get_all_flora():
                    flora.update_flora_mass(day)

            # FAUNA TEMPORARILY DISABLED - Focus on flora only
            # if day % 2 == 0:
            #     for fauna in plot.get_all_fauna():
            #         if hasattr(fauna, 'update_prey_mass'):
            #             fauna.update_prey_mass(day)
            # 
            # if day % 2 == 1 and day > 1:
            #     for fauna in plot.get_all_fauna():
            #         if hasattr(fauna, 'update_predator_mass'):
            #             fauna.update_predator_mass(day)
        
        # Clean up all extinct species
        for plot in self.plots.values():
            plot.remove_extinct_species()

        # FAUNA TEMPORARILY DISABLED - migration requires fauna
        # Handle migration (only call once, migrate_species already loops over all plots)
        # if day % 5 == 0:  # every 5th day
        #     self.migrate_species()

    def visualize_biomes(self, biome_colors: Dict[str, str], figsize: Tuple[int, int] = (12, 8), 
                        save_path: Optional[str] = None, ax: Optional = None, day: Optional[int] = None):
        """
        Visualize the grid with different colors for different biomes.
        
        Args:
            biome_colors (Dict[str, str]): Dictionary mapping biome names to colors
            figsize (Tuple[int, int]): Figure size for matplotlib
            save_path (Optional[str]): Path to save the image
            ax: Optional matplotlib axis to update (for real-time visualization)
            day: Optional day number to display in title
        
        Returns:
            The matplotlib axis for reuse in subsequent calls
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib is not available. Cannot create visualization.")
            return None
            
        if not self.plots:
            print("No plots to visualize")
            return None
        
        # 2D array for the visualization
        rows = self.max_row - self.min_row + 1
        cols = self.max_col - self.min_col + 1
        grid = np.full((rows, cols), -1, dtype=int)  # -1 for empty cells (water)
        
        biome_to_int = {biome: i + 1 for i, biome in enumerate(biome_colors.keys())}  # +1 because 0 is water
        
        # Create new figure/axis if not provided (for initial display)
        create_new = (ax is None)
        
        # On first visualization (whenever _initial_blended_grid is None), create and store the blended grid
        if self._initial_blended_grid is None:
            # Fill grid with biome data from plots
            for (row, col), plot in self.plots.items():
                grid_row = row - self.min_row
                grid_col = col - self.min_col
                biome = plot.get_climate().get_biome()
                grid[grid_row, grid_col] = biome_to_int.get(biome, len(biome_colors))
                # Store initial biome for comparison later
                self._initial_biomes[(row, col)] = biome
            
            # Blend biome borders for initial realistic visualization
            grid = self._blend_biome_borders(grid, rows, cols, blend_prob=0.2)
            # Store the blended grid for reuse
            self._initial_blended_grid = grid.copy()
        elif self._initial_blended_grid is not None:
            # Use stored blended grid and update only cells where biome has changed
            grid = self._initial_blended_grid.copy()
            for (row, col), plot in self.plots.items():
                grid_row = row - self.min_row
                grid_col = col - self.min_col
                current_biome = plot.get_climate().get_biome()
                # Check if biome has changed from initial
                initial_biome = self._initial_biomes.get((row, col))
                if initial_biome is not None and current_biome != initial_biome:
                    # Biome changed - update this cell to new biome color (no blending)
                    grid[grid_row, grid_col] = biome_to_int.get(current_biome, len(biome_colors))
                    # Update stored initial biome for this plot
                    self._initial_biomes[(row, col)] = current_biome
        else:
            # Fallback: fill grid with current biome data (shouldn't happen normally)
            for (row, col), plot in self.plots.items():
                grid_row = row - self.min_row
                grid_col = col - self.min_col
                biome = plot.get_climate().get_biome()
                grid[grid_row, grid_col] = biome_to_int.get(biome, len(biome_colors))
        if create_new:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            ax.clear()
            fig = ax.figure

        # Custom colormap - add dark blue for water/empty cells
        water_color = '#001F5C'  # Dark blue ocean color
        colors = [water_color] + list(biome_colors.values())  # Water is index 0
        cmap = mcolors.ListedColormap(colors)
        
        # Replace -1 (empty cells) with 0 (water color index)
        # Biome indices are already 1-based (from biome_to_int mapping above)
        grid[grid == -1] = 0
        
        # Plot the grid with water shown as dark blue
        im = ax.imshow(grid, cmap=cmap, aspect='equal', origin='lower', vmin=0, vmax=len(colors)-1)

        # Colorbar and biome labels (only create colorbar on first call)
        if create_new:
            # Adjust ticks and labels for water + biomes
            cbar_ticks = range(len(colors))
            cbar_labels = ['Water'] + list(biome_colors.keys())
            cbar = plt.colorbar(im, ax=ax, ticks=cbar_ticks)
            cbar.set_ticklabels(cbar_labels)
            cbar.set_label('Biome Type')
        
        # Update title with day if provided
        title = 'Eastern Siberia Biome Distribution'
        if day is not None:
            title = f'Eastern Siberia Biome Distribution - Day {day}'
        ax.set_title(title)
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')

        # Grid lines
        ax.grid(True, which='both', color='black', linewidth=0.5, alpha=0.3)
        # Remove axis tick labels (no numbers on axes)
        ax.set_xticks([])
        ax.set_yticks([])

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Biome visualization saved to {save_path}")

        if create_new:
            plt.show()
            return ax  # Return axis for reuse in subsequent calls
        else:
            plt.draw()  # Update existing plot
            return ax  # Return the same axis

    def _blend_biome_borders(self, grid, rows, cols, blend_prob=0.2):
        """
        Helps blend biome borders in visualize_biomes for more realistic transitions.
        For each border plot (adjacent to a different biome), with probability blend_prob,
        assign the plot the biome of a neighbor.
        Water cells (value -1) are never changed and are never used as blending targets.
        Args:
            grid: 2D numpy array of biome indices (-1 for water, >= 1 for biomes)
            rows: number of rows in grid
            cols: number of columns in grid
            blend_prob: probability to blend a border plot
        Returns:
            grid: blended 2D numpy array
        """
        import random
        WATER_VALUE = -1
        blended_grid = grid.copy()
        for r in range(rows):
            for c in range(cols):
                biome_idx = grid[r, c]
                # Skip water cells - they should never change
                if biome_idx == WATER_VALUE:
                    continue
                
                # Check neighbors for different biome (excluding water)
                neighbor_biomes = set()
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and (dr != 0 or dc != 0):
                            neighbor_biome = grid[nr, nc]
                            # Only consider non-water neighbors that differ
                            if neighbor_biome != biome_idx and neighbor_biome != WATER_VALUE:
                                neighbor_biomes.add(neighbor_biome)
                if neighbor_biomes:
                    # Border plot detected
                    if random.random() < blend_prob:
                        # Assign biome of a random neighbor (never water)
                        blended_grid[r, c] = random.choice(list(neighbor_biomes))
        return blended_grid
    