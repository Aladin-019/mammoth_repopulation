"""
Visualization helpers for the mammoth repopulation simulation.
Builds biome grids, Plotly figures, and sidebar stats/placement UI content.
"""

from typing import Dict
import logging
import numpy as np
from app.models.Plot.PlotGrid import PlotGrid


# ── Biome colors used throughout ──
BIOME_COLORS: Dict[str, str] = {
    'southern taiga': "#1D5A1D",
    'northern taiga': "#2A802A",
    'southern tundra': "#66A37B",
    'northern tundra': "#7BA696",
    'mammoth steppe': "#8D9E4A",
}

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


def _build_figure(plot_grid: PlotGrid, placements: Dict = None, day: int = 0):
    """Build a Plotly figure showing the biome grid with optional placement markers."""
    import plotly.graph_objects as go
    log = logging.getLogger(__name__)

    def _build_biome_trace(pg: PlotGrid):
        grid = build_biome_grid(pg)
        cs, n_colors = biome_colorscale()
        return go.Heatmap(
            z=grid.tolist(),
            colorscale=cs,
            zmin=0,
            zmax=n_colors - 1,
            hovertemplate='Row %{y}, Col %{x}<br>Biome idx: %{z}<extra></extra>',
            showscale=False,
            name='Biome',
        )

    def _placement_shapes(placements_local: Dict, pg: PlotGrid, d: int):
        shapes_local = []
        if placements_local and d == 0:
            for key, info in placements_local.items():
                r, c = map(int, key.split(','))
                gr = r - pg.min_row
                gc = c - pg.min_col
                if isinstance(info, dict):
                    species = info.get('species', 'mammoth')
                else:
                    species = 'mammoth'
                if species == 'wolf':
                    border_color = '#7f8c8d'
                    fill_color = 'rgba(127,140,141,0.15)'
                else:
                    border_color = '#8B4513'
                    fill_color = 'rgba(139,69,19,0.15)'
                shapes_local.append(dict(
                    type='rect',
                    x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                    line=dict(color=border_color, width=2),
                    fillcolor=fill_color,
                ))
        return shapes_local

    def _fauna_shapes_and_counts(pg: PlotGrid, d: int):
        shapes_local = []
        mammoth_count_local = 0
        wolf_count_local = 0
        if d > 0:
            for (r, c), plot in pg.plots.items():
                has_mammoths = any(f.get_name() == 'Mammoth' and f.get_population() > 0 for f in plot.get_all_fauna())
                has_wolves = any(f.get_name() == 'Wolf' and f.get_population() > 0 for f in plot.get_all_fauna())
                gr = r - pg.min_row
                gc = c - pg.min_col
                if has_mammoths:
                    mammoth_count_local += 1
                    shapes_local.append(dict(
                        type='rect',
                        x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                        line=dict(color='#8B4513', width=2),
                        fillcolor='rgba(139,69,19,0.15)',
                    ))
                if has_wolves:
                    wolf_count_local += 1
                    shapes_local.append(dict(
                        type='rect',
                        x0=gc - 0.5, y0=gr - 0.5, x1=gc + 0.5, y1=gr + 0.5,
                        line=dict(color='#7f8c8d', width=2),
                        fillcolor='rgba(127,140,141,0.15)',
                    ))
        return shapes_local, mammoth_count_local, wolf_count_local

    def _legend_shapes_annotations():
        legend_shapes_local = []
        legend_annotations_local = []
        box_x0 = 1.02
        box_x1 = 1.06
        start_y = 0.9
        step_y = 0.08
        items = ['Water'] + list(BIOME_COLORS.keys())
        colors = ['#001F5C'] + list(BIOME_COLORS.values())
        for i, (label, color) in enumerate(zip(items, colors)):
            y_center = start_y - i * step_y
            y0 = y_center - step_y * 0.35
            y1 = y_center + step_y * 0.35
            legend_shapes_local.append(dict(
                type='rect', xref='paper', yref='paper',
                x0=box_x0, x1=box_x1, y0=y0, y1=y1,
                line=dict(color='#000000', width=1), fillcolor=color,
            ))
            legend_annotations_local.append(dict(
                x=box_x1 + 0.01, y=y_center, xref='paper', yref='paper',
                text=label, showarrow=False, xanchor='left', yanchor='middle',
                font=dict(size=10, color='#111111')
            ))
        return legend_shapes_local, legend_annotations_local

    try:
        biome_trace = _build_biome_trace(plot_grid)
        placement_shapes = _placement_shapes(placements, plot_grid, day)
        fauna_shapes, mammoth_count, wolf_count = _fauna_shapes_and_counts(plot_grid, day)
        legend_shapes, legend_annotations = _legend_shapes_annotations()

        title_text = 'Eastern Siberia — Click to place fauna' if day == 0 else f'Eastern Siberia Biome Map — Day {day}'
        if placements and day == 0:
            title_text = f'Eastern Siberia — {len(placements)} placement(s)'

        fig = go.Figure(data=[biome_trace])
        all_shapes = placement_shapes + fauna_shapes + legend_shapes

        fig.update_layout(
            title=dict(text=title_text, x=0.5, font=dict(size=16)),
            xaxis=dict(showticklabels=False, showgrid=False, constrain='domain'),
            yaxis=dict(showticklabels=False, showgrid=False, scaleanchor='x'),
            shapes=all_shapes,
            annotations=legend_annotations,
            margin=dict(l=10, r=140, t=50, b=10),
            plot_bgcolor='#001F5C',
            paper_bgcolor='#f5f5f5',
        )
        return fig, mammoth_count, wolf_count
    except Exception:
        log.exception('Failed to build figure')
        # Return a minimal fallback figure and zero counts to avoid breaking callers
        return go.Figure(), 0, 0


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