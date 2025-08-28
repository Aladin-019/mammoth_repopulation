import unittest
from unittest.mock import Mock, patch
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot.Plot import Plot
from app.models.Climate import Climate
import numpy as np

class TestPlotGrid(unittest.TestCase):
    def setUp(self):
        self.grid = PlotGrid()
        self.climate = Climate('northern taiga', None)
        self.real_plot1 = Plot(Id=1, avg_snow_height=0.1, climate=self.climate, plot_area=1.0)
        self.real_plot2 = Plot(Id=2, avg_snow_height=0.2, climate=self.climate, plot_area=2.0)
        self.plot1 = Mock(spec=Plot)
        self.plot2 = Mock(spec=Plot)

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

    def test_update_all_plots_staggered_updates(self):
        """
        Test that update_all_plots performs staggered updates for flora, prey, 
        and predator, and handles snow height, extinction, and migration.
        """
        # Setup grid with two mock plots
        self.grid.plots = {(0, 0): self.plot1, (0, 1): self.plot2}
        # Mock all required plot methods
        for plot in [self.plot1, self.plot2]:
            plot.update_avg_snow_height = Mock()
            plot.get_all_flora = Mock(return_value=[Mock()])
            plot.get_all_fauna = Mock(return_value=[Mock()])
            plot.remove_extinct_species = Mock()
            plot.add_fauna = Mock()
        # Mock flora and fauna update methods
        flora1 = Mock()
        flora2 = Mock()
        fauna1 = Mock()
        fauna2 = Mock()
        flora1.update_flora_mass = Mock()
        flora2.update_flora_mass = Mock()
        fauna1.update_prey_mass = Mock()
        fauna2.update_predator_mass = Mock()
        self.plot1.get_all_flora.return_value = [flora1]
        self.plot2.get_all_flora.return_value = [flora2]
        self.plot1.get_all_fauna.return_value = [fauna1]
        self.plot2.get_all_fauna.return_value = [fauna2]
        # Test Day 1: Flora updates only
        self.grid.update_all_plots(day=1)
        flora1.update_flora_mass.assert_called_with(1)
        flora2.update_flora_mass.assert_called_with(1)
        fauna1.update_prey_mass.assert_not_called()
        fauna2.update_predator_mass.assert_not_called()
        # Test Day 2: Prey updates only
        fauna1.update_prey_mass.reset_mock()
        fauna2.update_predator_mass.reset_mock()
        self.grid.update_all_plots(day=2)
        fauna1.update_prey_mass.assert_called_with(2)
        fauna2.update_predator_mass.assert_not_called()
        # Test Day 3: Flora and predator updates
        flora1.update_flora_mass.reset_mock()
        flora2.update_flora_mass.reset_mock()
        fauna2.update_predator_mass.reset_mock()
        self.grid.update_all_plots(day=3)
        flora1.update_flora_mass.assert_called_with(3)
        flora2.update_flora_mass.assert_called_with(3)
        fauna2.update_predator_mass.assert_called_with(3)

        for day in [1,2,3,4,5,6,7,8,9,10,11]:
            # Test migration triggered every 5th day only
            if day % 5 == 0:
                with patch.object(self.grid, 'migrate_species') as mock_migrate:
                    self.grid.update_all_plots(day=day)
                    mock_migrate.assert_called()
            else:
                with patch.object(self.grid, 'migrate_species') as mock_migrate:
                    self.grid.update_all_plots(day=day)
                    mock_migrate.assert_not_called()

            # Test snow height and extinction always called
            for plot in [self.plot1, self.plot2]:
                plot.update_avg_snow_height.assert_any_call(day)
                plot.remove_extinct_species.assert_any_call()

    def test_update_all_plots_staggered_updates_multiple_animals(self):
        # Test with multiple flora and fauna in plots
        flora1 = Mock()
        flora2 = Mock()
        fauna1 = Mock()
        fauna2 = Mock()
        flora1.update_flora_mass = Mock()
        flora2.update_flora_mass = Mock()
        fauna1.update_prey_mass = Mock()
        fauna2.update_predator_mass = Mock()
        flora1_new = Mock()
        flora2_new = Mock()
        fauna1_new = Mock()
        fauna2_new = Mock()
        flora1_new.update_flora_mass = Mock()
        flora2_new.update_flora_mass = Mock()
        fauna1_new.update_prey_mass = Mock()
        fauna2_new.update_predator_mass = Mock()
        # fresh plot mocks for this test
        plot1 = Mock(spec=Plot)
        plot2 = Mock(spec=Plot)
        plot1.update_avg_snow_height = Mock()
        plot2.update_avg_snow_height = Mock()
        plot1.remove_extinct_species = Mock()
        plot2.remove_extinct_species = Mock()
        plot1.add_fauna = Mock()
        plot2.add_fauna = Mock()
        plot1.get_all_flora.return_value = [flora1, flora1_new]
        plot2.get_all_flora.return_value = [flora2, flora2_new]
        plot1.get_all_fauna.return_value = [fauna1, fauna1_new]
        plot2.get_all_fauna.return_value = [fauna2, fauna2_new]
        self.grid.plots = {(0, 0): plot1, (0, 1): plot2}
        self.plot1.update_avg_snow_height = Mock()
        self.plot2.update_avg_snow_height = Mock()
        self.plot1.remove_extinct_species = Mock()
        self.plot2.remove_extinct_species = Mock()
        self.plot1.add_fauna = Mock()
        self.plot2.add_fauna = Mock()
        self.plot1.get_all_flora.return_value = [flora1, flora1_new]
        self.plot2.get_all_flora.return_value = [flora2, flora2_new]
        self.plot1.get_all_fauna.return_value = [fauna1, fauna1_new]
        self.plot2.get_all_fauna.return_value = [fauna2, fauna2_new]
        # Test Day 1: Flora updates only
        self.grid.update_all_plots(day=1)
        flora1.update_flora_mass.assert_called_with(1)
        flora1_new.update_flora_mass.assert_called_with(1)
        flora2.update_flora_mass.assert_called_with(1)
        flora2_new.update_flora_mass.assert_called_with(1)
        fauna1.update_prey_mass.assert_not_called()
        fauna1_new.update_prey_mass.assert_not_called()
        fauna2.update_predator_mass.assert_not_called()
        fauna2_new.update_predator_mass.assert_not_called()
        # Test Day 2: Prey updates only
        fauna1.update_prey_mass.reset_mock()
        fauna1_new.update_prey_mass.reset_mock()
        fauna2.update_predator_mass.reset_mock()
        fauna2_new.update_predator_mass.reset_mock()
        self.grid.update_all_plots(day=2)
        fauna1.update_prey_mass.assert_called_with(2)
        fauna1_new.update_prey_mass.assert_called_with(2)
        fauna2.update_predator_mass.assert_not_called()
        fauna2_new.update_predator_mass.assert_not_called()
        # Test Day 3: Flora and predator updates
        flora1.update_flora_mass.reset_mock()
        flora1_new.update_flora_mass.reset_mock()
        flora2.update_flora_mass.reset_mock()
        flora2_new.update_flora_mass.reset_mock()
        fauna2.update_predator_mass.reset_mock()
        fauna2_new.update_predator_mass.reset_mock()
        fauna1.update_prey_mass.reset_mock()
        fauna1_new.update_prey_mass.reset_mock()
        self.grid.update_all_plots(day=3)
        flora1.update_flora_mass.assert_called_with(3)
        flora1_new.update_flora_mass.assert_called_with(3)
        flora2.update_flora_mass.assert_called_with(3)
        flora2_new.update_flora_mass.assert_called_with(3)
        fauna2.update_predator_mass.assert_called_with(3)
        fauna2_new.update_predator_mass.assert_called_with(3)
        fauna1.update_prey_mass.assert_not_called()
        fauna1_new.update_prey_mass.assert_not_called()

        for day in [1,2,3,4,5,6,7,8,9,10,11]:
            # Test migration triggered every 5th day only
            if day % 5 == 0:
                with patch.object(self.grid, 'migrate_species') as mock_migrate:
                    self.grid.update_all_plots(day=day)
                    mock_migrate.assert_called()
            else:
                with patch.object(self.grid, 'migrate_species') as mock_migrate:
                    self.grid.update_all_plots(day=day)
                    mock_migrate.assert_not_called()

            # Test snow height and extinction always called
            for plot in [plot1, plot2]:
                plot.update_avg_snow_height.assert_any_call(day)
                plot.remove_extinct_species.assert_any_call()

    def test_update_all_plots_empty_plot(self):
        """
        Test that update_all_plots works with plots that have no flora or fauna.
        Should not raise errors and should call snow height and extinction methods.
        """
        empty_plot = Mock(spec=Plot)
        empty_plot.get_all_flora.return_value = []
        empty_plot.get_all_fauna.return_value = []
        empty_plot.update_avg_snow_height = Mock()
        empty_plot.remove_extinct_species = Mock()

        empty_plot.update_flora_mass = Mock()
        empty_plot.update_prey_mass = Mock()
        empty_plot.update_predator_mass = Mock()
        empty_plot.add_fauna = Mock()
        self.grid.plots = {(0, 0): empty_plot}
        # Run for several days to check all update branches
        for day in [1, 2, 3, 5, 10]:
            self.grid.update_all_plots(day=day)
            empty_plot.update_avg_snow_height.assert_any_call(day)
            empty_plot.remove_extinct_species.assert_any_call()
            empty_plot.update_flora_mass.assert_not_called()
            empty_plot.update_prey_mass.assert_not_called()
            empty_plot.update_predator_mass.assert_not_called()
            empty_plot.add_fauna.assert_not_called()

    def test_visualize_biomes_no_plots(self):
        """
        Test visualize_biomes with no plots in the grid.
        Should print 'No plots to visualize' and not raise errors.
        """
        self.grid.plots = {}
        biome_colors = {'taiga': '#228B22', 'tundra': '#A9A9A9'}
        # Patch print to capture output
        with patch('builtins.print') as mock_print:
            self.grid.visualize_biomes(biome_colors)
            mock_print.assert_any_call('No plots to visualize')

    def test_visualize_biomes_matplotlib_not_available(self):
        """
        Test visualize_biomes when matplotlib is not available.
        Should print 'Matplotlib is not available. Cannot create visualization.'
        """
        # Patch MATPLOTLIB_AVAILABLE to False
        with patch('app.models.Plot.PlotGrid.MATPLOTLIB_AVAILABLE', False):
            biome_colors = {'taiga': '#228B22', 'tundra': '#A9A9A9'}
            with patch('builtins.print') as mock_print:
                self.grid.visualize_biomes(biome_colors)
                mock_print.assert_any_call('Matplotlib is not available. Cannot create visualization.')

    def test_visualize_biomes_basic(self):
        """
        Test visualize_biomes with a simple grid and biome mapping.
        Should call plt.show() if matplotlib is available and not raise errors.
        """
        if not hasattr(self.grid, 'visualize_biomes'):
            return  # Skip if method not present
        # Create mock plots with get_climate().get_biome()
        plot1 = Mock(spec=Plot)
        plot2 = Mock(spec=Plot)
        climate1 = Mock()
        climate2 = Mock()
        climate1.get_biome.return_value = 'taiga'
        climate2.get_biome.return_value = 'tundra'
        plot1.get_climate.return_value = climate1
        plot2.get_climate.return_value = climate2
        self.grid.plots = {(0, 0): plot1, (0, 1): plot2}
        self.grid.min_row = 0
        self.grid.max_row = 0
        self.grid.min_col = 0
        self.grid.max_col = 1
        biome_colors = {'taiga': '#228B22', 'tundra': '#A9A9A9'}
        # Patch plt.show and _blend_biome_borders to avoid randomness and window
        with patch('matplotlib.pyplot.show') as mock_show, \
             patch.object(self.grid, '_blend_biome_borders', side_effect=lambda grid, rows, cols, blend_prob=0.2: grid):
            self.grid.visualize_biomes(biome_colors)
            mock_show.assert_called()

    def test_blend_biome_borders(self):
        """
        Test _blend_biome_borders helper for correct blending behavior.
        """
        # Create a simple grid with a border between two biomes
        grid = np.array([
            [0, 0, 1],
            [0, 1, 1],
            [1, 1, 1]
        ], dtype=int)
        rows, cols = grid.shape
        # Patch random.random to always blend, and random.choice to pick the first neighbor
        with patch('random.random', return_value=0.0), patch('random.choice', side_effect=lambda x: x[0]):
            blended = self.grid._blend_biome_borders(grid, rows, cols, blend_prob=1.0)
        # Check that border cells have been blended
        # At 100% blend probability and diaglonals including neighbors, then
        # blended grid should be:
        #print("Blended Grid:\n", blended)
        self.assertTrue(np.array_equal(blended, np.array([
            [1, 1, 0],
            [1, 0, 0],
            [0, 0, 1]
        ], dtype=int)))
        
if __name__ == '__main__':
    unittest.main()