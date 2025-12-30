import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the path to handle imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

from app.models.Plot.PlotGrid import PlotGrid, P_PREY_MIGRATION, PREY_MIGRATION_RATIO
from app.models.Plot.Plot import Plot
from app.models.Climate.Climate import Climate
from app.models.Fauna.Prey import Prey
from app.models.Flora.Grass import Grass
import numpy as np


class TestPlotGridMigration(unittest.TestCase):
    """Test migration functionality in PlotGrid."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.grid = PlotGrid()
        self.climate = Climate('southern taiga', None)
        
        # Create real plots for testing
        self.plot1 = Plot(Id=1, avg_snow_height=0.1, climate=self.climate, plot_area=1000.0)
        self.plot2 = Plot(Id=2, avg_snow_height=0.1, climate=self.climate, plot_area=1000.0)
        self.climate.set_plot(self.plot1)
        
        # Add plots to grid
        self.grid.add_plot(0, 0, self.plot1)
        self.grid.add_plot(0, 1, self.plot2)
    
    def test_migrate_species_has_neighbors(self):
        """Test that migrate_species works when plots have neighbors."""
        # Create a mammoth in plot1
        mammoth = Prey(
            name='Mammoth',
            description='Test mammoth',
            population=10,
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,  # m^2 converted to km^2
            plot=self.plot1,
            predators=[],
            consumable_flora=[]
        )
        self.plot1.add_fauna(mammoth)
        
        initial_mass = mammoth.get_total_mass()
        self.assertGreater(initial_mass, 0)
        
        # Mock random to always migrate
        with patch('numpy.random.random', return_value=0.0), \
             patch('numpy.random.choice', return_value=self.plot2):
            self.grid.migrate_species()
        
        # Check that mass was reduced in plot1
        # (Migration should move some mass to plot2)
        plot1_mammoth = self.plot1.get_a_fauna('Mammoth')
        if plot1_mammoth:
            self.assertLess(plot1_mammoth.get_total_mass(), initial_mass)
    
    def test_migrate_species_no_neighbors(self):
        """Test that migration doesn't happen when there are no neighbors."""
        # Create isolated plot (no neighbors)
        isolated_plot = Plot(Id=3, avg_snow_height=0.1, climate=self.climate, plot_area=1000.0)
        self.grid.add_plot(10, 10, isolated_plot)
        
        mammoth = Prey(
            name='Mammoth',
            description='Test mammoth',
            population=10,
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=isolated_plot,
            predators=[],
            consumable_flora=[]
        )
        isolated_plot.add_fauna(mammoth)
        
        initial_mass = mammoth.get_total_mass()
        
        self.grid.migrate_species()
        
        # Mass should be unchanged (no neighbors to migrate to)
        isolated_mammoth = isolated_plot.get_a_fauna('Mammoth')
        self.assertEqual(isolated_mammoth.get_total_mass(), initial_mass)
    
    def test_migrate_species_zero_mass(self):
        """Test that migration doesn't happen for fauna with zero mass."""
        mammoth = Prey(
            name='Mammoth',
            description='Test mammoth',
            population=0,  # Zero population = zero mass
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot1,
            predators=[],
            consumable_flora=[]
        )
        mammoth.set_total_mass(0.0)
        self.plot1.add_fauna(mammoth)
        
        initial_mass = mammoth.get_total_mass()
        self.assertEqual(initial_mass, 0.0)
        
        # Should not crash and mass should remain 0
        self.grid.migrate_species()
        plot1_mammoth = self.plot1.get_a_fauna('Mammoth')
        self.assertEqual(plot1_mammoth.get_total_mass(), 0.0)
    
    def test_migrate_species_probability(self):
        """Test that migration respects probability threshold."""
        mammoth = Prey(
            name='Mammoth',
            description='Test mammoth',
            population=10,
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot1,
            predators=[],
            consumable_flora=[]
        )
        self.plot1.add_fauna(mammoth)
        
        initial_mass = mammoth.get_total_mass()
        
        # Mock random to always exceed migration probability (no migration)
        with patch('numpy.random.random', return_value=1.0):
            self.grid.migrate_species()
        
        # Mass should be unchanged (migration probability not met)
        plot1_mammoth = self.plot1.get_a_fauna('Mammoth')
        self.assertEqual(plot1_mammoth.get_total_mass(), initial_mass)
    
    def test_migrate_species_target_has_existing_fauna(self):
        """Test migration when target plot already has fauna of same type."""
        # Create mammoths in both plots
        # Use smaller masses to ensure plot2 is not over capacity (max = 1000.0 * 10.0 = 10000 kg)
        # plot1: 6000 kg, plot2: 3000 kg (both under capacity)
        mammoth1 = Prey(
            name='Mammoth',
            description='Test mammoth 1',
            population=10,
            avg_mass=600.0,  # Total mass = 6000 kg
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot1,
            predators=[],
            consumable_flora=[]
        )
        mammoth2 = Prey(
            name='Mammoth',
            description='Test mammoth 2',
            population=5,
            avg_mass=600.0,  # Total mass = 3000 kg (under capacity limit of 10000 kg)
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot2,
            predators=[],
            consumable_flora=[]
        )
        self.plot1.add_fauna(mammoth1)
        self.plot2.add_fauna(mammoth2)
        
        plot1_initial_mass = mammoth1.get_total_mass()
        plot2_initial_mass = mammoth2.get_total_mass()
        total_initial_mass = plot1_initial_mass + plot2_initial_mass
        
        # Mock random to always migrate
        with patch('numpy.random.random', return_value=0.0), \
             patch('numpy.random.choice', return_value=self.plot2):
            self.grid.migrate_species()
        
        # Total mass should be preserved (just moved between plots)
        plot1_mammoth = self.plot1.get_a_fauna('Mammoth')
        plot2_mammoth = self.plot2.get_a_fauna('Mammoth')
        total_final_mass = plot1_mammoth.get_total_mass() + plot2_mammoth.get_total_mass()
        
        # Allow for small floating point differences
        self.assertAlmostEqual(total_initial_mass, total_final_mass, places=5)
        # Mass should have moved from plot1 to plot2
        self.assertLess(plot1_mammoth.get_total_mass(), plot1_initial_mass)
        self.assertGreater(plot2_mammoth.get_total_mass(), plot2_initial_mass)
    
    def test_migrate_species_over_capacity(self):
        """Test that migration doesn't happen when target is over capacity."""
        # Create mammoth in plot1
        mammoth = Prey(
            name='Mammoth',
            description='Test mammoth',
            population=10,
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot1,
            predators=[],
            consumable_flora=[]
        )
        self.plot1.add_fauna(mammoth)
        
        # Make plot2 over capacity
        # Create a very large population in plot2
        large_mammoth = Prey(
            name='Mammoth',
            description='Large test mammoth',
            population=10000,  # Very large population
            avg_mass=6000.0,
            ideal_temp_range=(-80.0, 30.0),
            min_food_per_day=200.0,
            ideal_growth_rate=2.0,
            feeding_rate=0.8,
            avg_steps_taken=80000.0,
            avg_foot_area=0.00012,
            plot=self.plot2,
            predators=[],
            consumable_flora=[]
        )
        self.plot2.add_fauna(large_mammoth)
        
        initial_mass = mammoth.get_total_mass()
        
        # Mock random to always migrate
        with patch('numpy.random.random', return_value=0.0), \
             patch('numpy.random.choice', return_value=self.plot2):
            self.grid.migrate_species()
        
        # Mass should be unchanged (target plot is over capacity)
        plot1_mammoth = self.plot1.get_a_fauna('Mammoth')
        self.assertEqual(plot1_mammoth.get_total_mass(), initial_mass)


if __name__ == '__main__':
    unittest.main()

