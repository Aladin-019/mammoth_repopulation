import unittest
from unittest.mock import Mock, patch
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot.Plot import Plot
from app.models.Climate import Climate

class TestPlotGrid(unittest.TestCase):
    def setUp(self):
        self.grid = PlotGrid()
        self.climate = Climate('northern taiga', None)
        self.real_plot1 = Plot(Id=1, avg_snow_height=0.1, climate=self.climate, plot_area=1.0)
        self.real_plot2 = Plot(Id=2, avg_snow_height=0.2, climate=self.climate, plot_area=2.0)
        self.plot1 = Mock(spec=Plot)
        self.plot2 = Mock(spec=Plot)
        # Only pre-populate grid for migration tests


    def test_add_and_get_plot(self):
        self.grid.add_plot(0, 0, self.plot1)
        self.grid.add_plot(1, 2, self.plot2)
        self.assertIs(self.grid.get_plot(0, 0), self.plot1)
        self.assertIs(self.grid.get_plot(1, 2), self.plot2)
        self.assertIsNone(self.grid.get_plot(5, 5))

    def test_add_plot_invalid_plot(self):
        with self.assertRaises(TypeError):
            self.grid.add_plot(0, 0, "NotAPlotInstance")

    def test_grid_boundaries(self):
        self.grid.add_plot(3, 4, self.plot1)
        self.grid.add_plot(-2, 10, self.plot2)
        self.assertEqual(self.grid.min_row, -2)
        self.assertEqual(self.grid.max_row, 3)
        self.assertEqual(self.grid.min_col, 4)
        self.assertEqual(self.grid.max_col, 10)

    def test_overwrite_plot(self):
        self.grid.add_plot(0, 0, self.plot1)
        self.grid.add_plot(0, 0, self.plot2)
        self.assertIs(self.grid.get_plot(0, 0), self.plot2)

    def test_empty_grid(self):
        # Use a fresh grid
        empty_grid = PlotGrid()
        self.assertIsNone(empty_grid.get_plot(0, 0))
        self.assertEqual(empty_grid.plots, {})

    def test_get_all_plots(self):
        grid = PlotGrid()
        grid.add_plot(0, 0, self.plot1)
        grid.add_plot(1, 2, self.plot2)
        all_plots = grid.get_all_plots()
        self.assertEqual(len(all_plots), 2)
        self.assertIn(self.plot1, all_plots)
        self.assertIn(self.plot2, all_plots)

        # Test with empty grid
        empty_grid = PlotGrid()
        self.assertEqual(empty_grid.get_all_plots(), [])

    def test_get_plot_coordinates(self):
        grid = PlotGrid()
        grid.add_plot(0, 0, self.plot1)
        grid.add_plot(1, 2, self.plot2)
        coords = list(grid.plots.keys())
        self.assertIn((0, 0), coords)
        self.assertIn((1, 2), coords)
        self.assertEqual(len(coords), 2)

        # Test after overwriting a plot
        grid.add_plot(0, 0, self.plot2)
        coords = list(grid.plots.keys())
        self.assertIn((0, 0), coords)
        self.assertIn((1, 2), coords)
        self.assertEqual(len(coords), 2)

        # Test with empty grid
        empty_grid = PlotGrid()
        self.assertEqual(list(empty_grid.plots.keys()), [])

    def test_grid_dimensions(self):
        # Empty grid 
        empty_grid = PlotGrid()
        self.assertEqual(empty_grid.min_row, float('inf'))
        self.assertEqual(empty_grid.max_row, float('-inf'))
        self.assertEqual(empty_grid.min_col, float('inf'))
        self.assertEqual(empty_grid.max_col, float('-inf'))

        # Add one plot
        self.grid.add_plot(2, 3, self.plot1)
        self.assertEqual(self.grid.min_row, 2)
        self.assertEqual(self.grid.max_row, 2)
        self.assertEqual(self.grid.min_col, 3)
        self.assertEqual(self.grid.max_col, 3)

        # Add another plot
        self.grid.add_plot(-1, 5, self.plot2)
        self.assertEqual(self.grid.min_row, -1)
        self.assertEqual(self.grid.max_row, 2)
        self.assertEqual(self.grid.min_col, 3)
        self.assertEqual(self.grid.max_col, 5)

        # Overwrite plot at (2, 3) should not change dimensions
        self.grid.add_plot(2, 3, self.plot2)
        self.assertEqual(self.grid.min_row, -1)
        self.assertEqual(self.grid.max_row, 2)
        self.assertEqual(self.grid.min_col, 3)
        self.assertEqual(self.grid.max_col, 5)

    def test_get_neighbors(self):
        grid = PlotGrid()
        plots = {}
        for r in range(0, 3):
            for c in range(0, 3):
                p = Plot(Id=10*r+c, avg_snow_height=0.1, climate=self.climate, plot_area=1.0)
                grid.add_plot(r, c, p)
                plots[(r, c)] = p

        # Center plot (1,1) should have 8 neighbors
        neighbors = grid.get_neighbors(1, 1)
        self.assertEqual(len(neighbors), 8)
        for coord in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
            self.assertIn(plots[coord], neighbors)

        # Corner plot (0,0) should have 3 neighbors
        neighbors = grid.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)
        for coord in [(0,1),(1,0),(1,1)]:
            self.assertIn(plots[coord], neighbors)

        # Edge plot (0,1) should have 5 neighbors
        neighbors = grid.get_neighbors(0, 1)
        self.assertEqual(len(neighbors), 5)
        for coord in [(0,0),(0,2),(1,0),(1,1),(1,2)]:
            self.assertIn(plots[coord], neighbors)

        # Plot with no neighbors
        empty_grid = PlotGrid()
        p = Plot(Id=99, avg_snow_height=0.1, climate=self.climate, plot_area=1.0)
        empty_grid.add_plot(5, 5, p)
        neighbors = empty_grid.get_neighbors(5, 5)
        self.assertEqual(neighbors, [])

    def test_migrate_fauna_new_to_target_plot(self):
        """
        Test that migrating fauna transfers mass and adds new fauna to target plot 
        with no existing fauna of that type.
        """
        # Setup migration grid
        self.grid.plots = {(0, 0): self.plot1, (0, 1): self.plot2}
        self.grid.get_neighbors = Mock(return_value=[self.plot2])
        fauna = Mock()
        fauna.name = "mammoth"
        fauna.get_total_mass.return_value = 100.0
        fauna.set_total_mass = Mock()
        from app.models.Fauna.Fauna import Fauna
        fauna.__class__ = Fauna
        self.plot2.get_a_fauna.return_value = None  # No existing fauna of this type
        self.plot2.add_fauna = Mock()
        self.plot2.over_prey_capacity = Mock(return_value=False)
        self.plot1.get_all_fauna.return_value = [fauna]
        self.plot2.get_all_fauna.return_value = []
        # Patch Fauna.from_existing_with_mass to return a new mock fauna
        from app.models.Fauna.Fauna import Fauna
        new_fauna = Mock()
        with patch.object(Fauna, 'from_existing_with_mass', side_effect=lambda *args, **kwargs: new_fauna):
            self.grid._migrate_fauna(fauna, self.plot2, 'over_prey_capacity', 0.5)
        self.plot2.add_fauna.assert_called_with(new_fauna)  # fauna added to target plot with migration mass
        fauna.set_total_mass.assert_called()  # source fauna mass changed

    def test_migrate_fauna_existing_on_target_plot(self):
        """
        Test that migrating fauna transfers mass to an existing fauna on the target plot.
        """
        self.grid.plots = {(0, 0): self.plot1, (0, 1): self.plot2}
        self.grid.get_neighbors = Mock(return_value=[self.plot2])
        fauna = Mock()
        fauna.name = "mammoth"
        fauna.get_total_mass.return_value = 100.0
        fauna.set_total_mass = Mock()
        fauna.__class__.__name__ = "Fauna"
        target_fauna = Mock()
        target_fauna.get_total_mass.return_value = 50.0
        target_fauna.set_total_mass = Mock()
        self.plot2.get_a_fauna.return_value = target_fauna
        self.plot2.over_prey_capacity = Mock(return_value=False)
        self.grid._migrate_fauna(fauna, self.plot2, 'over_prey_capacity', 0.5)
        # assert both target and source fauna masses updated
        target_fauna.set_total_mass.assert_called() 
        fauna.set_total_mass.assert_called()

    def test_migrate_fauna_no_migration_if_over_capacity(self):
        self.grid.plots = {(0, 0): self.plot1, (0, 1): self.plot2}
        self.grid.get_neighbors = Mock(return_value=[self.plot2])
        fauna = Mock()
        fauna.name = "mammoth"
        fauna.get_total_mass.return_value = 100.0
        fauna.set_total_mass = Mock()
        fauna.__class__.__name__ = "Fauna"
        self.plot2.over_prey_capacity = Mock(return_value=True)
        self.plot2.get_a_fauna.return_value = None
        self.plot2.add_fauna = Mock()
        self.grid._migrate_fauna(fauna, self.plot2, 'over_prey_capacity', 0.5)
        # assert no transfer of mass or addition of fauna
        self.plot2.add_fauna.assert_not_called()
        fauna.set_total_mass.assert_not_called()

    @patch('numpy.random.random', return_value=0.1)
    @patch('numpy.random.choice', return_value=Mock(spec=Plot))
    def test_migrate_species_triggers_migration(self, mock_choice, mock_random):
        self.grid.plots = {(0, 0): self.plot1, (0, 1): self.plot2}
        self.grid.get_neighbors = Mock(return_value=[self.plot2])
        fauna = Mock()
        fauna.get_total_mass.return_value = 100.0
        fauna.__class__.__name__ = "Fauna"
        fauna.name = "mammoth"
        fauna.update_prey_mass = Mock()
        self.plot1.get_all_fauna.return_value = [fauna]
        self.plot2.get_all_fauna.return_value = []
        self.plot2.over_prey_capacity = Mock(return_value=False)
        self.plot2.get_a_fauna.return_value = None
        self.plot2.add_fauna = Mock()
        # Ensure migration conditions are met
        fauna.get_total_mass.return_value = 100.0
        fauna.update_prey_mass = Mock()
        self.grid.get_neighbors = Mock(return_value=[self.plot2])
        with patch.object(PlotGrid, '_migrate_fauna') as mock_migrate:
            self.grid.migrate_species()
            mock_migrate.assert_called()

if __name__ == '__main__':
    unittest.main()