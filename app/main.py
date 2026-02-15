"""
Main script to run the mammoth repopulation simulation.
This script initializes a grid based on real Siberia geography and
visualizes the biome map using a Dash web app.
"""

from typing import Tuple, List, Dict
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
import numpy as np


# ── Biome colors used throughout ──
BIOME_COLORS: Dict[str, str] = {
    'southern taiga': "#1D5A1D",
    'northern taiga': "#2A802A",
    'southern tundra': "#66A37B",
    'northern tundra': "#7BA696",
    'mammoth steppe': "#8D9E4A",
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


# ═══════════════════════════════════════════════════════════
#  Grid data helpers
# ═══════════════════════════════════════════════════════════

# Cache for blended grid - blend once at startup, then only update changed cells
_grid_cache: Dict = {'blended': None, 'original': None}


def _grid_shape(pg: PlotGrid):
    """Get the shape of the grid."""
    rows = pg.max_row - pg.min_row + 1
    cols = pg.max_col - pg.min_col + 1
    return rows, cols


def _blend_biome_borders(grid: np.ndarray, blend_prob: float = 0.2, seed: int = 42) -> np.ndarray:
    """
    Blend biome borders for more realistic transitions.
    For each border plot (adjacent to a different biome), with probability blend_prob,
    assign the plot the biome of a neighbor.
    Water cells (value 0) are never changed.
    """
    import random
    rng = random.Random(seed)
    rows, cols = grid.shape
    blended = grid.copy()
    
    for r in range(rows):
        for c in range(cols):
            biome_idx = grid[r, c]
            if biome_idx == 0:  # Skip water
                continue
            
            # Check neighbors for different biome (excluding water)
            neighbor_biomes = set()
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbor = grid[nr, nc]
                        if neighbor != biome_idx and neighbor != 0:
                            neighbor_biomes.add(neighbor)
            
            if neighbor_biomes and rng.random() < blend_prob:
                blended[r, c] = rng.choice(list(neighbor_biomes))
    
    return blended


def build_biome_grid(pg: PlotGrid) -> np.ndarray:
    """Return 2D int array: 0=water, 1..N = biome index.
    
    On first call: builds grid and applies blending, caches both.
    On subsequent calls: uses cached blended grid, only updates cells where biome actually changed.
    """
    rows, cols = _grid_shape(pg)
    biome_to_int = {b: i + 1 for i, b in enumerate(BIOME_COLORS)}
    
    # Build current raw grid
    current_grid = np.zeros((rows, cols), dtype=int)
    for (r, c), plot in pg.plots.items():
        biome = plot.get_climate().get_biome()
        current_grid[r - pg.min_row, c - pg.min_col] = biome_to_int.get(biome, 0)
    
    # First call - blend and cache
    if _grid_cache['blended'] is None:
        _grid_cache['original'] = current_grid.copy()
        _grid_cache['blended'] = _blend_biome_borders(current_grid, blend_prob=0.2, seed=42)
        return _grid_cache['blended'].copy()
    
    # Subsequent calls - update only cells where biome actually changed
    result = _grid_cache['blended'].copy()
    for r in range(rows):
        for c in range(cols):
            if current_grid[r, c] != _grid_cache['original'][r, c]:
                # Biome changed - update to new biome (no blending)
                result[r, c] = current_grid[r, c]
                _grid_cache['original'][r, c] = current_grid[r, c]
                _grid_cache['blended'][r, c] = current_grid[r, c]
    
    return result


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

def _build_figure(plot_grid: PlotGrid, placements: Dict = None, day: int = 0):
    """Build a Plotly figure showing the biome grid with optional placement markers."""
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

    shapes = []

    # Show colored borders on placement cells (before simulation starts)
    if placements and day == 0:
        for key, info in placements.items():
            r, c = map(int, key.split(','))
            gr = r - plot_grid.min_row
            gc = c - plot_grid.min_col
            # Handle both new format (dict with species) and old format (just density)
            if isinstance(info, dict):
                species = info.get('species', 'mammoth')
            else:
                species = 'mammoth'
            # Different colors: red/orange for mammoth, gray for wolf
            if species == 'wolf':
                border_color = '#7f8c8d'
                fill_color = 'rgba(127,140,141,0.15)'
            else:
                border_color = 'red'
                fill_color = 'rgba(255,0,0,0.15)'
            shapes.append(dict(
                type='rect',
                x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                line=dict(color=border_color, width=2),
                fillcolor=fill_color,
            ))

    # Show borders on plots with fauna (during simulation)
    mammoth_count = 0
    wolf_count = 0
    if day > 0:
        for (r, c), plot in plot_grid.plots.items():
            has_mammoths = any(f.get_name() == 'Mammoth' and f.get_population() > 0 
                               for f in plot.get_all_fauna())
            has_wolves = any(f.get_name() == 'Wolf' and f.get_population() > 0 
                             for f in plot.get_all_fauna())
            gr = r - plot_grid.min_row
            gc = c - plot_grid.min_col
            if has_mammoths:
                mammoth_count += 1
                shapes.append(dict(
                    type='rect',
                    x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                    line=dict(color='#8B4513', width=2),  # Brown
                    fillcolor='rgba(139,69,19,0.15)',
                ))
            if has_wolves:
                wolf_count += 1
                shapes.append(dict(
                    type='rect',
                    x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                    line=dict(color='#7f8c8d', width=2),  # Gray
                    fillcolor='rgba(127,140,141,0.15)',
                ))

    title_text = 'Eastern Siberia — Click to place fauna' if day == 0 else f'Eastern Siberia Biome Map — Day {day}'
    if placements and day == 0:
        title_text = f'Eastern Siberia — {len(placements)} placement(s)'

    fig = go.Figure(data=[biome_trace])

    fig.update_layout(
        title=dict(text=title_text, x=0.5, font=dict(size=16)),
        xaxis=dict(showticklabels=False, showgrid=False, constrain='domain'),
        yaxis=dict(showticklabels=False, showgrid=False, scaleanchor='x'),
        shapes=shapes,
        margin=dict(l=10, r=120, t=50, b=10),
        plot_bgcolor='#001F5C',
        paper_bgcolor='#f5f5f5',
    )
    return fig, mammoth_count, wolf_count


def _build_stats(plot_grid: PlotGrid, day: int, mammoth_plots: int = 0, wolf_plots: int = 0):
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
        if mammoth_plots > 0:
            children.append(html.Div(
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '8px', 'gap': '8px'},
                children=[
                    # Hollow brown box to match plot borders on map
                    html.Div(style={
                        'width': '14px',
                        'height': '14px',
                        'border': '2px solid #8B4513',
                        'borderRadius': '2px',
                        'flexShrink': '0',
                    }),
                    html.Span(f"{mammoth_plots} plots with mammoths", style={
                        'color': '#CD853F',
                        'fontSize': '12px',
                    }),
                ]
            ))
        if wolf_plots > 0:
            children.append(html.Div(
                style={'display': 'flex', 'alignItems': 'center', 'marginTop': '8px', 'gap': '8px'},
                children=[
                    # Hollow gray box to match wolf plot borders
                    html.Div(style={
                        'width': '14px',
                        'height': '14px',
                        'border': '2px solid #7f8c8d',
                        'borderRadius': '2px',
                        'flexShrink': '0',
                    }),
                    html.Span(f"{wolf_plots} plots with wolves", style={
                        'color': '#95a5a6',
                        'fontSize': '12px',
                    }),
                ]
            ))
    else:
        children.append(html.Div("  (none yet)"))

    children.append(html.B("Flora biomass (kg)", style={'marginTop': '10px', 'display': 'block'}))
    for fname, mass in stats['flora'].items():
        children.append(html.Div(f"  {fname}: {mass:,.0f}"))

    return children


