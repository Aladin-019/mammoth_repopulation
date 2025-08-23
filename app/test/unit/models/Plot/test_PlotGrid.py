import unittest
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Plot import Plot
from app.models.Climate import Climate

class TestPlotGrid(unittest.TestCase):
    def setUp(self):
        self.grid = PlotGrid()
        # Minimal Climate stub for Plot
        self.climate = Climate('northern taiga', None)
        self.plot1 = Plot(Id=1, avg_snow_height=0.1, climate=self.climate, plot_area=1.0)
        self.plot2 = Plot(Id=2, avg_snow_height=0.2, climate=self.climate, plot_area=2.0)

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
        self.assertIsNone(self.grid.get_plot(0, 0))
        self.assertEqual(self.grid.plots, {})

    def test_get_all_plots(self):
        self.grid.add_plot(0, 0, self.plot1)
        self.grid.add_plot(1, 2, self.plot2)
        all_plots = self.grid.get_all_plots()
        self.assertEqual(len(all_plots), 2)
        self.assertIn(self.plot1, all_plots)
        self.assertIn(self.plot2, all_plots)

        # Test with empty grid
        empty_grid = PlotGrid()
        self.assertEqual(empty_grid.get_all_plots(), [])

    def test_get_plot_coordinates(self):
        self.grid.add_plot(0, 0, self.plot1)
        self.grid.add_plot(1, 2, self.plot2)
        coords = list(self.grid.plots.keys())
        self.assertIn((0, 0), coords)
        self.assertIn((1, 2), coords)
        self.assertEqual(len(coords), 2)

        # Test after overwriting a plot
        self.grid.add_plot(0, 0, self.plot2)
        coords = list(self.grid.plots.keys())
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

if __name__ == '__main__':
    unittest.main()