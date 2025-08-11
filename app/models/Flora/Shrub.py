from .Flora import Flora
from ..Fauna import Fauna
from typing import List, Tuple
from app.interfaces.flora_plot_info import FloraPlotInformation


class Shrub(Flora):
    """
    Represents a shrub species.
    Shrubs are destroyed by trampling of large fauna.
    They are affected by canopy cover, which reduces UV exposure.
    """
    
    # amount of shrub area trampled by large herbivores
    STOMPING_RATE = 0.5

    def __init__(self, name: str, description: str, total_mass: float, population: int,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List[Fauna], 
                 root_depth: int, plot: FloraPlotInformation, shrub_area: float = 1.0):
                
        super().__init__(name, description, total_mass, population, ideal_growth_rate, 
                        ideal_temp_range, ideal_uv_range, ideal_hydration_range,
                        ideal_soil_temp_range, consumers, root_depth, plot)
        
        self._validate_positive_number(shrub_area, "shrub_area")
        self._validate_instance(shrub_area, float, "shrub_area")
        self.shrub_area = shrub_area

    def update_flora_mass(self, day: int) -> None:
        """
        Update the mass of the shrub.
        Shrubs can be stomped out by large herbivores and has sunlight reduced
        by tree canopy cover.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        try:
            environmental_conditions = self._get_current_environmental_conditions(day)

            shaded_environmental_conditions = self._apply_canopy_shading(environmental_conditions)
            
            environmental_penalty = self._calculate_environmental_penalty(shaded_environmental_conditions)
            
            base_growth_rate = self._calculate_base_growth_rate(environmental_penalty)
            consumption_rate = self.total_consumption_rate()
            
            self._update_mass_from_growth_and_consumption(base_growth_rate, consumption_rate)
            
            self._apply_trampling_reduction()
        except Exception as e:
            raise RuntimeError(f"Error updating shrub mass: {e}")

    def _apply_trampling_reduction(self) -> None:
        """
        Apply reduction in shrub mass due to trampling by prey.
        Calculate the area of shrubs stomped out based on trampled area.
        """
        self._validate_not_none(self.plot, "plot")
        
        total_area_trampled = self.plot.get_area_trampled_ratio()
        
        initial_shrub_area = self.population * self.shrub_area
        
        stomping_rate = self.STOMPING_RATE * total_area_trampled
        area_stomped_out = initial_shrub_area * stomping_rate
        
        updated_shrub_area = max(0, initial_shrub_area - area_stomped_out)
        
        if initial_shrub_area > 0:
            area_reduction_ratio = updated_shrub_area / initial_shrub_area
            self.total_mass *= area_reduction_ratio
            
            self.population = int(updated_shrub_area / self.shrub_area)
    
    def capacity_penalty(self) -> None:
        """
        Apply a penalty to shrub mass if the plot is over shrub capacity.
        Shrubs need more space than grass but can still grow densely.
        
        Precondition: calculate_flora_masses() must be called first (for current timestep)
        """
        self._validate_not_none(self.plot, "plot")
        
        if self.plot.over_shrub_capacity():
            self.total_mass *= 0.9    # Reduce mass by 10% if over shrub capacity
    
