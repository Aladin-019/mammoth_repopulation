import logging
from typing import List, Optional, Tuple, Union, Any
# Re-enabling fauna - mammoths only for now
from app.models import Fauna, Flora, Climate
from app.interfaces.flora_plot_info import FloraPlotInformation

logger = logging.getLogger(__name__)

from app.globals import *

# Physical constants for snow melting calculations
ETA = 0.75
RHO_SNOW = 100.0
LF = 100_000

# Maximum density constants for flora types (kg/km^2)
MAX_GRASS_DENSITY = 1_000_000.0
MAX_SHRUB_DENSITY = 1_000_000.0
MAX_TREE_DENSITY = 1_000_000.0
MAX_MOSS_DENSITY = 1_000_000.0

# Maximum density constants for fauna types (kg/km^2)
MAX_PREY_DENSITY = 10_000.0
MAX_PREDATOR_DENSITY = 10_000.0

class Plot(FloraPlotInformation):
    """
    Represents a plot of land in the mammoth repopulation simulation.
    
    A plot contains flora, fauna, and environmental conditions including snow cover,
    climate data, and trampling effects. It manages the interactions between different
    species and environmental factors, including snow melting calculations and capacity
    management for flora and fauna populations.
    """
    
    @staticmethod
    def _validate_positive_number(value: Union[int, float], name: str, allow_zero: bool = True) -> None:
        """Validate that a value is a positive number."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got: {type(value).__name__}")
        if value < 0 or (not allow_zero and value == 0):
            raise ValueError(f"{name} must be {'positive' if not allow_zero else 'non-negative'}, got: {value}")
    
    @staticmethod
    def _validate_not_none(value: Any, name: str) -> None:
        """Validate that a value is not None."""
        if value is None:
            raise ValueError(f"{name} cannot be None")
    
    @staticmethod
    def _validate_instance(value: Any, expected_type: Union[type, str], name: str) -> None:
        """Validate that a value is an instance of the expected type."""
        if isinstance(expected_type, str):
            # Handle string type names (for forward references)
            if not hasattr(value, '__class__'):
                raise TypeError(f"{name} must be an instance of {expected_type}, got: {type(value).__name__}")
            
            # For Flora and Fauna, we need to check inheritance hierarchy
            if expected_type == 'Flora':
                # Check if it's Flora or any of its subclasses
                flora_subclasses = ['Flora', 'Grass', 'Shrub', 'Tree', 'Moss']
                if value.__class__.__name__ not in flora_subclasses:
                    raise TypeError(f"{name} must be an instance of Flora or its subclasses, got: {value.__class__.__name__}")
            elif expected_type == 'Fauna':
                # Check if it's Fauna or any of its subclasses
                fauna_subclasses = ['Fauna', 'Prey', 'Predator']
                if value.__class__.__name__ not in fauna_subclasses:
                    raise TypeError(f"{name} must be an instance of Fauna or its subclasses, got: {value.__class__.__name__}")
            else:
                # For other types, check exact match
                if value.__class__.__name__ != expected_type:
                    raise TypeError(f"{name} must be an instance of {expected_type}, got: {value.__class__.__name__}")
        else:
            # Handle actual types
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} must be an instance of {expected_type.__name__}, got: {type(value).__name__}")
    
    def __init__(self, Id: int, avg_snow_height: float, climate: 'Climate', 
                plot_area: float):
        """
        Args:
            Id (int): Unique identifier for the plot.
            avg_snow_height (float): Average snow height in meters.
            climate (Climate): Climate object containing environmental data.
            plot_area (float): Total area of the plot in km².
        Raises:
            ValueError: If any input parameters are invalid.
            TypeError: If any input parameters have incorrect types.  
        Attributes:
            flora (list): List of Flora objects present on the plot.
            fauna (list): List of Fauna objects present on the plot.
            Id (int): Unique identifier for the plot.
            climate (Climate): Climate object containing environmental data.
            avg_snow_height (float): Current average snow height in meters.
            previous_avg_snow_height (float): Previous average snow height in meters.
            compaction_depth (float): Snow height reduction factor per step (70%).
            plot_area (float): Total area of the plot in km^2.
        """
        self._validate_instance(Id, int, "Id")
        self._validate_positive_number(Id, "Id", allow_zero=True)
        
        self._validate_instance(avg_snow_height, float, "avg_snow_height")
        self._validate_positive_number(avg_snow_height, "avg_snow_height", allow_zero=True)
        
        self._validate_instance(climate, 'Climate', "climate")
        
        self._validate_instance(plot_area, float, "plot_area")
        self._validate_positive_number(plot_area, "plot_area", allow_zero=False)
        
        try:
            self.flora = []
            self.fauna = []
            self.Id = Id
            self.climate = climate
            self.avg_snow_height = float(avg_snow_height)
            self.previous_avg_snow_height = float(avg_snow_height)
            self.compaction_depth = 0.7
            self.plot_area = float(plot_area)
            
            self.grass_mass = 0.0
            self.shrub_mass = 0.0
            self.tree_mass = 0.0
            self.moss_mass = 0.0
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Plot {Id}: {e}")

    def get_plot_id(self) -> int:
        """Get the unique identifier for the plot."""
        return self.Id
    
    def add_flora(self, flora: Flora) -> None:
        """Add flora to the plot, preventing duplicates by name."""
        self._validate_not_none(flora, "flora")
        self._validate_instance(flora, 'Flora', "flora")
        if any(f.name == flora.name for f in self.flora):
            raise ValueError(f"Flora with name '{flora.name}' already exists in plot {self.Id}.")
        try:
            self.flora.append(flora)
        except Exception as e:
            raise RuntimeError(f"Failed to add flora {flora.name} to plot {self.Id}: {e}")
    
    def add_fauna(self, fauna: Fauna) -> None:
        """Add fauna to the plot, preventing duplicates by name."""
        self._validate_not_none(fauna, "fauna")
        self._validate_instance(fauna, 'Fauna', "fauna")
        if any(f.name == fauna.name for f in self.fauna):
            raise ValueError(f"Fauna with name '{fauna.name}' already exists in plot {self.Id}.")
        try:
            self.fauna.append(fauna)
        except Exception as e:
            raise RuntimeError(f"Failed to add fauna {fauna.name} to plot {self.Id}: {e}")
    
    def get_a_fauna(self, name: str) -> Optional[Fauna]:
        """Get a specific fauna by name."""
        self._validate_instance(name, str, "name")
        
        try:
            for fauna in self.fauna:
                if fauna.name == name:
                    return fauna
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get fauna {name} from plot {self.Id}: {e}")
    
    def get_a_flora(self, name: str) -> Optional[Flora]:
        """Get a specific flora by name."""
        self._validate_instance(name, str, "name")
        
        try:
            for flora in self.flora:
                if flora.name == name:
                    return flora
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get flora {name} from plot {self.Id}: {e}")
        
    def get_all_fauna(self) -> List[Fauna]:
        """Get all fauna on the plot."""
        return self.fauna
    
    def get_all_flora(self) -> List[Flora]:
        """Get all flora on the plot."""
        return self.flora
    
    def remove_extinct_species(self) -> None:
        """Remove any flora or fauna with mass <= 0 from the plot."""
        self.flora = [flora for flora in self.flora if flora.get_total_mass() > 0]
        self.fauna = [fauna for fauna in self.fauna if fauna.get_total_mass() > 0]

    def get_climate(self) -> 'Climate':
        """Get the climate object associated with this plot."""
        return self.climate
    
    def get_avg_snow_height(self) -> float:
        """Get average snow height."""
        return self.avg_snow_height
    
    def get_previous_snow_height(self) -> float:
        """Get previous average snow height."""
        return self.previous_avg_snow_height
    
    def delta_snow_height(self) -> float:
        """
        Calculate the change in snow height from the previous day.
        
        Returns:
            float: The change in snow height in meters (positive = increase, negative = decrease)
        """
        if self.previous_avg_snow_height is None:
            return 0.0  # No change if we don't have previous data
        
        delta = self.avg_snow_height - self.previous_avg_snow_height
        return delta
    
    def get_current_temperature(self, day: int) -> float:
        """Get current temperature for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_temperature(day)
    
    def get_current_soil_temp(self, day: int) -> float:
        """Get current soil temperature for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_soil_temp(day)
    
    def get_current_snowfall(self, day: int) -> float:
        """Get current snowfall for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_snowfall(day)
    
    def get_current_rainfall(self, day: int) -> float:
        """Get current rainfall for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_rainfall(day)
    
    def get_current_uv(self, day: int) -> float:
        """Get current UV index for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_uv(day)
    
    def get_current_SSRD(self, day: int) -> float:
        """Get current SSRD for the given day."""
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        return self.climate._get_current_SSRD(day)
    
    def get_current_melt_water_mass(self, day: int) -> float:
        """
        Calculate meltwater mass from surface solar radiation downward (SSRD).
        The calculation uses the efficiency factor (ETA) and latent heat of fusion (LF) 
        to convert energy to mass.
        
        Formula: meltwater_mass = (ETA * SSRD) / LF
        
        Args:
            day (int): The day of the year to get SSRD data for. 
        Returns:
            float: Meltwater mass in kg/m².  
        Raises:
            ValueError: If day is not a positive number.
            RuntimeError: If calculation fails.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        try:
            ssrd = self.get_current_SSRD(day)
            return (ETA * ssrd) / LF
        except Exception as e:
            raise RuntimeError(f"Failed to calculate meltwater mass from SSRD on day {day}: {e}")
    
    def get_plot_area(self) -> float:
        """Get the total area of the plot."""
        return self.plot_area
    
    def update_avg_snow_height(self, day: int):
        """
        Update the average snow height based on current snowfall, trampling,
        and solar radiation conditions.
        The previous snow height is stored for tracking changes over time.
        
        Args:
            day (int): The day of the year to get snowfall data for
        Raises:
            ValueError: If day is not a positive number.
            RuntimeError: If snow height update fails.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        try:
            self.previous_avg_snow_height = self.avg_snow_height
            
            # new snowfall
            snowfall = self.get_current_snowfall(day)
            self.avg_snow_height += snowfall
            
            # solar radiation reduction
            ssrd_height_loss = self.snow_height_loss_from_ssrd(day)
            self.avg_snow_height -= ssrd_height_loss
            
            # trampling reduction
            trampled_ratio = self.get_area_trampled_ratio()
            trampling_height_reduction = self.compaction_depth * trampled_ratio * self.avg_snow_height
            self.avg_snow_height -= trampling_height_reduction
            
            if self.avg_snow_height < 0:
                self.avg_snow_height = 0
                
        except Exception as e:
            raise RuntimeError(f"Failed to update snow height on day {day}: {e}")
    

    def _calculate_trampled_area(self) -> float:
        """
        Calculate the total area trampled by all fauna on the plot in km^2
        This is a private method to avoid duplicate calculations.
        
        Returns:
            float: Total trampled area in km²
        Raises:
            RuntimeError: If calculation fails.
        """
        try:
            total_trampled_area = 0.0
            
            for fauna in self.fauna:
                if fauna.get_total_mass() > 0:  # Only count living fauna
                    individual_trampled = fauna.get_avg_foot_area() * fauna.get_avg_steps_taken()
                    total_trampled_area += individual_trampled * fauna.get_population()
            
            # Cap the trampled area at the plot area
            return min(total_trampled_area, self.plot_area)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate total trampled area: {e}")
    
    def get_total_trampled_area(self) -> float:
        """
        Get the total area trampled by all fauna on the plot in km².
        
        Returns:
            float: Total trampled area in km²
        Raises:
            RuntimeError: If calculation fails.
        """
        return self._calculate_trampled_area()
    
    def get_area_trampled_ratio(self) -> float:
        """
        Get the ratio of trampled area to plot area.
        
        Returns:
            float: Ratio of trampled area to plot area
        Raises:
            RuntimeError: If calculation fails.
        """
        try:
            total_trampled_area = self._calculate_trampled_area()
            return (total_trampled_area / self.plot_area)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate trampled area ratio: {e}")
    
    def snow_height_loss_from_ssrd(self, day: int) -> float:
        """
        Calculate snow height loss from surface solar radiation downward (SSRD).
        It first calculates the meltwater mass, then converts it to height loss 
        using snow density and plot area.
        
        Formula: height_loss = meltwater_mass / (RHO_SNOW * plot_area_m2)
        
        Args:
            day (int): The day of the year to get SSRD data for.
        Returns:
            float: Snow height loss in meters. 
        Raises:
            ValueError: If day is not a positive number.
            RuntimeError: If calculation fails.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        try:
            meltwater_mass = self.get_current_melt_water_mass(day)
            plot_area_m2 = self.plot_area * 1_000_000 # convert plot_area from km^2 to m^2
            ssrd_height_loss = meltwater_mass / (RHO_SNOW * plot_area_m2)
            
            return ssrd_height_loss
        except Exception as e:
            raise RuntimeError(f"Failed to calculate snow height loss from SSRD on day {day}: {e}")
    
    def calculate_flora_masses(self) -> None:
        """
        Calculate the total masses of each flora type by summing
        the masses of all individual flora objects of each type.
        Stores the results as instance variables for use by capacity methods.
        
        Raises:
            RuntimeError: If mass calculation fails.
        """
        try:
            grass_mass = 0.0
            shrub_mass = 0.0
            tree_mass = 0.0
            moss_mass = 0.0
            
            for flora in self.flora:
                if flora.__class__.__name__ == "Grass":
                    grass_mass += flora.get_total_mass()
                elif flora.__class__.__name__ == "Shrub":
                    shrub_mass += flora.get_total_mass()
                elif flora.__class__.__name__ == "Tree":
                    tree_mass += flora.get_total_mass()
                elif flora.__class__.__name__ == "Moss":
                    moss_mass += flora.get_total_mass()
            
            # Store as instance variables for capacity methods
            self.grass_mass = grass_mass
            self.shrub_mass = shrub_mass
            self.tree_mass = tree_mass
            self.moss_mass = moss_mass
            
        except Exception as e:
            raise RuntimeError(f"Failed to calculate flora masses: {e}")
    
    def get_flora_masses(self) -> Tuple[float, float, float, float]:
        """
        Get the current flora masses.
        
        Returns:
            Tuple[float, float, float, float]: contains (grass_mass, shrub_mass, tree_mass, moss_mass) in kg.
        """
        return self.grass_mass, self.shrub_mass, self.tree_mass, self.moss_mass
    
    def get_flora_mass_composition(self) -> Tuple[float, float, float, float]:
        """
        This method calculates what percentage of the total flora biomass
        each flora type represents.
        
        Returns:
            Tuple[float, float, float, float]: contains (grass_ratio, shrub_ratio, tree_ratio, moss_ratio)  
        Raises:
            RuntimeError: If composition calculation fails.
        """
        try:
            self.calculate_flora_masses() # Calculate fresh flora masses
            grass_mass, shrub_mass, tree_mass, moss_mass = self.get_flora_masses()
            total_mass = grass_mass + shrub_mass + tree_mass + moss_mass
            
            if total_mass == 0:
                return 0.0, 0.0, 0.0, 0.0
            
            grass_ratio = grass_mass / total_mass
            shrub_ratio = shrub_mass / total_mass
            tree_ratio = tree_mass / total_mass
            moss_ratio = moss_mass / total_mass
            
            return grass_ratio, shrub_ratio, tree_ratio, moss_ratio
            
        except Exception as e:
            raise RuntimeError(f"Failed to get flora mass composition: {e}")
    
    # Capacity management methods - Absolute maximum density limits per km^2
    
    def over_grass_capacity(self) -> bool:
        """
        Check if grass mass exceeds its maximum density per km^2.
        precondition: calculate_flora_masses() must be called first (for current timestep)
        
        Returns:
            bool: True if grass mass exceeds maximum density, False otherwise.
        """
        grass_mass, _, _, _ = self.get_flora_masses()
        return grass_mass > (self.plot_area * MAX_GRASS_DENSITY)
    
    def over_shrub_capacity(self) -> bool:
        """
        Check if shrub mass exceeds its maximum density per km^2.
        precondition: calculate_flora_masses() must be called first (for current timestep)
        Returns:
            bool: True if shrub mass exceeds maximum density, False otherwise.
        """
        _, shrub_mass, _, _ = self.get_flora_masses()
        return shrub_mass > (self.plot_area * MAX_SHRUB_DENSITY)
    
    def over_tree_capacity(self) -> bool:
        """
        Check if tree mass exceeds its maximum density per km^2.
        precondition: calculate_flora_masses() must be called first (for current timestep)

        Returns:
            bool: True if tree mass exceeds maximum density, False otherwise.
        """
        _, _, tree_mass, _ = self.get_flora_masses()
        return tree_mass > (self.plot_area * MAX_TREE_DENSITY)
    
    def over_moss_capacity(self) -> bool:
        """
        Check if moss mass exceeds its maximum density per km^2.
        precondition: calculate_flora_masses() must be called first (for current timestep)

        Returns:
            bool: True if moss mass exceeds maximum density, False otherwise.
        """
        _, _, _, moss_mass = self.get_flora_masses()
        return moss_mass > (self.plot_area * MAX_MOSS_DENSITY)
    
    def over_prey_capacity(self) -> bool:
        """
        Check if prey mass exceeds absolute maximum density per km^2.
        precondition: calculate_flora_masses() must be called first (for current timestep)
        
        Returns:
            bool: True if prey mass exceeds maximum density, False otherwise.
        """
        prey_mass = sum(fauna.get_total_mass() for fauna in self.fauna if fauna.__class__.__name__ == "Prey")
        return prey_mass > (self.plot_area * MAX_PREY_DENSITY)
    
    # TEMPORARILY DISABLED
    def over_predator_capacity(self) -> bool:
        """
        Check if predator mass exceeds absolute maximum density per km^2.
        DISABLED - returns False since fauna not currently used.
        """
        # TEMPORARILY DISABLED
        # predator_mass = sum(fauna.get_total_mass() for fauna in self.fauna if fauna.__class__.__name__ == "Predator")
        # return predator_mass > (self.plot_area * MAX_PREDATOR_DENSITY)
        return False  # Stub - fauna not currently used
    
    def _determine_biome_from_flora(self) -> Optional[str]:
        """
        Determine the appropriate biome based on current flora mass composition.
        Uses simplified logic based on typical ratios from grid_initializer:
        """
        try:
            grass_ratio, shrub_ratio, tree_ratio, moss_ratio = self.get_flora_mass_composition()
            current_flora_ratios = (grass_ratio, shrub_ratio, tree_ratio, moss_ratio)
            total_mass = sum(self.get_flora_masses())
            
            # If no flora, don't change biome
            if total_mass == 0:
                return None
            
            s_taiga_ratios = (S_TAIGA_GRASS_MASS / S_TAIGA_TOTAL_MASS, S_TAIGA_SHRUB_MASS / S_TAIGA_TOTAL_MASS, S_TAIGA_TREE_MASS / S_TAIGA_TOTAL_MASS, S_TAIGA_MOSS_MASS / S_TAIGA_TOTAL_MASS)
            n_taiga_ratios = (N_TAIGA_GRASS_MASS / N_TAIGA_TOTAL_MASS, N_TAIGA_SHRUB_MASS / N_TAIGA_TOTAL_MASS, N_TAIGA_TREE_MASS / N_TAIGA_TOTAL_MASS, N_TAIGA_MOSS_MASS / N_TAIGA_TOTAL_MASS)
            s_tundra_ratios = (S_TUNDRA_GRASS_MASS / S_TUNDRA_TOTAL_MASS, S_TUNDRA_SHRUB_MASS / S_TUNDRA_TOTAL_MASS, S_TUNDRA_TREE_MASS / S_TUNDRA_TOTAL_MASS, S_TUNDRA_MOSS_MASS / S_TUNDRA_TOTAL_MASS)
            n_tundra_ratios = (N_TUNDRA_GRASS_MASS / N_TUNDRA_TOTAL_MASS, N_TUNDRA_SHRUB_MASS / N_TUNDRA_TOTAL_MASS, N_TUNDRA_TREE_MASS / N_TUNDRA_TOTAL_MASS, N_TUNDRA_MOSS_MASS / N_TUNDRA_TOTAL_MASS)
            
            # Calculate Euclidean distance between current ratios and each biome's ideal ratios
            def distance(ratios1, ratios2):
                return sum((a - b) ** 2 for a, b in zip(ratios1, ratios2)) ** 0.5
            
            biome_distances = [
                ('southern taiga', distance(current_flora_ratios, s_taiga_ratios)),
                ('northern taiga', distance(current_flora_ratios, n_taiga_ratios)),
                ('southern tundra', distance(current_flora_ratios, s_tundra_ratios)),
                ('northern tundra', distance(current_flora_ratios, n_tundra_ratios))
            ]
            
            closest_biome = min(biome_distances, key=lambda x: x[1])[0]
            
            current_biome = self.climate.get_biome()
            if closest_biome != current_biome:
                logger.debug(f"Plot {self.Id}: Flora ratios indicate biome change from {current_biome} to {closest_biome} "
                           f"(current ratios: grass={grass_ratio:.3f}, shrub={shrub_ratio:.3f}, tree={tree_ratio:.3f}, moss={moss_ratio:.3f})")
                return closest_biome
            
            return None
        except Exception as e:
            logger.error(f"Failed to determine biome from flora for plot {self.Id}: {e}")
            return None
    
    def check_and_update_biome(self) -> bool:
        """
        Check flora ratios and mammoth presence to update biome if they indicate a significant change.
        First checks for mammoth steppe.
        then uses distance-based classification for other biomes.
        
        Returns:
            bool: True if biome was changed, False otherwise
        """
        try:
            current_biome = self.climate.get_biome()
            is_steppe_conditions_met = self.climate.is_steppe()
            
            # Steppe conditions are met - set to steppe
            if is_steppe_conditions_met:
                if current_biome != 'mammoth steppe':
                    logger.info(f"Plot {self.Id}: Conditions indicate mammoth steppe (was {current_biome})")
                    # Store the current biome as the original before changing to steppe
                    if self.climate.original_biome is None:
                        self.climate.original_biome = current_biome
                    self.climate.set_biome('mammoth steppe')
                    return True
                return False  # Already steppe
            
            # Steppe conditions not met
            if current_biome == 'mammoth steppe':
                new_biome = self._determine_biome_from_flora()
                if new_biome:
                    logger.info(f"Plot {self.Id}: Steppe conditions no longer met, changing to {new_biome} based on flora composition")
                    self.climate.set_biome(new_biome)
                    return True
                return False
            else:
                # Not steppe - determine new biome normally based on flora
                new_biome = self._determine_biome_from_flora()
                if new_biome:
                    self.climate.set_biome(new_biome)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to check and update biome for plot {self.Id}: {e}")
            return False