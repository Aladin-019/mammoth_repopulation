from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot.Plot import Plot
from app.models.Climate.Climate import Climate

class GridInitializer:
    def _create_flora_for_biome(self, flora_name, biome, plot):
        # Stub for testing
        return None
    def _add_northern_taiga_plot_id(self, plot_id):
        # Stub for testing
        pass
    def _create_prey_for_biome(self, prey_name, biome, plot):
        # Stub for testing
        return None
    def _create_predator_for_biome(self, predator_name, biome, prey_list, plot):
        # Stub for testing
        return None
    def _establish_food_chain_relationships(self, plot):
        # Stub for testing
        pass
    def _update_predator_prey_lists(self, plot):
        # Stub for testing
        pass

    """
    Helper class to automatically initialize plots in a PlotGrid based on biome data.
    
    Automatically handles different grid resolutions by scaling biomass and population
    values appropriately. All base values are defined per 1 km^2 and automatically
    scaled to the current plot size.

    lat_step: The latitude step size (in degrees) for the grid.
    lon_step: The longitude step size (in degrees) for the grid.
    """
    
    def __init__(self, lat_step: float = 0.5, lon_step: float = 0.5):
        if lat_step <= 0 or lon_step <= 0:
            raise ValueError("lat_step and lon_step must be greater than 0")

        self.plot_grid = PlotGrid()  # The PlotGrid to initialize
        self.plot_counter = 0        # Simple counter for plot IDs

        # Calculate plot area based on resolution
        # At equator: 1° latitude ≈ 111 km, 1° longitude ≈ 111 km
        # Using average for Siberia (around 65°N): 1° longitude ≈ 47 km

        # Base plot area in km^2 (1° × 1° at 65°N)
        base_lat_km = 111.0  # 1° latitude = 111 km (constant)
        base_lon_km = 47.0   # 1° longitude ≈ 47 km at 65°N (Siberia average)

        # Calculate actual plot area based on resolution
        self.plot_area_km2 = (lat_step * base_lat_km) * (lon_step * base_lon_km)

        # Standardization factor: calculate how much larger plots are compared to 1 km^2
        self.standardization_factor = self.plot_area_km2 / 1.0  # Directly related to plot area

        print(f"Grid Initializer: Resolution {lat_step}°×{lon_step}°.\nPlot area = {self.plot_area_km2:.1f} km^2")
        print(f"Standardization: plots are {self.standardization_factor:.1f}x larger than 1 km^2 plots")

        # Default flora and fauna for each biome
        self.biome_defaults = {
            'southern taiga': {
                'flora': ['tree', 'shrub', 'grass', 'moss'],
                'prey': ['deer', 'mammoth'],
                'predators': ['wolf']
            },
            'northern taiga': {
                'flora': ['tree', 'shrub', 'grass', 'moss'],
                'prey': ['deer', 'mammoth'],
                'predators': ['wolf']
            },
            'southern tundra': {
                'flora': ['shrub', 'grass', 'moss'],
                'prey': ['deer', 'mammoth'],
                'predators': ['wolf']
            },
            'northern tundra': {
                'flora': ['shrub', 'grass', 'moss'],
                'prey': ['deer', 'mammoth'],
                'predators': ['wolf']
            }
        }

    def update_resolution(self, lat_step: float, lon_step: float) -> None:
        """Update the grid resolution and recalculate plot area and standardization factor."""
        
        base_lat_km = 111.0  # 1° latitude = 111 km (constant)
        base_lon_km = 47.0   # 1° longitude ≈ 47 km at 65°N (Siberia average)
        
        # Calculate actual plot area and standardization factor
        self.plot_area_km2 = (lat_step * base_lat_km) * (lon_step * base_lon_km)
        self.standardization_factor = self.plot_area_km2 / 1.0
        
        print(f"Resolution updated: {lat_step}°×{lon_step}° → Plot area = {self.plot_area_km2:.1f} km²")
        print(f"  Standardization: plots are {self.standardization_factor:.1f}x larger than 1 km² plots")
    
    def get_resolution_info(self) -> dict:
        """Get current resolution information."""
        return {
            'plot_area_km2': self.plot_area_km2,
            'standardization_factor': self.standardization_factor,
            'base_resolution_km2': 1.0
        }

    def get_plot_grid(self) -> PlotGrid:
        """Get the initialized plot grid."""
        return self.plot_grid
    
    def create_plot_from_biome(self, biome: str) -> Plot:
        """
        Create a plot with appropriate flora and fauna for the given biome.
        """
        # Create climate for this plot - Plot=None initially to avoid circular reference
        climate = Climate(biome, None)

        if self.plot_counter < 0:
            raise ValueError("Plot counter cannot be negative")

        if not isinstance(biome, str):
            raise TypeError("Biome must be a string")

        if biome not in self.biome_defaults:
            raise ValueError(f"Biome '{biome}' not recognized. Available: {list(self.biome_defaults.keys())}")

        plot_id = self.plot_counter  # Simple sequential ID starting from 0
        self.plot_counter += 1       # Increment counter for next plot
        
        # Track northern taiga plots for finding the central one
        if biome == 'northern taiga':
            self._add_northern_taiga_plot_id(plot_id)
        
        plot = Plot(
            Id=plot_id,
            avg_snow_height=0.1,
            climate=climate,
            plot_area=self.plot_area_km2
        )
    
        climate.set_plot(plot)
        
        self._add_default_flora(plot, biome)
        self._add_default_fauna(plot, biome)
        
        return plot

    def _add_default_flora(self, plot: Plot, biome: str) -> None:
        """Add default flora to the plot based on biome."""
        if biome not in self.biome_defaults:
            return
            
        flora_names = self.biome_defaults[biome]['flora']
        
        for flora_name in flora_names:
            # Create flora with appropriate parameters for the biome
            flora = self._create_flora_for_biome(flora_name, biome, plot)
            if flora:
                plot.add_flora(flora)

    def _add_default_fauna(self, plot: Plot, biome: str) -> None:
        """Add default fauna to the plot based on biome."""
        if biome not in self.biome_defaults:
            return
            
        prey_names = self.biome_defaults[biome]['prey']
        predator_names = self.biome_defaults[biome]['predators']
        
        prey_list = []
        for prey_name in prey_names:
            if prey_name == 'mammoth':
                # Don't add mammoths yet - we do this after all plots are created
                continue
            else:
                prey = self._create_prey_for_biome(prey_name, biome, plot)
                if prey:
                    prey.plot = plot
                    plot.add_fauna(prey)
                    prey_list.append(prey)

        for predator_name in predator_names:
            predator = self._create_predator_for_biome(predator_name, biome, prey_list, plot)
            if predator:
                predator.plot = plot
                plot.add_fauna(predator)
        
        self._establish_food_chain_relationships(plot)
        
        self._update_predator_prey_lists(plot)

    def _get_standardized_float(self, base_float: float) -> float:
        """Convert from base 1km^2 to standardized value based on current plot size."""
        return base_float * self.standardization_factor

    def _get_standardized_population(self, base_population_per_km2: float) -> int:
        """Convert 1 km^2 population to standardized value based on current plot size population."""
        return max(0, int(base_population_per_km2 * self.standardization_factor))

    def _m2_to_km2(self, area_m2: float) -> float:
        """Convert area from square meters to square kilometers."""
        return area_m2 / 1_000_000  # 1 km^2 = 1,000,000 m^2
    
    def _add_random_variation(self, base_value: float, variation_percent: float = 15.0) -> float:
        """
        Add some random variation to a base value, by multiplying it by a random multiplier within variation_percent.

        Args:
            base_value (float): The base value to vary
            variation_percent (float): Percentage variation (default: ±15%)
        Returns:
            float: Base value with random variation applied
        """
        import random
        
        variation_decimal = variation_percent / 100.0
        
        # Generate multiplier range between (1 - variation) and (1 + variation)
        min_multiplier = 1.0 - variation_decimal
        max_multiplier = 1.0 + variation_decimal

        random_multiplier = random.uniform(min_multiplier, max_multiplier)

        return base_value * random_multiplier




