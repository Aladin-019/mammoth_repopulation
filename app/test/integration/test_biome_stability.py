"""
Integration test to check biome stability based on initial flora ratios.
Tests different combinations of initial conditions (base masses, variation percentages, etc.)
to find which combinations result in stable biome classification.
"""

import unittest
import sys
import os
from itertools import product

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from app.setup.grid_initializer import GridInitializer
from app.models.Plot.Plot import Plot
import app.globals as globals_module


class TestBiomeStability(unittest.TestCase):
    """Test biome stability with different base mass combinations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.biomes = ['southern taiga', 'northern taiga', 'southern tundra', 'northern tundra']
        
        # Store original globals values
        self.original_globals = {
            'S_TAIGA_GRASS_MASS': globals_module.S_TAIGA_GRASS_MASS,
            'S_TAIGA_SHRUB_MASS': globals_module.S_TAIGA_SHRUB_MASS,
            'S_TAIGA_TREE_MASS': globals_module.S_TAIGA_TREE_MASS,
            'S_TAIGA_MOSS_MASS': globals_module.S_TAIGA_MOSS_MASS,
            'N_TAIGA_GRASS_MASS': globals_module.N_TAIGA_GRASS_MASS,
            'N_TAIGA_SHRUB_MASS': globals_module.N_TAIGA_SHRUB_MASS,
            'N_TAIGA_TREE_MASS': globals_module.N_TAIGA_TREE_MASS,
            'N_TAIGA_MOSS_MASS': globals_module.N_TAIGA_MOSS_MASS,
            'S_TUNDRA_GRASS_MASS': globals_module.S_TUNDRA_GRASS_MASS,
            'S_TUNDRA_SHRUB_MASS': globals_module.S_TUNDRA_SHRUB_MASS,
            'S_TUNDRA_TREE_MASS': globals_module.S_TUNDRA_TREE_MASS,
            'S_TUNDRA_MOSS_MASS': globals_module.S_TUNDRA_MOSS_MASS,
            'N_TUNDRA_GRASS_MASS': globals_module.N_TUNDRA_GRASS_MASS,
            'N_TUNDRA_SHRUB_MASS': globals_module.N_TUNDRA_SHRUB_MASS,
            'N_TUNDRA_TREE_MASS': globals_module.N_TUNDRA_TREE_MASS,
            'N_TUNDRA_MOSS_MASS': globals_module.N_TUNDRA_MOSS_MASS,
        }
    
    def _recalculate_totals(self):
        """Helper method to recalculate total masses after individual mass values change."""
        globals_module.S_TAIGA_TOTAL_MASS = (globals_module.S_TAIGA_GRASS_MASS + 
                                              globals_module.S_TAIGA_SHRUB_MASS + 
                                              globals_module.S_TAIGA_TREE_MASS + 
                                              globals_module.S_TAIGA_MOSS_MASS)
        globals_module.N_TAIGA_TOTAL_MASS = (globals_module.N_TAIGA_GRASS_MASS + 
                                              globals_module.N_TAIGA_SHRUB_MASS + 
                                              globals_module.N_TAIGA_TREE_MASS + 
                                              globals_module.N_TAIGA_MOSS_MASS)
        globals_module.S_TUNDRA_TOTAL_MASS = (globals_module.S_TUNDRA_GRASS_MASS + 
                                               globals_module.S_TUNDRA_SHRUB_MASS + 
                                               globals_module.S_TUNDRA_TREE_MASS + 
                                               globals_module.S_TUNDRA_MOSS_MASS)
        globals_module.N_TUNDRA_TOTAL_MASS = (globals_module.N_TUNDRA_GRASS_MASS + 
                                               globals_module.N_TUNDRA_SHRUB_MASS + 
                                               globals_module.N_TUNDRA_TREE_MASS + 
                                               globals_module.N_TUNDRA_MOSS_MASS)
    
    def tearDown(self):
        """Restore original globals values after each test."""
        for key, value in self.original_globals.items():
            setattr(globals_module, key, value)
        self._recalculate_totals()
    
    def set_globals(self, masses):
        """Set globals to specific mass values (used for testing different configurations)."""
        for key, value in masses.items():
            setattr(globals_module, key, value)
        self._recalculate_totals()
    
    def calculate_ideal_ratios(self):
        """Calculate ideal ratios from current globals."""
        return {
            'southern taiga': (
                globals_module.S_TAIGA_GRASS_MASS / globals_module.S_TAIGA_TOTAL_MASS,
                globals_module.S_TAIGA_SHRUB_MASS / globals_module.S_TAIGA_TOTAL_MASS,
                globals_module.S_TAIGA_TREE_MASS / globals_module.S_TAIGA_TOTAL_MASS,
                globals_module.S_TAIGA_MOSS_MASS / globals_module.S_TAIGA_TOTAL_MASS
            ),
            'northern taiga': (
                globals_module.N_TAIGA_GRASS_MASS / globals_module.N_TAIGA_TOTAL_MASS,
                globals_module.N_TAIGA_SHRUB_MASS / globals_module.N_TAIGA_TOTAL_MASS,
                globals_module.N_TAIGA_TREE_MASS / globals_module.N_TAIGA_TOTAL_MASS,
                globals_module.N_TAIGA_MOSS_MASS / globals_module.N_TAIGA_TOTAL_MASS
            ),
            'southern tundra': (
                globals_module.S_TUNDRA_GRASS_MASS / globals_module.S_TUNDRA_TOTAL_MASS,
                globals_module.S_TUNDRA_SHRUB_MASS / globals_module.S_TUNDRA_TOTAL_MASS,
                globals_module.S_TUNDRA_TREE_MASS / globals_module.S_TUNDRA_TOTAL_MASS,
                globals_module.S_TUNDRA_MOSS_MASS / globals_module.S_TUNDRA_TOTAL_MASS
            ),
            'northern tundra': (
                globals_module.N_TUNDRA_GRASS_MASS / globals_module.N_TUNDRA_TOTAL_MASS,
                globals_module.N_TUNDRA_SHRUB_MASS / globals_module.N_TUNDRA_TOTAL_MASS,
                globals_module.N_TUNDRA_TREE_MASS / globals_module.N_TUNDRA_TOTAL_MASS,
                globals_module.N_TUNDRA_MOSS_MASS / globals_module.N_TUNDRA_TOTAL_MASS
            )
        }
    
    def calculate_distance(self, ratios1, ratios2):
        """Calculate Euclidean distance between two ratio tuples."""
        return sum((a - b) ** 2 for a, b in zip(ratios1, ratios2)) ** 0.5
    
    def test_all_combinations(self):
        """Test all combinations of base masses and growth rates for taiga biomes only."""
        print("\n" + "="*80)
        print("Testing All Combinations of Base Masses and Growth Rates - Taiga Only")
        print("="*80)
        
        num_samples = 2  # Just a couple samples as requested
        
        # Define test values separately for each biome (only 4 flora types per biome)
        mass_test_values_southern = {
            'S_TAIGA_GRASS_MASS': [10000.0, 12000.0, 14000.0],  # Current: 12000
            'S_TAIGA_SHRUB_MASS': [18000.0, 20000.0, 22000.0],  # Current: 20000
            'S_TAIGA_TREE_MASS': [8000.0, 10000.0, 12000.0],    # Current: 10000
            'S_TAIGA_MOSS_MASS': [6000.0, 8000.0, 10000.0],     # Current: 8000
        }
        
        mass_test_values_northern = {
            'N_TAIGA_GRASS_MASS': [14000.0, 16000.0, 18000.0],  # Current: 16000
            'N_TAIGA_SHRUB_MASS': [12000.0, 14000.0, 16000.0],  # Current: 14000
            'N_TAIGA_TREE_MASS': [3000.0, 4000.0, 5000.0],      # Current: 4000
            'N_TAIGA_MOSS_MASS': [10000.0, 12000.0, 14000.0],   # Current: 12000
        }
        
        # Define test values for growth rates (kg/day)
        growth_rate_values = [5.0, 10.0, 15.0]  # Current: 10.0
        
        # Store all results
        all_results = []
        
        # Test each biome separately with only its relevant mass values
        for biome_name, mass_test_values in [('southern taiga', mass_test_values_southern),
                                              ('northern taiga', mass_test_values_northern)]:
            print(f"\n{'='*80}")
            print(f"Testing {biome_name.upper()}")
            print(f"{'='*80}")
            
            mass_keys = list(mass_test_values.keys())
            mass_value_lists = [mass_test_values[key] for key in mass_keys]
            total_combinations = len(growth_rate_values) * len(list(product(*mass_value_lists)))
            print(f"Testing {total_combinations} combinations for {biome_name}...\n")
            
            # Loop through growth rates
            for growth_rate in growth_rate_values:
                print(f"\n{'='*60}")
                print(f"Growth Rate: {growth_rate} kg/day")
                print(f"{'='*60}")
                
                # Loop through mass combinations (only 4 values now: 3^4 = 81 combinations)
                for mass_combo in product(*mass_value_lists):
                    # Create description
                    mass_overrides = {key: value for key, value in zip(mass_keys, mass_combo)}
                    # Short description showing key values
                    tree_key = 'S_TAIGA_TREE_MASS' if biome_name == 'southern taiga' else 'N_TAIGA_TREE_MASS'
                    combo_desc = f"GR={growth_rate:4.1f}, {biome_name}, TREE={mass_overrides[tree_key]:.0f}"
                    
                    # Set globals with this mass combination (preserving other biome values)
                    masses = self.original_globals.copy()
                    masses.update(mass_overrides)
                    self.set_globals(masses)
                    
                    # Recalculate ideal ratios with new values
                    ideal_ratios = self.calculate_ideal_ratios()
                    
                    # Test this biome
                    stable_count = 0
                    
                    initializer = GridInitializer(lat_step=0.75, lon_step=0.75)
                    
                    # Patch the growth rate in _create_flora_for_biome
                    original_method = initializer._create_flora_for_biome
                    gr_value = growth_rate  # Capture in closure
                    def patched_create_flora(flora_name, biome, plot):
                        flora = original_method(flora_name, biome, plot)
                        # Override growth rate (without variation for testing)
                        flora.ideal_growth_rate = gr_value
                        return flora
                    initializer._create_flora_for_biome = patched_create_flora
                    
                    for _ in range(num_samples):
                        plot = initializer.create_plot_from_biome(biome_name)
                        actual_ratios = plot.get_flora_mass_composition()
                        
                        # Calculate distances to all biome ideals (including tundra for comparison)
                        distances = {
                            b: self.calculate_distance(actual_ratios, ideal_ratios[b])
                            for b in self.biomes
                        }
                        
                        closest_biome = min(distances.items(), key=lambda x: x[1])[0]
                        
                        if closest_biome == biome_name:
                            stable_count += 1
                    
                    stability_pct = (stable_count / num_samples) * 100
                    
                    result = {
                        'growth_rate': growth_rate,
                        'mass_overrides': mass_overrides,
                        'biome': biome_name,
                        'stability': stability_pct,
                        'description': combo_desc
                    }
                    all_results.append(result)
                    
                    # Print result as we go
                    print(f"  {combo_desc:60s}: Stability={stability_pct:5.1f}%")
        
        # Summary - show best combinations per biome
        print(f"\n{'='*80}")
        print("SUMMARY - Top 10 Most Stable Combinations per Biome")
        print(f"{'='*80}")
        
        for biome_name in ['southern taiga', 'northern taiga']:
            biome_results = [r for r in all_results if r['biome'] == biome_name]
            sorted_biome_results = sorted(biome_results, key=lambda x: x['stability'], reverse=True)
            print(f"\n{biome_name.upper()}:")
            for i, result in enumerate(sorted_biome_results[:10], 1):
                print(f"  {i:2d}. {result['description']:60s}: Stability={result['stability']:5.1f}%")
        
        # Also show worst combinations for comparison
        print(f"\n{'='*80}")
        print("Bottom 5 Least Stable Combinations per Biome")
        print(f"{'='*80}")
        
        for biome_name in ['southern taiga', 'northern taiga']:
            biome_results = [r for r in all_results if r['biome'] == biome_name]
            sorted_biome_results = sorted(biome_results, key=lambda x: x['stability'], reverse=True)
            print(f"\n{biome_name.upper()}:")
            for i, result in enumerate(sorted_biome_results[-5:], 1):
                print(f"  {i}. {result['description']:60s}: Stability={result['stability']:5.1f}%")


    def test_simulation_over_time(self):
        """Test how flora ratios change over time during simulation to identify growth issues."""
        print("\n" + "="*80)
        print("Testing Flora Ratio Changes Over Time During Simulation")
        print("="*80)
        
        # Test both taiga biomes
        for biome_name in ['southern taiga', 'northern taiga']:
            print(f"\n{'='*80}")
            print(f"Testing {biome_name.upper()}")
            print(f"{'='*80}")
            
            # Create a plot
            initializer = GridInitializer(lat_step=0.75, lon_step=0.75)
            plot = initializer.create_plot_from_biome(biome_name)
            
            # Get initial ratios and biome
            initial_ratios = plot.get_flora_mass_composition()
            initial_biome = plot.get_climate().get_biome()
            
            print(f"\nInitial State (Day 0):")
            print(f"  Biome: {initial_biome}")
            print(f"  Ratios - Grass: {initial_ratios[0]:.4f}, Shrub: {initial_ratios[1]:.4f}, Tree: {initial_ratios[2]:.4f}, Moss: {initial_ratios[3]:.4f}")
            
            # Get initial masses
            initial_masses = plot.get_flora_masses()
            print(f"  Masses (kg) - Grass: {initial_masses[0]:.2f}, Shrub: {initial_masses[1]:.2f}, Tree: {initial_masses[2]:.2f}, Moss: {initial_masses[3]:.2f}")
            
            # Calculate ideal ratios for this biome
            ideal_ratios = self.calculate_ideal_ratios()[biome_name]
            initial_distance = self.calculate_distance(initial_ratios, ideal_ratios)
            print(f"  Distance to ideal: {initial_distance:.6f}")
            
            # Simulate forward for 10 days
            print(f"\nSimulating forward 10 days...")
            print(f"{'Day':<6} {'Biome':<20} {'Tree Ratio':<12} {'Distance':<12} {'Grass Mass':<15} {'Tree Mass':<15}")
            print("-" * 80)
            
            for day in range(1, 11):
                # Update flora masses (only on odd days as per the simulation logic)
                if day % 2 == 1:
                    for flora in plot.get_all_flora():
                        # Debug: Print environmental conditions and penalties before update
                        if day == 1:  # Only print on first day to see initial conditions
                            env_conditions = flora._get_current_environmental_conditions(day)
                            penalty = flora._calculate_environmental_penalty(env_conditions)
                            base_gr = flora._calculate_base_growth_rate(penalty)
                            print(f"    {flora.__class__.__name__}: penalty={penalty:.4f}, base_growth_rate={base_gr:.6f}, soil_temp={env_conditions.get('soil_temperature', 'N/A')}")
                        flora.update_flora_mass(day)
                
                # Check biome
                plot.check_and_update_biome()
                current_biome = plot.get_climate().get_biome()
                current_ratios = plot.get_flora_mass_composition()
                current_masses = plot.get_flora_masses()
                current_distance = self.calculate_distance(current_ratios, ideal_ratios)
                
                biome_changed = "CHANGED" if current_biome != initial_biome else ""
                
                print(f"{day:<6} {current_biome:<20} {current_ratios[2]:<12.4f} {current_distance:<12.6f} {current_masses[0]:<15.2f} {current_masses[2]:<15.2f} {biome_changed}")
                
                # Check if biome has changed
                if current_biome != initial_biome:
                    print(f"\n BIOME CHANGED from {initial_biome} to {current_biome} on day {day} !!!")
                    print(f"     Tree ratio: {initial_ratios[2]:.4f} -> {current_ratios[2]:.4f}")
                    print(f"     Distance: {initial_distance:.6f} -> {current_distance:.6f}")
                    break
            
            # Show final state if biome didn't change
            if plot.get_climate().get_biome() == initial_biome:
                final_ratios = plot.get_flora_mass_composition()
                final_distance = self.calculate_distance(final_ratios, ideal_ratios)
                print(f"\n  Final state (Day 10) - Biome still {initial_biome}")
                print(f"     Tree ratio: {initial_ratios[2]:.4f} -> {final_ratios[2]:.4f}")
                print(f"     Distance: {initial_distance:.6f} -> {final_distance:.6f}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
