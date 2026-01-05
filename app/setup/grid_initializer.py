from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot.Plot import Plot
from app.models.Climate.Climate import Climate
from app.models.Flora.Grass import Grass
from app.models.Flora.Shrub import Shrub
from app.models.Flora.Tree import Tree
from app.models.Flora.Moss import Moss
from app.models.Flora.Flora import Flora
from app.models.Fauna.Prey import Prey
# Predators not yet enabled
# from app.models.Fauna.Predator import Predator
from typing import List, Optional
from app.globals import *

class GridInitializer:
    # TEMPORARILY DISABLED
    def _create_predator(self, predator_name: str, prey_list, plot: Plot):  # -> Predator:  # Type hint disabled since Fauna import is commented
        # Stub for testing - fauna not currently used
        pass
    def _establish_food_chain_relationships(self, plot):
        """Set up which flora each prey consumes. Mammoths eat grass, shrub, and moss."""
        for fauna in plot.get_all_fauna():
            if fauna.get_name() == 'Mammoth':
                consumable_flora = []
                for flora in plot.get_all_flora():
                    if flora.get_name() in ['Grass', 'Shrub', 'Moss']:
                        consumable_flora.append(flora)
                fauna.consumable_flora = consumable_flora
                for flora in consumable_flora:
                    if fauna not in flora.consumers:
                        flora.consumers.append(fauna)
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
                'prey': [],  # Mammoths will be added manually to specific plots
                # 'predators': []  # Predators not yet enabled
            },
            'northern taiga': {
                'flora': ['tree', 'shrub', 'grass', 'moss'],
                'prey': [],  # Mammoths will be added manually to specific plots
                # 'predators': []  # Predators not yet enabled
            },
            'southern tundra': {
                'flora': ['tree','shrub', 'grass', 'moss'],
                'prey': [],  # Mammoths will be added manually to specific plots
                # 'predators': []  # Predators not yet enabled
            },
            'northern tundra': {
                'flora': ['shrub', 'grass', 'moss'],
                'prey': [],  # Mammoths will be added manually to specific plots
                # 'predators': []  # Predators not yet enabled
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
        Create a plot with appropriate flora for the given biome.
        (Fauna functionality is temporarily disabled)
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
        
        plot = Plot(
            Id=plot_id,
            avg_snow_height=0.1,
            climate=climate,
            plot_area=self.plot_area_km2
        )
    
        climate.set_plot(plot)
        
        self._add_default_flora(plot, biome)
        
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

    # TEMPORARILY UNUSED
    # re-enable it when add default fauna and modify it to add all fauna (not just mammoths)
    # def _add_default_fauna(self, plot: Plot, biome: str) -> None:
    #     """Add default fauna to the plot based on biome. Currently only mammoths."""
    #     if biome not in self.biome_defaults:
    #         return
            
    #     prey_names = self.biome_defaults[biome]['prey']
        
    #     # Add mammoths only (no other prey or predators for now)
    #     for prey_name in prey_names:
    #         if prey_name == 'mammoth':
    #             mammoth = self._create_prey(prey_name, plot)
    #             if mammoth:
    #                 mammoth.plot = plot
    #                 plot.add_fauna(mammoth)
    #                 # Set up food chain: mammoths eat all flora (grass, shrub, moss)
    #                 self._establish_food_chain_relationships(plot)

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

    def _create_flora_for_biome(self, flora_name: str, biome: str, plot: Plot) -> Flora:
        """Create a flora object with appropriate parameters for the biome and flora subtype.
            Necessary values are automatically scaled to current plot size and randomized.

            base_mass = mass of all flora per km^2, which is used to calculate population 
            of only Tree and Shrub flora. Total mass for these are calculated internally.

            Grass and Moss do not use population, but rather total mass directly as their 
            populations are hard to quantify.

        Args:
            flora_name: 'grass', 'shrub', 'tree', 'moss'
            biome: biome type 
            plot: the Plot object to which this flora will belong
        Returns:
            Flora: The created flora object
        """
        if flora_name == 'grass':
            if biome == 'southern taiga':
                base_mass = S_TAIGA_GRASS_MASS
            elif biome == 'northern taiga':
                base_mass = N_TAIGA_GRASS_MASS
            elif biome == 'southern tundra':
                base_mass = S_TUNDRA_GRASS_MASS
            else:  # northern tundra
                base_mass = N_TUNDRA_GRASS_MASS

            return Grass(
                name='Grass',
                description='Hardy grass',
                total_mass=self._get_standardized_float(self._add_random_variation(base_mass, 5.0)),
                population=1,  # grass doesnt use population, value is irrelevant
                ideal_growth_rate=self._add_random_variation(0.01, 5.0),
                ideal_temp_range=(-40.0, 30.0),      # degree Celsius
                ideal_uv_range=(10.0, 60_000.0),     # J/m^2/day
                ideal_hydration_range=(0.01, 1.5),   # kg/m^2/day
                ideal_soil_temp_range=(-5.0, 30.0),  # Not used for grass (shallow roots)
                consumers=[],  # No consumers initially
                root_depth=1,  # Shallow roots for grasses
                plot=plot
            )
        elif flora_name == 'shrub':
            avg_mass = 10.0   # kg (average mass per shrub)
            if biome == 'southern taiga':
                base_mass = S_TAIGA_SHRUB_MASS
            elif biome == 'northern taiga':
                base_mass = N_TAIGA_SHRUB_MASS
            elif biome == 'southern tundra':
                base_mass = S_TUNDRA_SHRUB_MASS
            else:  # northern tundra
                base_mass = N_TUNDRA_SHRUB_MASS

            base_population = base_mass / avg_mass

            return Shrub(
                name='Shrub',
                description='Low-growing shrub',
                avg_mass=self._add_random_variation(avg_mass, 5.0),
                population=self._get_standardized_population(self._add_random_variation(base_population, 5.0)),
                ideal_growth_rate=self._add_random_variation(0.01, 5.0),
                ideal_temp_range=(-40.0, 30.0),     # degree Celsius
                ideal_uv_range=(10.0, 40_000.0),    # J/m^2/day
                ideal_hydration_range=(0.01, 1.5),  # kg/m^2/day
                ideal_soil_temp_range=(-5.0, 20.0), # Not used for shrubs (shallow roots)
                consumers=[],  # No consumers initially
                root_depth=1,  # Shallow root depth for shrubs
                plot=plot
            )
        elif flora_name == 'tree':
            avg_mass = 2400.0   # kg (average mass per tree)
            if biome == 'southern taiga':
                base_mass = S_TAIGA_TREE_MASS
            elif biome == 'northern taiga':
                base_mass = N_TAIGA_TREE_MASS
            elif biome == 'southern tundra':
                base_mass = S_TUNDRA_TREE_MASS
            else:  # northern tundra
                base_mass = N_TUNDRA_TREE_MASS

            base_population = base_mass / avg_mass

            return Tree(
                name='Pine Tree',
                description='Coniferous tree',
                avg_mass=self._add_random_variation(avg_mass, 5.0),
                population=self._get_standardized_population(self._add_random_variation(base_population, 5.0)),
                ideal_growth_rate=self._add_random_variation(0.01, 5.0),
                ideal_temp_range=(-40.0, 20.0),     # degree Celsius
                ideal_uv_range=(10.0, 40_000.0),    # J/m^2/day
                ideal_hydration_range=(0.01, 1.5),  # kg/m^2/day
                ideal_soil_temp_range=(5.0, 20.0),  # degree Celsius
                consumers=[],  # No consumers initially
                root_depth=3,  # Deep roots for trees
                plot=plot,
                single_tree_canopy_cover=self._m2_to_km2(self._add_random_variation(28.0, 15.0)),
                coniferous=True
            )
        elif flora_name == 'moss':
            if biome == 'southern taiga':
                base_mass = S_TAIGA_MOSS_MASS
            elif biome == 'northern taiga':
                base_mass = N_TAIGA_MOSS_MASS
            elif biome == 'southern tundra':
                base_mass = S_TUNDRA_MOSS_MASS
            else:  # northern tundra
                base_mass = N_TUNDRA_MOSS_MASS

            return Moss(
                name='Moss',
                description='Low-growing moss',
                total_mass=self._get_standardized_float(self._add_random_variation(base_mass, 5.0)),
                population=1,  # moss doesnt use population, value is irrelevant
                ideal_growth_rate=self._add_random_variation(0.01, 5.0),
                ideal_temp_range=(-40.0, 5.0),      # degree Celsius
                ideal_uv_range=(10.0, 10_000.0),     # J/m^2/day
                ideal_hydration_range=(0.01, 0.8),   # kg/m^2/day
                ideal_soil_temp_range=(0.0, 15.0), # Not used for moss (shallow roots)
                consumers=[],  # No consumers initially
                root_depth=1,  # Shallow roots for moss
                plot=plot
            )
        
        return None
    
    def _create_prey(self, prey_name: str, plot: Plot, population_per_km2: Optional[float] = None) -> Prey:
        """
        Create a prey object. Currently only supports mammoths.
        
        Args:
            prey_name: Name of the prey ('mammoth')
            plot: The plot to add the prey to
            population_per_km2: Optional population density per km^2. If None, uses default (0.01).
        """
        if prey_name == 'mammoth':
            # Default population if not specified
            if population_per_km2 is None:
                base_population = 0.01  # mammoths per km^2 (default)
            else:
                base_population = population_per_km2
            
            avg_mass = 4000.0  # kg per mammoth
            avg_foot_area = 0.12  # m^2
            avg_steps_taken = 40000  # steps per day
            return Prey(
                name='Mammoth',
                description='Woolly mammoth adapted to cold steppe conditions',
                population=self._get_standardized_population(self._add_random_variation(base_population, 30.0)),
                avg_mass=self._add_random_variation(avg_mass, 20.0),
                ideal_growth_rate=self._add_random_variation(0.2, 10.0),  # ARTIFICIALLY HIGH GROWTH RATE to speed up simulation due to low compute 
                ideal_temp_range=(-60.0, 30.0),  # degree Celsius
                min_food_per_day=self._get_standardized_float(self._add_random_variation(8.0, 10.0)),  # kg per day
                feeding_rate=self._add_random_variation(10.0, 15.0),  # kg per day
                avg_steps_taken=self._get_standardized_float(self._add_random_variation(avg_steps_taken, 20.0)),
                avg_foot_area=self._m2_to_km2(self._add_random_variation(avg_foot_area, 15.0)),
                plot=plot,
                predators=[],        # No predators for now
                consumable_flora=[]  # Will be set when flora is added
            )
        
        return None
    
    def add_mammoth_to_plot(self, plot: Plot, population_per_km2: float = 0.01) -> Prey:
        """
        Add a mammoth to a specific plot with the specified population density.
        
        Args:
            plot: The plot to add mammoths to
            population_per_km2: Population density in mammoths per km^2 (default: 0.01)
        
        Returns:
            The created mammoth Prey object
        """
        mammoth = self._create_prey('mammoth', plot, population_per_km2=population_per_km2)
        if mammoth:
            mammoth.plot = plot
            plot.add_fauna(mammoth)
            # Set up food chain: mammoths eat all flora (grass, shrub, moss)
            self._establish_food_chain_relationships(plot)
        return mammoth



