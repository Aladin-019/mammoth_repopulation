from .Flora import Flora
from ..Fauna import Fauna
from typing import List, Tuple
from app.interfaces.flora_plot_info import FloraPlotInformation


class Shrub(Flora):
    """
    Represents a shrub species.
    Shrubs are destroyed by trampling of mammoths only - smaller prey like deer cannot trample shrubs.
    They are affected by canopy cover, which reduces UV exposure.
    """
    
    # amount of shrub area trampled by mammoths (probability they will trample if encountered)
    # Only mammoths are large enough to trample shrubs - smaller prey cannot
    STOMPING_RATE = 0.85

    def __init__(self, name: str, description: str, avg_mass: float, population: int,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List[Fauna], 
                 root_depth: int, plot: FloraPlotInformation, shrub_area_m2: float = 1.0):
                
        super().__init__(name, description, avg_mass, population, ideal_growth_rate, 
                        ideal_temp_range, ideal_uv_range, ideal_hydration_range,
                        ideal_soil_temp_range, consumers, root_depth, plot)
        
        self._validate_positive_number(shrub_area_m2, "shrub_area_m2")
        self._validate_instance(shrub_area_m2, float, "shrub_area_m2")
        self.shrub_area = shrub_area_m2 / 1_000_000.0   # to km^2

    def update_flora_mass(self, day: int) -> None:
        """
        Update the mass of the shrub.
        Shrubs can be stomped out by mammoths only and has sunlight reduced
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
        Apply reduction in shrub mass due to trampling by mammoths only.
        Only mammoths are large enough to trample shrubs - smaller prey like deer cannot.
        The trampling effect is proportional to how much of the plot is trampled by mammoths.
        """
        self._validate_not_none(self.plot, "plot")
        
        # Check if there are any mammoths on the plot - only mammoths can trample shrubs
        has_mammoths = any(fauna.get_name().lower() == 'mammoth' and fauna.get_total_mass() > 0 
                          for fauna in self.plot.get_all_fauna())
        
        if not has_mammoths:
            return  # No mammoths, no shrub trampling
        
        # Calculate only mammoth trampling area and ratio
        mammoth_trampled_area = 0.0
        for fauna in self.plot.get_all_fauna():
            if fauna.get_name().lower() == 'mammoth' and fauna.get_total_mass() > 0:
                individual_trampled = fauna.get_avg_feet_area() * fauna.get_avg_steps_taken()
                mammoth_trampled_area += individual_trampled * fauna.get_population()
        
        # Cap at plot area and calculate ratio
        mammoth_trampled_area = min(mammoth_trampled_area, self.plot.get_plot_area())
        mammoth_trampled_ratio = mammoth_trampled_area / self.plot.get_plot_area()
        
        trampling_damage = self.STOMPING_RATE * mammoth_trampled_ratio
        
        if trampling_damage > 0:
            # Reduce mass by trampling damage
            mass_reduction = 1.0 - trampling_damage
            self.total_mass *= max(0.0, mass_reduction)
            
            # Recalculate population after mass reduction
            if self.avg_mass > 0:
                new_population = int(self.total_mass / self.avg_mass)
                self.population = max(0, new_population)
    
    def capacity_penalty(self) -> None:
        """
        Apply a penalty to shrub mass if the plot is over shrub capacity.
        Shrubs need more space than grass but can still grow densely.
        
        Precondition: calculate_flora_masses() must be called first (for current timestep)
        """
        self._validate_not_none(self.plot, "plot")
        
        if self.plot.over_shrub_capacity():
            self.total_mass *= 0.9    # Reduce mass by 10% if over shrub capacity
    
