from .Flora import Flora
# FAUNA TEMPORARILY DISABLED - Focus on flora only
# from ..Fauna import Fauna
from typing import List, Tuple
from app.interfaces.flora_plot_info import FloraPlotInformation


class Tree(Flora):
    """
    Represents a tree species of Flora.
    Trees provide canopy cover shade which reduces UV exposure and affects the mass of other
    ground flora. Trees are resistent to trampling from large herbivores.
    """

    def __init__(self, name: str, description: str, avg_mass: float, population: int,
                 ideal_growth_rate: float, ideal_temp_range: Tuple[float, float],
                 ideal_uv_range: Tuple[float, float], ideal_hydration_range: Tuple[float, float],
                 ideal_soil_temp_range: Tuple[float, float], consumers: List,  # consumers: List[Fauna] when fauna enabled 
                 root_depth: int, plot: FloraPlotInformation, single_tree_canopy_cover: float = 10.0, coniferous: bool = True):
               
        super().__init__(name, description, avg_mass, population, ideal_growth_rate, 
                        ideal_temp_range, ideal_uv_range, ideal_hydration_range,
                        ideal_soil_temp_range, consumers, root_depth, plot)
        
        self._validate_instance(single_tree_canopy_cover, float, "single_tree_canopy_cover")
        self._validate_positive_number(single_tree_canopy_cover, "single_tree_canopy_cover")
        self._validate_instance(coniferous, bool, "coniferous")
        
        self.single_tree_canopy_cover = single_tree_canopy_cover  # Single tree canopy cover in km^2 (float)
        self.coniferous = coniferous  # Tree is coniferous or deciduous (bool)

    def update_flora_mass(self, day: int) -> None:
        """
        Update the mass of the Tree.
        """
        self._validate_instance(day, int, "day")
        self._validate_positive_number(day, "day")
        
        super().update_flora_mass(day)

    def get_Tree_canopy_cover(self) -> float:
        """Get the total canopy cover from all trees of this species in km^2"""
        return self.single_tree_canopy_cover * self.population
    
    def capacity_penalty(self) -> None:
        """
        Apply a penalty to tree mass if the plot is over tree capacity.
        Trees need significant space and are sensitive to overcrowding.
        
        Precondition: calculate_flora_masses() must be called first (for current timestep)
        """
        self._validate_not_none(self.plot, "plot")
        
        if self.plot.over_tree_capacity():
            self.total_mass *= 0.9    # Reduce mass by 10% if over tree capacity
    
