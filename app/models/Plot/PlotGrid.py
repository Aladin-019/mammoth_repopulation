from typing import Dict, Tuple, List, Optional
from .Plot import Plot
from app.interfaces.flora_plot_info import PlotInformation
import numpy as np

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

    def migrate_species(self) -> None:
        """
        Simulate species migration between neighboring plots.
        This allows for dynamic ecosystem changes and species spread.
        """
        for (row, col), plot in self.plots.items():
            neighbors = self.get_neighbors(row, col)
            for fauna in plot.get_all_fauna()[:]:
                if fauna.get_total_mass() > 0 and neighbors:
                    target_plot = np.random.choice(neighbors)
                    if hasattr(fauna, 'update_prey_mass'):
                        if np.random.random() < P_PREY_MIGRATION:
                            self._migrate_fauna(fauna, target_plot, 'over_prey_capacity', PREY_MIGRATION_RATIO)
                    elif hasattr(fauna, 'update_predator_mass'):
                        if np.random.random() < P_PREDATOR_MIGRATION:
                            self._migrate_fauna(fauna, target_plot, 'over_predator_capacity', PREDATOR_MIGRATION_RATIO)
