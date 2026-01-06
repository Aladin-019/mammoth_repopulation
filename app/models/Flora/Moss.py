from .Flora import Flora
# FAUNA TEMPORARILY DISABLED - Focus on flora only
# from ..Fauna import Fauna
from typing import List, Tuple
from app.interfaces.flora_plot_info import FloraPlotInformation


class Moss(Flora):
    """
    Represents a moss species.
    Mosses thrive in cold and wetter conditions such as Tundra.
    They are resilient and can grow in shaded areas, making them suitable for undergrowth.
    They are affected by canopy cover, which reduces UV exposure.
    """

    def __init__(self, name: str, description: str, total_mass: float, population: int,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List,  # consumers: List[Fauna] when fauna enabled 
                 root_depth: int, plot: FloraPlotInformation):
        
        # Moss uses total mass directly, so we pass a dummy avg_mass to satisfy the base class
        dummy_avg_mass = 1.0
        
        super().__init__(name, description, dummy_avg_mass, population, ideal_growth_rate, 
                        ideal_temp_range, ideal_uv_range, ideal_hydration_range,
                        ideal_soil_temp_range, consumers, root_depth, plot)
        
        self.total_mass = float(total_mass)

    def update_flora_mass(self, day: int) -> None:
        """
        Update the mass of the Moss.
        Mosses do well in cold and wetter conditions such as Tundra.
        UV is reduced by tree canopy cover on the plot.
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
            
            self.capacity_penalty()
        except Exception as e:
            raise RuntimeError(f"Error updating moss mass: {e}")
    
    def capacity_penalty(self) -> None:
        """
        Apply a penalty to moss mass if the plot is over moss capacity.
        Moss grows in patches and has the lowest density limits.
        
        Precondition: calculate_flora_masses() must be called first (for current timestep)
        """
        self._validate_not_none(self.plot, "plot")
        
        if self.plot.over_moss_capacity():
            self.total_mass *= 0.9    # Reduce mass by 10% if over moss capacity
    
