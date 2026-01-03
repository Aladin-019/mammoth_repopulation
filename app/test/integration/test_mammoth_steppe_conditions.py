"""
Integration test to debug mammoth steppe conditions.
Simplified test that tracks conditions over 20 days starting with normal northern taiga.
"""

import unittest
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from app.setup.grid_initializer import GridInitializer
from app.models.Plot.Plot import Plot
from app.models.Climate.Climate import Climate


class TestMammothSteppeConditions(unittest.TestCase):
    """Test mammoth steppe conditions day by day."""
    
    def test_steppe_conditions_over_time(self):
        """Track steppe conditions over 20 days starting with normal northern taiga."""
        print("\n" + "="*100)
        print("Mammoth Steppe Conditions Over 20 Days (Starting with Northern Taiga + Mammoths)")
        print("="*100)
        
        # Use GridInitializer to create plot with standard northern taiga flora
        initializer = GridInitializer(lat_step=0.55, lon_step=0.55)
        plot = initializer.create_plot_from_biome('northern taiga')
        climate = plot.climate
        
        # Add mammoths
        initializer.add_mammoth_to_plot(plot, population_per_km2=0.1)
        
        for day in range(1, 101):
            ###### SIMULATION UPDATE PATTERN from PlotGrid.update_all_plots ######
            # Update snow height
            plot.update_avg_snow_height(day)

            # Update flora on odd days (day % 2 == 1)
            if day % 2 == 1:
                for flora in plot.get_all_flora():
                    flora.update_flora_mass(day)
            
            # Update fauna (prey/mammoths) on even days (day % 2 == 0)
            if day % 2 == 0:
                for fauna in plot.get_all_fauna():
                    if hasattr(fauna, 'update_prey_mass'):
                        fauna.update_prey_mass(day)
            
            # Clean up extinct species
            plot.remove_extinct_species()
            
            # Check and update biome on odd days (when flora has updated)
            if day % 2 == 1:
                plot.check_and_update_biome()

        
            ###### CHECK STEPPE CONDITIONS ######

            # Get current state
            ratios = plot.get_flora_mass_composition()
            grass_ratio, shrub_ratio, tree_ratio, moss_ratio = ratios

            # Ideal steppe ratios (thresholds)
            steppe_grass_min = 0.55
            steppe_tree_max = 0.10
            steppe_shrub_max = 0.15
            steppe_moss_max = 0.20

            # Count mammoths (sum population from all mammoth Prey objects)
            mammoth_count = sum(f.population for f in plot.get_all_fauna() if f.get_name() == 'Mammoth' and f.get_total_mass() > 0)
            # Check permafrost and steppe conditions
            is_permafrost = climate.is_permafrost()
            is_steppe = climate.is_steppe()
            
            # Get climate data from flora's stored environmental conditions
            all_flora = plot.get_all_flora()
            if all_flora and all_flora[0].last_environmental_conditions:
                env_conditions = all_flora[0].last_environmental_conditions
                temp = env_conditions['temperature']
                uv = env_conditions['uv']
                hydration = env_conditions['hydration']
                soil_temp = env_conditions.get('soil_temperature', 0.0)
            else:
                # Fallback if no stored conditions available yet
                temp = 0.0
                uv = 0.0
                hydration = 0.0
                soil_temp = 0.0
            
            print(f"Day: {day}")
            print(f"Temperature: {temp:.2f}°C")
            print(f"UV: {uv:.2f}")
            print(f"Hydration: {hydration:.4f}")
            print(f"Soil Temp: {soil_temp:.2f}°C")
            print(f"Grass: {grass_ratio}, Min grass: {steppe_grass_min}")
            print(f"Tree: {tree_ratio}, Max tree: {steppe_tree_max}")
            print(f"Shrub: {shrub_ratio}, Max shrub: {steppe_shrub_max}")
            print(f"Moss: {moss_ratio}, Max moss: {steppe_moss_max}")
            print(f"Mammoths: {mammoth_count}")
            print(f"Frozen Days: {climate.consecutive_frozen_soil_days}")
            print(f"Is Permafrost: {is_permafrost}")
            print(f"Is Steppe: {is_steppe}")

if __name__ == '__main__':
    unittest.main()
