"""
Main script to run the mammoth repopulation simulation.
This script initializes a grid based on real Siberia geography and
visualizes the biome map using a Dash web app.
"""

from typing import Tuple, List, Optional, Dict
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
from app.models.Fauna.Prey import Prey
import numpy as np


# ── Biome colors used throughout ──
BIOME_COLORS: Dict[str, str] = {
    'southern taiga': '#228B22',
    'northern taiga': '#32CD32',
    'southern tundra': '#D3D3D3',
    'northern tundra': '#FFFFFF',
    'mammoth steppe': '#8B9662',
}


def latitude_to_biome(latitude: float) -> str:
    """
    Convert latitude to biome type based on Siberia's biome distribution.
    
    Based on climate data locations:
    - Krasnoyarsk (56.0°N) - southern taiga
    - Salekhard (66.5°N) - northern taiga  
    - Saskylakh (71.9°N) - southern tundra
    - Cape Chelyuskin (77.7°N) - northern tundra
    
    Args:
        latitude: Latitude in degrees
    Returns:
        Biome name string
    """
    if latitude < 60.0:
        return 'southern taiga'
    elif latitude < 70.0:
        return 'northern taiga'
    elif latitude < 75.0:
        return 'southern tundra'
    else:
        return 'northern tundra'


def create_siberia_grid(resolution: float = 0.75, lon_min: float = 120.0, lon_max: float = 180.0) -> Tuple[PlotGrid, List[Tuple[float, float]], GridInitializer]:
    """
    Create a realistic Siberia grid using actual geography.
    Only creates plots for land cells (within Siberia polygon), not water.
    
    Args:
        resolution: Grid resolution in degrees (default: 0.75 for better detail)
        lon_min: Minimum longitude (default: 120.0 for eastern/right third)
        lon_max: Maximum longitude (default: 180.0 for eastern edge)
    
    Returns:
        Tuple of (PlotGrid, list of (lon, lat) coordinates, GridInitializer)
    """
    import geopandas as gp
    from shapely.geometry import Point, box
    import os
    
    # Generate grid with specified resolution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    geo_json_path = os.path.join(project_root, "app", "data", "geographical_data", "russia_borders_data", "custom.geo.json")
    
    # Load Russia GeoJSON
    gdf = gp.read_file(geo_json_path)
    russia = gdf[gdf["name"].str.contains("Russia", case=False)]
    minx, miny, maxx, maxy = russia.total_bounds
    # Use custom longitude range for eastern/right third
    clip_box = box(lon_min, miny, maxx, maxy)
    siberia_polyg = russia.geometry.iloc[0].intersection(clip_box)
    
    # Generate grid cells with specified resolution - ONLY for land (within polygon)
    # Focusing on eastern/right third of Siberia
    latitudes = np.arange(45.0, 80.1, resolution)
    longitudes = np.arange(lon_min, lon_max + resolution, resolution)
    grid_cells = []
    for lat in latitudes:
        for lon in longitudes:
            pt = Point(lon, lat)
            # Only include points that are within the Siberia polygon (land, not water)
            if siberia_polyg.contains(pt):
                grid_cells.append((lon, lat))
    
    print(f"Generated {len(grid_cells)} grid cells from eastern Siberia ({resolution}° resolution, {lon_min}°-{lon_max}°E)")
    
    # Initialize grid with matching resolution
    initializer = GridInitializer(lat_step=resolution, lon_step=resolution)
    plot_grid = initializer.get_plot_grid()
    
    # Convert lat/lon to row/col indices for the grid
    # Use the actual grid cell coordinates to maintain spatial relationships
    unique_lats = sorted(set(lat for lon, lat in grid_cells))
    unique_lons = sorted(set(lon for lon, lat in grid_cells))
    
    lat_to_row = {lat: row for row, lat in enumerate(unique_lats)}
    lon_to_col = {lon: col for col, lon in enumerate(unique_lons)}
    
    print("Creating plots from grid cells...")
    for lon, lat in grid_cells:
        row = lat_to_row[lat]
        col = lon_to_col[lon]
        biome = latitude_to_biome(lat)
        
        plot = initializer.create_plot_from_biome(biome)
        plot_grid.add_plot(row, col, plot)
    
    print(f"Created grid with {len(plot_grid.plots)} plots (land only)")
    return plot_grid, grid_cells, initializer


def add_mammoths_to_location(plot_grid: PlotGrid, initializer: GridInitializer, row: int, col: int, population_per_km2: float = 15.0) -> Optional[Prey]:
    """
    Add mammoths to a specific plot location.
    
    Args:
        plot_grid: The PlotGrid to add mammoths to
        initializer: The GridInitializer instance
        row: Row coordinate of the plot
        col: Column coordinate of the plot
        population_per_km2: Population density in mammoths per km^2
    
    Returns:
        The mammoth Prey object if successful, None otherwise
    """
    plot = plot_grid.get_plot(row, col)
    if plot is None:
        print(f"Warning: No plot found at row={row}, col={col}")
        return None
    
    mammoth = initializer.add_mammoth_to_plot(plot, population_per_km2=population_per_km2)
    if mammoth:
        print(f"Added mammoths to plot at row={row}, col={col} with population density {population_per_km2} per km^2")
        print(f"  Actual population: {mammoth.population} mammoths")
    return mammoth


# ═══════════════════════════════════════════════════════════
#  Grid data helpers
# ═══════════════════════════════════════════════════════════

def _grid_shape(pg: PlotGrid):
    """Get the shape of the grid."""
    rows = pg.max_row - pg.min_row + 1
    cols = pg.max_col - pg.min_col + 1
    return rows, cols


