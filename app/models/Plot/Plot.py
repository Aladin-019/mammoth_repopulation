import logging
from typing import List, Optional, Tuple
from app.models import Fauna, Flora, Climate
from app.interfaces.flora_plot_info import FloraPlotInformation

logger = logging.getLogger(__name__)

# Physical constants for snow melting calculations
ETA = 0.35
RHO_SNOW = 300.0
LF = 334_000

# Maximum density constants for flora types (kg/km^2)
MAX_GRASS_DENSITY = 3000.0    # Grass can grow densely
MAX_SHRUB_DENSITY = 1500.0    # Shrubs need more space
MAX_TREE_DENSITY = 800.0      # Trees need significant space
MAX_MOSS_DENSITY = 200.0      # Moss grows in patches

# Maximum density constants for fauna types (kg/km^2)
MAX_PREY_DENSITY = 500.0      # Maximum herbivore density
MAX_PREDATOR_DENSITY = 50.0   # Maximum predator density

class Plot(FloraPlotInformation):
    """
    Represents a plot of land in the mammoth repopulation simulation.
    
    A plot contains flora, fauna, and environmental conditions including snow cover,
    climate data, and trampling effects. It manages the interactions between different
    species and environmental factors, including snow melting calculations and capacity
    management for flora and fauna populations.
    """
    
    @staticmethod
    def _validate_positive_number(value, name: str, allow_zero: bool = True):
        """Validate that a value is a positive number."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got: {type(value).__name__}")
        if value < 0 or (not allow_zero and value == 0):
            raise ValueError(f"{name} must be {'positive' if not allow_zero else 'non-negative'}, got: {value}")
    
    @staticmethod
    def _validate_not_none(value, name: str):
        """Validate that a value is not None."""
        if value is None:
            raise ValueError(f"{name} cannot be None")
    
    @staticmethod
    def _validate_instance(value, expected_type, name: str):
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
                total_area_trampled: float, plot_area: float):
        """
        Args:
            Id (int): Unique identifier for the plot.
            avg_snow_height (float): Average snow height in meters.
            climate (Climate): Climate object containing environmental data.
            total_area_trampled (float): Total area trampled by fauna in km².
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
            total_area_trampled (float): Total area trampled by fauna in km^2.
        """
        self._validate_instance(Id, int, "Id")
        self._validate_positive_number(Id, "Id", allow_zero=True)
        
        self._validate_instance(avg_snow_height, float, "avg_snow_height")
        self._validate_positive_number(avg_snow_height, "avg_snow_height", allow_zero=True)
        
        self._validate_instance(climate, 'Climate', "climate")
        
        self._validate_instance(total_area_trampled, float, "total_area_trampled")
        self._validate_positive_number(total_area_trampled, "total_area_trampled", allow_zero=True)
        
        self._validate_instance(plot_area, float, "plot_area")
        self._validate_positive_number(plot_area, "plot_area", allow_zero=False)
        
        try:
            self.flora = []
            self.fauna = []
            self.Id = Id
            self.climate = climate
            self.avg_snow_height = float(avg_snow_height)
            self.previous_avg_snow_height = None
            self.compaction_depth = 0.7
            self.plot_area = float(plot_area)
            self.total_area_trampled = float(total_area_trampled)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Plot {Id}: {e}")
    
    def add_flora(self, flora):
        """Add flora to the plot."""
        self._validate_not_none(flora, "flora")
        self._validate_instance(flora, 'Flora', "flora")
        
        try:
            self.flora.append(flora)
        except Exception as e:
            raise RuntimeError(f"Failed to add flora {flora.name} to plot {self.Id}: {e}")
    
    def add_fauna(self, fauna):
        """Add fauna to the plot."""
        self._validate_not_none(fauna, "fauna")
        self._validate_instance(fauna, 'Fauna', "fauna")
        
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
        
    def get_all_fauna(self) -> list:
        """Get all fauna on the plot."""
        return self.fauna
    
    def get_all_flora(self) -> list:
        """Get all flora on the plot."""
        return self.flora
    
    def get_avg_snow_height(self) -> float:
        """Get average snow height."""
        return self.avg_snow_height
    
    def get_previous_snow_height(self) -> float:
        """Get previous average snow height."""
        return self.previous_avg_snow_height
    
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
    
    def update_area_trampled(self, additional_area: float):
        """
        Update the total area trampled by fauna.
        
        Args:
            additional_area (float): Additional area trampled in km^2.
        Raises:
            ValueError: If additional_area is not a positive number.
            RuntimeError: If area update fails.
        """
        self._validate_instance(additional_area, float, "additional_area")
        self._validate_positive_number(additional_area, "additional_area")
        
        try:
            self.total_area_trampled += additional_area
        except Exception as e:
            raise RuntimeError(f"Failed to update trampled area: {e}")
    
    def get_area_trampled_ratio(self) -> float:
        """
        Get the ratio of trampled area to plot area.
        
        Returns:
            float: Ratio of trampled area to plot area
        Raises:
            RuntimeError: If calculation fails.
        """
        try:
            return (self.total_area_trampled / self.plot_area)
        except Exception as e:
            raise RuntimeError(f"Failed to calculate trampled area ratio: {e}")
    
    def snow_height_loss_from_ssrd(self, day: int) -> float:
        """
        Calculate snow height loss from surface solar radiation downward (SSRD).
        It first calculates the meltwater mass, then converts it to height loss 
        using snow density and plot area.
        
        Formula: height_loss = meltwater_mass / (RHO_SNOW * plot_area)
        
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
            return meltwater_mass / (RHO_SNOW * self.plot_area)
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
                    grass_mass += flora.total_mass
                elif flora.__class__.__name__ == "Shrub":
                    shrub_mass += flora.total_mass
                elif flora.__class__.__name__ == "Tree":
                    tree_mass += flora.total_mass
                elif flora.__class__.__name__ == "Moss":
                    moss_mass += flora.total_mass
            
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
        Based on maximum herbivore density that could be supported.
        precondition: calculate_fauna_masses() must be called first (for current timestep)

        Returns:
            bool: True if prey mass exceeds maximum density, False otherwise.
        """
        prey_mass = sum(fauna.total_mass for fauna in self.fauna if fauna.__class__.__name__ == "Prey")
        return prey_mass > (self.plot_area * MAX_PREY_DENSITY)
    
    def over_predator_capacity(self) -> bool:
        """
        Check if predator mass exceeds absolute maximum density per km^2.
        Based on maximum predator density that could be supported.
        precondition: calculate_fauna_masses() must be called first (for current timestep)

        Returns:
            bool: True if predator mass exceeds maximum density, False otherwise.
        """
        predator_mass = sum(fauna.total_mass for fauna in self.fauna if fauna.__class__.__name__ == "Predator")
        return predator_mass > (self.plot_area * MAX_PREDATOR_DENSITY)