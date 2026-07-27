"""
Main script to run the mammoth repopulation simulation.
This script initializes a grid based on real Siberia geography and
visualizes the biome map using a Dash web app.
"""

from app.grid_builder import create_siberia_grid
from app.dash_app import create_dash_app


def main() -> None:
    print("=" * 50)
    print("Mammoth Repopulation Simulator")
    print("=" * 50)

    plot_grid, grid_cells, initializer = create_siberia_grid(
        resolution=0.55, lon_min=130.0, lon_max=180.0
    )

    app = create_dash_app(plot_grid, initializer)

    print("\nStarting Dash server...")
    print("   Open http://127.0.0.1:8050 in your browser")
    print("   Press Ctrl+C to stop\n")
    app.run(debug=False, port=8050)


if __name__ == "__main__":
    main()