def build_biome_grid(pg: PlotGrid) -> np.ndarray:
    """Return 2D int array: 0=water, 1..N = biome index."""
    rows, cols = _grid_shape(pg)
    grid = np.zeros((rows, cols), dtype=int)
    biome_to_int = {b: i + 1 for i, b in enumerate(BIOME_COLORS)}
    for (r, c), plot in pg.plots.items():
        biome = plot.get_climate().get_biome()
        grid[r - pg.min_row, c - pg.min_col] = biome_to_int.get(biome, 0)
    return grid


def biome_colorscale():
    """Discrete colorscale for the biome grid."""
    water = '#001F5C'
    all_c = [water] + list(BIOME_COLORS.values())
    n = len(all_c)
    cs = []
    for i, c in enumerate(all_c):
        cs.append([i / n, c])
        cs.append([(i + 1) / n, c])
    return cs, n


def get_population_stats(pg: PlotGrid) -> Dict:
    """Gather per-species population totals and flora totals."""
    fauna_pops: Dict[str, int] = {}
    flora_mass: Dict[str, float] = {'Grass': 0, 'Shrub': 0, 'Tree': 0, 'Moss': 0}
    for plot in pg.get_all_plots():
        for f in plot.get_all_fauna():
            if f.get_total_mass() > 0:
                fauna_pops[f.get_name()] = fauna_pops.get(f.get_name(), 0) + f.get_population()
        gm, sm, tm, mm = plot.get_flora_masses()
        flora_mass['Grass'] += gm
        flora_mass['Shrub'] += sm
        flora_mass['Tree'] += tm
        flora_mass['Moss'] += mm
    return {'fauna': fauna_pops, 'flora': flora_mass}


# ═══════════════════════════════════════════════════════════
#  Dash App
# ═══════════════════════════════════════════════════════════

def _build_figure(plot_grid: PlotGrid, day: int = 0):
    """Build a Plotly figure showing the biome grid."""
    import plotly.graph_objects as go

    biome_grid = build_biome_grid(plot_grid)
    cs, n_colors = biome_colorscale()
    cbar_labels = ['Water'] + list(BIOME_COLORS.keys())

    biome_trace = go.Heatmap(
        z=biome_grid.tolist(),
        colorscale=cs,
        zmin=0,
        zmax=n_colors - 1,
        colorbar=dict(
            title='Biome', tickvals=list(range(n_colors)),
            ticktext=cbar_labels, tickfont=dict(size=9), len=0.5, x=1.02,
        ),
        hovertemplate='Row %{y}, Col %{x}<br>Biome idx: %{z}<extra></extra>',
        showscale=True,
        name='Biome',
    )

    title_text = f'Eastern Siberia Biome Map — Day {day}'

    fig = go.Figure(data=[biome_trace])
    fig.update_layout(
        title=dict(text=title_text, x=0.5, font=dict(size=16)),
        xaxis=dict(showticklabels=False, showgrid=False, constrain='domain'),
        yaxis=dict(showticklabels=False, showgrid=False, scaleanchor='x'),
        margin=dict(l=10, r=120, t=50, b=10),
        plot_bgcolor='#001F5C',
        paper_bgcolor='#f5f5f5',
    )
    return fig


def _build_stats(plot_grid: PlotGrid, day: int):
    """Build the stats panel children."""
    from dash import html

    stats = get_population_stats(plot_grid)
    children = [
        html.Div(f"Day {day}", style={
            'fontSize': '16px', 'fontWeight': 'bold', 'marginBottom': '10px',
        }),
        html.B("Fauna"),
    ]
    if stats['fauna']:
        for name, pop in stats['fauna'].items():
            children.append(html.Div(f"  {name}: {pop:,}"))
    else:
        children.append(html.Div("  (none yet)"))

    children.append(html.B("Flora biomass (kg)", style={'marginTop': '10px', 'display': 'block'}))
    for fname, mass in stats['flora'].items():
        children.append(html.Div(f"  {fname}: {mass:,.0f}"))

    return children


def create_dash_app(plot_grid: PlotGrid, initializer: GridInitializer):
    """Build and return the Dash application."""
    from dash import Dash, html, dcc

    app = Dash(__name__)
    app.title = "Mammoth Repopulation Simulator"

    # Initial figure
    init_fig = _build_figure(plot_grid)

    # ── Layout ──
    app.layout = html.Div(style={'display': 'flex', 'height': '100vh', 'fontFamily': 'Arial'}, children=[
        # ── Sidebar ──
        html.Div(id='sidebar', style={
            'width': '300px', 'padding': '20px', 'backgroundColor': '#1a1a2e',
            'color': '#eee', 'overflowY': 'auto', 'flexShrink': 0,
        }, children=[
            html.H2("Mammoth Sim", style={'margin': '0 0 15px 0', 'textAlign': 'center'}),
            html.Hr(style={'borderColor': '#444'}),

            html.P("Siberia biome visualization. Interactive features coming soon!",
                   style={'fontSize': '12px', 'color': '#aaa', 'lineHeight': '1.5'}),

            html.Hr(style={'borderColor': '#444'}),

            # ── Stats panel ──
            html.Div(id='stats-panel', children=_build_stats(plot_grid, 0),
                     style={'fontSize': '13px', 'lineHeight': '1.8'}),
        ]),

        # ── Main map area ──
        html.Div(style={'flex': 1, 'position': 'relative'}, children=[
            dcc.Graph(id='biome-map', figure=init_fig, style={'height': '100%'},
                      config={'scrollZoom': True, 'displayModeBar': True}),
        ]),
    ])

    return app


# ═══════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════

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

