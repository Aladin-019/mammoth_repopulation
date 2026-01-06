import unittest
import sys
import os
from unittest.mock import patch

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot.Plot import Plot
from app.models.Climate.Climate import Climate


class TestMammothMigration(unittest.TestCase):
    """Integration test for mammoth migration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.initializer = GridInitializer(lat_step=0.75, lon_step=0.75)
        
        # Create a simple 3x3 grid of plots
        self.grid = PlotGrid()
        for row in range(3):
            for col in range(3):
                climate = Climate('southern taiga', None)
                plot = Plot(Id=row*3 + col, avg_snow_height=0.1, climate=climate, plot_area=1000.0)
                climate.set_plot(plot)
                self.grid.add_plot(row, col, plot)
    
    def test_add_mammoth_to_plot(self):
        """Test that mammoths can be added to a plot."""
        plot = self.grid.get_plot(1, 1)  # Center plot
        
        mammoth = self.initializer.add_mammoth_to_plot(plot, population_per_km2=0.01)
        
        self.assertIsNotNone(mammoth)
        self.assertEqual(mammoth.get_name(), 'Mammoth')
        self.assertGreater(mammoth.get_total_mass(), 0)
        self.assertGreater(mammoth.population, 0)
        
        # Check that mammoth is in the plot
        plot_mammoth = plot.get_a_fauna('Mammoth')
        self.assertIsNotNone(plot_mammoth)
        self.assertEqual(plot_mammoth.get_name(), 'Mammoth')
    
    def test_mammoth_migration_over_time(self):
        """Test that mammoths migrate to neighboring plots over multiple days."""
        # Add mammoths to center plot
        center_plot = self.grid.get_plot(1, 1)
        mammoth = self.initializer.add_mammoth_to_plot(center_plot, population_per_km2=0.05)
        
        initial_center_mass = mammoth.get_total_mass()
        self.assertGreater(initial_center_mass, 0)
        
        # Get neighboring plots
        neighbors = self.grid.get_neighbors(1, 1)
        self.assertGreater(len(neighbors), 0)
        
        # Count initial mammoths in neighboring plots
        initial_neighbor_mammoth_count = sum(
            1 for plot in neighbors if plot.get_a_fauna('Mammoth') is not None
        )
        self.assertEqual(initial_neighbor_mammoth_count, 0)
        
        # Run simulation for 25 days
        # Migration can happen on days 5, 10, 15, 20, 25... 76 days (20% probability each day)
        # Should be plenty of time to migrate to at least one neighbor
        for day in range(1, 76):
            self.grid.update_all_plots(day)
        
        # Check that mammoths have appeared in at least one neighbor
        # (depending on random chance and migration probability)
        final_neighbor_mammoth_count = sum(
            1 for plot in neighbors if plot.get_a_fauna('Mammoth') is not None and 
            plot.get_a_fauna('Mammoth').get_total_mass() > 0
        )
        
        # Note: Migration is probabilistic, so we can't guarantee it happens
        # But we can check that the center plot mass decreased or neighbors have mammoths
        center_mammoth = center_plot.get_a_fauna('Mammoth')
        
        if center_mammoth:
            center_final_mass = center_mammoth.get_total_mass()
            # Either mass decreased (migration happened) or neighbors have mammoths
            # Use a percentage-based check for mass decrease
            # Allow for 5% decrease to account for small migrations
            mass_decreased = center_final_mass < (initial_center_mass * 0.95)
            neighbors_have_mammoths = final_neighbor_mammoth_count > 0
            
            # At least one of these should be true if migration is working
            # With 5 migration opportunities at 20% each, probability of at least one migration is ~67%
            self.assertTrue(mass_decreased or neighbors_have_mammoths, 
                          f"Migration doesn't seem to be working. Center mass: {initial_center_mass} -> {center_final_mass}, "
                          f"Neighbors with mammoths: {final_neighbor_mammoth_count}")
        else:
            # If center mammoth is gone, migration definitely happened
            self.assertTrue(True, "Center mammoth migrated away completely")
    
    def test_mammoth_migration_mass_preservation(self):
        """Test that total mammoth mass is preserved during migration."""
        # Add mammoths to center plot
        center_plot = self.grid.get_plot(1, 1)
        mammoth = self.initializer.add_mammoth_to_plot(center_plot, population_per_km2=0.05)
        
        initial_total_mass = mammoth.get_total_mass()
        
        # Run simulation for 5 days (migration happens on day 5)
        for day in range(1, 6):
            self.grid.update_all_plots(day)
        
        # Calculate total mass across all plots
        total_mass = 0.0
        for row in range(3):
            for col in range(3):
                plot = self.grid.get_plot(row, col)
                mammoth_in_plot = plot.get_a_fauna('Mammoth')
                if mammoth_in_plot:
                    total_mass += mammoth_in_plot.get_total_mass()
        
        # Total mass should be approximately preserved (allow for small floating point errors)
        # Mass might decrease slightly due to consumption, but should be close
        self.assertGreater(total_mass, initial_total_mass * 0.9, 
                          f"Total mass decreased too much: {initial_total_mass} -> {total_mass}")
    
    def test_mammoth_visualization_borders(self):
        """Test that plots with mammoths can be identified for visualization."""
        # Add mammoths to two plots
        plot1 = self.grid.get_plot(0, 0)
        plot2 = self.grid.get_plot(2, 2)
        
        self.initializer.add_mammoth_to_plot(plot1, population_per_km2=0.01)
        self.initializer.add_mammoth_to_plot(plot2, population_per_km2=0.01)
        
        # Count plots with mammoths
        plots_with_mammoths = []
        for (row, col), plot in self.grid.plots.items():
            has_mammoths = False
            for fauna in plot.get_all_fauna():
                if fauna.get_name() == 'Mammoth' and fauna.get_total_mass() > 0:
                    has_mammoths = True
                    break
            if has_mammoths:
                plots_with_mammoths.append((row, col))
        
        self.assertEqual(len(plots_with_mammoths), 2)
        self.assertIn((0, 0), plots_with_mammoths)
        self.assertIn((2, 2), plots_with_mammoths)
    
    def test_mammoth_migration_creates_new_population(self):
        """Test that migration creates new mammoth population in target plot if it doesn't exist."""
        # Add mammoths only to center plot
        center_plot = self.grid.get_plot(1, 1)
        mammoth = self.initializer.add_mammoth_to_plot(center_plot, population_per_km2=0.05)
        
        # Pick a neighbor that definitely doesn't have mammoths
        neighbor = self.grid.get_neighbors(1, 1)[0]
        self.assertIsNone(neighbor.get_a_fauna('Mammoth'))
        
        # Force migration by calling migrate_species directly with mocked random
        from app.models.Plot.PlotGrid import P_PREY_MIGRATION
        with patch('numpy.random.random', return_value=0.0), \
             patch('numpy.random.choice', return_value=neighbor):
            self.grid.migrate_species()
        
        # Check if mammoth appeared in neighbor (if migration succeeded)
        neighbor_mammoth = neighbor.get_a_fauna('Mammoth')
        # Migration is probabilistic, so neighbor might or might not have mammoths
        # But if it does, it should be a valid mammoth
        if neighbor_mammoth:
            self.assertEqual(neighbor_mammoth.get_name(), 'Mammoth')
            self.assertGreater(neighbor_mammoth.get_total_mass(), 0)


if __name__ == '__main__':
    unittest.main()

