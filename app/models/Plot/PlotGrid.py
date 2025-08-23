from typing import Dict, Tuple, List, Optional
from .Plot import Plot

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
