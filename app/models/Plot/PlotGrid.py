from typing import Dict, Tuple, List, Optional, Any
from .Plot import Plot
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ** DAILY MIGRATION PROBABILITIES **
# Articifically high daily migration probabilities to speed up simulation due to low compute
P_PREY_MIGRATION = 0.2
P_PREDATOR_MIGRATION = 0.4

# ** MIGRATION MASS RATIOS **
PREY_MIGRATION_RATIO = 0.2
PREDATOR_MIGRATION_RATIO = 0.2


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
        self._initial_blended_grid: Optional[np.ndarray] = None
        self._current_biomes: Dict[Tuple[int, int], str] = {}
        self._colorbar = None
        self._total_pop_text = None
    
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

    def _migrate_fauna(self, fauna: Any, target_plot: Plot, capacity_check: str, migration_percent: float) -> None:
        """
        Helper to migrate fauna between plots.
        Args:
            fauna: The fauna instance to migrate
            target_plot: The target Plot instance
            capacity_check (str): Method name to check capacity on target plot
            migration_percent (float): Percentage of mass to migrate
        """
        # Block migration if source fauna has less than avg mass (non-viable population)
        if fauna.get_total_mass() < getattr(fauna, 'avg_mass', 1):
            return
        # Only migrate to target plot if its not over capacity (has space)
        if not getattr(target_plot, capacity_check)():
            migration_mass = fauna.get_total_mass() * migration_percent
            if migration_mass > 0:
                target_fauna = target_plot.get_a_fauna(fauna.name)
                if target_fauna:
                    existing_mass = target_fauna.get_total_mass()
                    target_fauna.set_total_mass(existing_mass + migration_mass)
                    fauna.set_total_mass(fauna.get_total_mass() - migration_mass)
                else:
                    # Create a new fauna instance in the target plot
                    try:
                        new_fauna = fauna.__class__.from_existing_with_mass(fauna, migration_mass, plot=target_plot)
                        target_plot.add_fauna(new_fauna)
                        fauna.set_total_mass(fauna.get_total_mass() - migration_mass)
                    except Exception as e:
                        logger.error(f"Failed to migrate fauna '{fauna.name}' with mass {migration_mass} to plot {target_plot}: {e}", exc_info=True)

    def migrate_species(self) -> None:
        """
        Simulate species migration between neighboring plots.
        """
        for (row, col), plot in self.plots.items():
            neighbors = self.get_neighbors(row, col)
            for fauna in plot.get_all_fauna()[:]:  # Use [:] to avoid modifying list while iterating
                if fauna.get_total_mass() > 0 and neighbors:
                    target_plot = np.random.choice(neighbors)
                    if hasattr(fauna, 'update_prey_mass'):
                        if np.random.random() < P_PREY_MIGRATION:
                            self._migrate_fauna(fauna, target_plot, 'over_prey_capacity', PREY_MIGRATION_RATIO)
                    elif hasattr(fauna, 'update_predator_mass'):
                        if np.random.random() < P_PREDATOR_MIGRATION:
                            self._migrate_fauna(fauna, target_plot, 'over_predator_capacity', PREDATOR_MIGRATION_RATIO)

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
                # Calculate flora masses before updates for capacity checks
                plot.calculate_flora_masses()
                for flora in plot.get_all_flora():
                    flora.update_flora_mass(day)

            # Update prey on even days
            if day % 2 == 0:
                for fauna in plot.get_all_fauna():
                    if hasattr(fauna, 'update_prey_mass'):
                        fauna.update_prey_mass(day)
            
            # Update predators on odd days (after day 1)
            if day % 2 == 1 and day > 1:
                for fauna in plot.get_all_fauna():
                    if hasattr(fauna, 'update_predator_mass'):
                        fauna.update_predator_mass(day)
        
        # Clean up all extinct species
        for plot in self.plots.values():
            plot.remove_extinct_species()

        # Handle migration - migrate_species loops over all plots
        if day % 5 == 0:
            self.migrate_species()

        # Update biomes for each plot
        for plot in self.plots.values():
            plot.check_and_update_biome()

    def visualize_biomes(self, biome_colors: Dict[str, str], *args, day: Optional[int] = None, **kwargs):
        """
        Create and return a Plotly figure showing the biome grid.

        Args:
            biome_colors (Dict[str, str]): Mapping of biome names to hex colors.
            day (Optional[int]): Optional day number to include in the title.

        Returns:
            A Plotly `Figure` representing the biome grid.
        """
        import plotly.graph_objs as go
        try:
            import plotly.graph_objs as go

            # Clear cached blended grid and biome states before plotting
            self._initial_blended_grid = None
            self._current_biomes = {}

            if not self.plots:
                print("No plots to visualize")
                return None

            rows, cols, grid, biome_to_int, int_to_biome, int_to_color = \
                self._prepare_grid_and_mappings(biome_colors)

            grid = self._apply_blending_and_cache(grid, rows, cols, biome_to_int)

            # Build Plotly figure
            fig = go.Figure(data=go.Heatmap(
                z=grid,
                x=list(range(self.min_col, self.max_col + 1)),
                y=list(range(self.min_row, self.max_row + 1)),
                colorscale=[[i / (len(int_to_color) - 1), c] for i, c in int_to_color.items()],
                showscale=False,
                hovertemplate='Row: %{y}<br>Col: %{x}<br>Biome: %{customdata}',
                customdata=np.vectorize(lambda v: int_to_biome.get(v, 'Water'))(grid),
                zsmooth=False,
            ))

            mammoth_count, total_mammoth_population = self._add_mammoth_borders(fig)

            self._add_legend_annotations(fig, biome_colors)

            # Title and layout
            title = 'Mammoth Repopulation Simulator'
            if day is not None:
                title = f'Eastern Siberia Biome Map - Day {day}'
            fig.update_layout(
                title=title,
                xaxis_title='Column',
                yaxis_title='Row',
                margin=dict(l=40, r=40, t=60, b=120),
                width=900, height=700,
                xaxis=dict(constrain='domain'),
                yaxis=dict(constrain='domain'),
            )
            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)

            # Add mammoth indicator and population text
            fig.add_annotation(
                x=cols + 0.5, y=rows - 0.5,
                text="Mammoths are present",
                showarrow=False,
                font=dict(size=10, color="black"),
                xref="x", yref="y"
            )
            fig.add_annotation(
                x=cols + 0.5, y=rows - 1.5,
                text=f"<b>Mammoth population: {total_mammoth_population}</b>",
                showarrow=False,
                font=dict(size=10, color="black", family="Arial"),
                xref="x", yref="y"
            )

            return fig
        except Exception:
            logger.exception("Failed to build biome visualization")
            return None

    def _prepare_grid_and_mappings(self, biome_colors: Dict[str, str]):
        """Prepare numeric grid and color mappings for plotting."""
        rows = self.max_row - self.min_row + 1
        cols = self.max_col - self.min_col + 1
        grid = np.full((rows, cols), -1, dtype=int)  # -1 for empty cells (water)
        biome_to_int = {biome: i + 1 for i, biome in enumerate(biome_colors.keys())}  # +1 because 0 is water
        int_to_biome = {i + 1: biome for i, biome in enumerate(biome_colors.keys())}
        int_to_color = {0: '#001F5C'}  # Water color
        for i, (biome, color) in enumerate(biome_colors.items()):
            int_to_color[i + 1] = color

        # Fill grid with current biome data from plots
        for (row, col), plot in self.plots.items():
            grid_row = row - self.min_row
            grid_col = col - self.min_col
            biome = plot.get_climate().get_biome()
            grid[grid_row, grid_col] = biome_to_int.get(biome, 0)

        return rows, cols, grid, biome_to_int, int_to_biome, int_to_color

    def _apply_blending_and_cache(self, grid: np.ndarray, rows: int, cols: int, biome_to_int: Dict[str, int]) -> np.ndarray:
        """Apply border blending and update or reuse cached blended grid."""
        # Apply border blending only on initial render (day 0), then reuse that blended grid
        create_new = True  # Plotly always creates new figure
        if create_new and self._initial_blended_grid is None:
            for (row, col), plot in self.plots.items():
                self._current_biomes[(row, col)] = plot.get_climate().get_biome()
            grid = self._blend_biome_borders(grid, rows, cols, blend_prob=0.2)
            grid[grid == -1] = 0
            self._initial_blended_grid = grid.copy()
        elif self._initial_blended_grid is not None:
            grid = self._initial_blended_grid
            for (row, col), plot in self.plots.items():
                grid_row = row - self.min_row
                grid_col = col - self.min_col
                actual_biome = plot.get_climate().get_biome()
                stored_biome = self._current_biomes.get((row, col))
                if stored_biome is not None and actual_biome != stored_biome:
                    grid[grid_row, grid_col] = biome_to_int.get(actual_biome, 0)
                self._current_biomes[(row, col)] = actual_biome
        else:
            grid[grid == -1] = 0

        return grid

    def _add_mammoth_borders(self, fig):
        """Add rectangular borders for plots containing mammoths and return counts."""
        mammoth_border_color = '#8B4513'
        mammoth_count = 0
        total_mammoth_population = 0
        for (row, col), plot in self.plots.items():
            grid_row = row - self.min_row
            grid_col = col - self.min_col
            has_mammoths = False
            for fauna in plot.get_all_fauna():
                if fauna.get_name() == 'Mammoth' and fauna.get_total_mass() > 0:
                    has_mammoths = True
                    plot_pop = fauna.get_population()
                    total_mammoth_population += plot_pop
            if has_mammoths:
                mammoth_count += 1
                fig.add_shape(
                    type="rect",
                    x0=grid_col - 0.5, y0=grid_row - 0.5,
                    x1=grid_col + 0.5, y1=grid_row + 0.5,
                    line=dict(color=mammoth_border_color, width=3),
                    fillcolor="rgba(0,0,0,0)",
                    layer="above"
                )
        return mammoth_count, total_mammoth_population

    def _add_legend_annotations(self, fig, biome_colors: Dict[str, str]):
        """Add a simple vertical legend as shapes + annotations (keeps previous layout)."""
        legend_labels = ['Water'] + list(biome_colors.keys())
        legend_colors = ['#001F5C'] + list(biome_colors.values())
        legend_y = -1.5
        # Vertical legend: colored box, name to right, center-aligned
        legend_x = -1.5
        box_height = 0.4
        for i, (label, color) in enumerate(zip(legend_labels, legend_colors)):
            # Draw colored box
            fig.add_shape(
                type="rect",
                x0=legend_x, y0=legend_y + i * box_height,
                x1=legend_x + 0.5, y1=legend_y + i * box_height + box_height * 0.8,
                line=dict(color='black', width=2),
                fillcolor=color,
                layer="above"
            )
            # Add biome name to right, center-aligned (slightly smaller font to avoid clipping)
            fig.add_annotation(
                x=legend_x + 0.7, y=legend_y + i * box_height + box_height * 0.4,
                text=label,
                showarrow=False,
                font=dict(size=10, color='black', family='Arial'),
                xref="x", yref="y",
                align="left",
                valign="middle"
            )
    def _blend_biome_borders(self, grid: np.ndarray, rows: int, cols: int, blend_prob: float = 0.2) -> np.ndarray:
        """Blend biome borders for more realistic transitions.

        For each border plot (adjacent to a different biome), with probability
        ``blend_prob`` assign the plot the biome of a neighbor. Water cells
        (value -1) are never changed.
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