def create_dash_app(plot_grid: PlotGrid, initializer: GridInitializer):
    """Build and return the Dash application with interactive fauna placement."""
    from dash import Dash, html, dcc, Input, Output, State, no_update

    app = Dash(__name__)
    app.title = "Mammoth Repopulation Simulator"

    # Initial figure
    init_fig, _, _ = _build_figure(plot_grid)

    # ── Layout ──
    app.layout = html.Div(style={'display': 'flex', 'height': '100vh', 'fontFamily': 'Arial'}, children=[
        # ── Sidebar ──
        html.Div(id='sidebar', style={
            'width': '300px', 'padding': '20px', 'backgroundColor': '#1a1a2e',
            'color': '#eee', 'overflowY': 'auto', 'flexShrink': 0,
        }, children=[
            html.H2("Mammoth Sim", style={'margin': '0 0 15px 0', 'textAlign': 'center'}),
            html.Hr(style={'borderColor': '#444'}),

            # ── Placement controls ──
            html.Div(id='placement-controls', children=[
                html.P("Click on a land plot to place fauna. Select species and density below, then click plots on the map.",
                       style={'fontSize': '12px', 'color': '#aaa', 'lineHeight': '1.5'}),

                # Species selector
                html.Label("Species:", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                dcc.RadioItems(
                    id='species-selector',
                    options=[
                        {'label': ' Mammoth', 'value': 'mammoth'},
                        {'label': ' Wolf', 'value': 'wolf'},
                    ],
                    value='mammoth',
                    style={'marginTop': '5px', 'marginBottom': '10px'},
                    inputStyle={'marginRight': '5px'},
                    labelStyle={'display': 'block', 'marginBottom': '5px', 'cursor': 'pointer'},
                ),

                # Density slider
                html.Label(id='density-label', children="Density (mammoths/km²):", style={'fontWeight': 'bold', 'marginTop': '10px'}),
                html.Div(id='density-display', children="2.0", style={
                    'fontSize': '18px', 'fontWeight': 'bold', 'color': '#f39c12',
                    'textAlign': 'center', 'marginTop': '5px',
                }),
                dcc.Slider(
                    id='density-slider',
                    min=0.5, max=20, step=0.5, value=2.0,
                    marks={i: str(i) for i in [1, 5, 10, 15, 20]},
                    tooltip=None,
                ),

                # Placement list
                html.Div(id='placement-list', style={
                    'marginTop': '15px', 'maxHeight': '200px', 'overflowY': 'auto',
                    'fontSize': '12px', 'lineHeight': '1.6',
                }),

                # Clear button
                html.Button('Clear All', id='clear-btn', n_clicks=0,
                            style={'marginTop': '15px', 'padding': '10px 20px', 'fontSize': '14px',
                                   'cursor': 'pointer', 'backgroundColor': '#e74c3c',
                                   'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                                   'fontWeight': 'bold', 'width': '100%'}),

                # Start Simulation button
                html.Button('Start Simulation', id='start-btn', n_clicks=0,
                            style={'marginTop': '10px', 'padding': '12px 20px', 'fontSize': '14px',
                                   'cursor': 'pointer', 'backgroundColor': '#27ae60',
                                   'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                                   'fontWeight': 'bold', 'width': '100%'}),
            ]),

            html.Hr(style={'borderColor': '#444'}),

            # ── Stats panel ──
            html.Div(id='stats-panel', children=_build_stats(plot_grid, 0),
                     style={'fontSize': '13px', 'lineHeight': '1.8'}),
        ]),

        # ── Main map area ──
        html.Div(style={'flex': 1, 'position': 'relative'}, children=[
            dcc.Graph(id='biome-map', figure=init_fig, style={'height': '100%'},
                      config={'scrollZoom': True, 'displayModeBar': True}),
            dcc.Store(id='placements', data={}),  # {"row,col": density}
            dcc.Store(id='sim-state', data={'running': False, 'day': 0, 'initialized': False}),
            dcc.Interval(id='sim-interval', interval=1000, disabled=True),  # 1s per day (reduced from 500ms for reliability)
        ]),
    ])

    # ══════════════════════════════════════════════════════
    #  Update density display and label when slider/species changes
    # ══════════════════════════════════════════════════════
    @app.callback(
        Output('density-display', 'children'),
        Output('density-label', 'children'),
        Input('density-slider', 'value'),
        Input('species-selector', 'value'),
    )
    def update_density_display(value, species):
        label = f"Density ({species}s/km²):"
        return f"{value}", label

    # ══════════════════════════════════════════════════════
    #  Click on map to add/remove placement
    # ══════════════════════════════════════════════════════
    @app.callback(
        Output('placements', 'data'),
        Output('biome-map', 'figure'),
        Output('placement-list', 'children'),
        Input('biome-map', 'clickData'),
        Input('clear-btn', 'n_clicks'),
        State('placements', 'data'),
        State('density-slider', 'value'),
        State('species-selector', 'value'),
        State('sim-state', 'data'),
        prevent_initial_call=True,
    )
    def handle_click_or_clear(click_data, clear_clicks, placements, density, species, sim_state):
        from dash import ctx, no_update

        triggered = ctx.triggered_id

        # Ignore clicks if simulation has started
        if sim_state and sim_state.get('initialized', False):
            return no_update, no_update, no_update

        if triggered == 'clear-btn':
            fig, _, _ = _build_figure(plot_grid, {}, 0)
            return {}, fig, []

        if triggered == 'biome-map' and click_data is not None:
            pt = click_data['points'][0]
            grid_col = int(round(pt['x']))
            grid_row = int(round(pt['y']))
            plot_row = grid_row + plot_grid.min_row
            plot_col = grid_col + plot_grid.min_col

            plot = plot_grid.get_plot(plot_row, plot_col)
            if plot is None:
                return no_update, no_update, no_update

            key = f'{plot_row},{plot_col}'
            if key in placements:
                new_placements = {k: v for k, v in placements.items() if k != key}
            else:
                new_placements = {**placements, key: {
                    'density': density if density and density > 0 else 2.0,
                    'species': species or 'mammoth'
                }}

            fig, _, _ = _build_figure(plot_grid, new_placements, 0)
            placement_items = _build_placement_list(plot_grid, new_placements)
            return new_placements, fig, placement_items

        return no_update, no_update, no_update

    # ══════════════════════════════════════════════════════
    #  Start/Stop simulation button
    # ══════════════════════════════════════════════════════
    @app.callback(
        Output('sim-state', 'data'),
        Output('sim-interval', 'disabled'),
        Output('start-btn', 'children'),
        Output('start-btn', 'style'),
        Output('placement-controls', 'style'),
        Input('start-btn', 'n_clicks'),
        State('sim-state', 'data'),
        State('placements', 'data'),
        prevent_initial_call=True,
    )
    def toggle_simulation(n_clicks, sim_state, placements):
        if sim_state['running']:
            # Stop simulation
            sim_state['running'] = False
            return (
                sim_state,
                True,  # disable interval
                'Start Simulation',
                {'marginTop': '10px', 'padding': '12px 20px', 'fontSize': '14px',
                 'cursor': 'pointer', 'backgroundColor': '#27ae60',
                 'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                 'fontWeight': 'bold', 'width': '100%'},
                {},  # show placement controls
            )
        else:
            # Start simulation - first add fauna from placements
            if not sim_state['initialized'] and placements:
                for key, info in placements.items():
                    r, c = map(int, key.split(','))
                    plot = plot_grid.get_plot(r, c)
                    if plot:
                        # Handle both new format (dict with species) and old format (just density)
                        if isinstance(info, dict):
                            density = info.get('density', 2.0)
                            species = info.get('species', 'mammoth')
                        else:
                            density = info
                            species = 'mammoth'
                        
                        if species == 'mammoth':
                            initializer.add_mammoth_to_plot(plot, population_per_km2=density)
                        elif species == 'wolf':
                            initializer.add_wolf_to_plot(plot, population_per_km2=density)
                sim_state['initialized'] = True

            sim_state['running'] = True
            return (
                sim_state,
                False,  # enable interval
                'Stop Simulation',
                {'marginTop': '10px', 'padding': '12px 20px', 'fontSize': '14px',
                 'cursor': 'pointer', 'backgroundColor': '#c0392b',
                 'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                 'fontWeight': 'bold', 'width': '100%'},
                {'display': 'none'},  # hide placement controls
            )

    # ══════════════════════════════════════════════════════
    #  Simulation step on interval
    # ══════════════════════════════════════════════════════
    @app.callback(
        Output('sim-state', 'data', allow_duplicate=True),
        Output('biome-map', 'figure', allow_duplicate=True),
        Output('stats-panel', 'children'),
        Input('sim-interval', 'n_intervals'),
        State('sim-state', 'data'),
        prevent_initial_call=True,
    )
    def run_simulation_step(n_intervals, sim_state):
        from dash import no_update

        if not sim_state['running']:
            return no_update, no_update, no_update

        # Advance one day
        new_state = dict(sim_state)
        new_state['day'] += 1
        plot_grid.update_all_plots(day=new_state['day'])
        print(f"[SIM] Day {new_state['day']} tick at n_intervals={n_intervals}")
        fig, mammoth_count, wolf_count = _build_figure(plot_grid, {}, new_state['day'])
        stats_children = _build_stats(plot_grid, new_state['day'], mammoth_count, wolf_count)
        return new_state, fig, stats_children

    return app


def _build_placement_list(plot_grid: PlotGrid, placements: Dict):
    """Build the placement list for the sidebar."""
    from dash import html

    items = []
    if placements:
        for key, info in placements.items():
            r, c = key.split(',')
            plot = plot_grid.get_plot(int(r), int(c))
            biome = plot.get_climate().get_biome() if plot else '?'
            # Handle both new format (dict with species) and old format (just density)
            if isinstance(info, dict):
                density = info.get('density', 2.0)
                species = info.get('species', 'mammoth')
            else:
                density = info
                species = 'mammoth'
            # Different colors for different species
            color = '#f39c12' if species == 'mammoth' else '#95a5a6'  # Orange for mammoth, gray for wolf
            items.append(html.Div(
                f"({r},{c}) {biome}: {species} {density}/km²",
                style={'color': color},
            ))
    return items


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