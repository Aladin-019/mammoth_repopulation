"""
Dash application factory for the mammoth repopulation simulation.
Builds the layout and registers all callbacks, including the background
SimulationRunner integration for advancing days independently of the UI.
"""

import threading
from app.setup.grid_initializer import GridInitializer
from app.models.Plot.PlotGrid import PlotGrid
from app.simulation import SimulationRunner
from app.visualization import _build_figure, _build_stats, _build_placement_list

# Module-level lock to prevent overlapping interval callbacks
SIM_LOCK = threading.Lock()

# Simulation runner (set when app is created)
SIM_RUNNER = None


def create_dash_app(plot_grid: PlotGrid, initializer: GridInitializer):
    """Build and return the Dash application with interactive fauna placement."""
    from dash import Dash, html, dcc, Input, Output, State, no_update

    app = Dash(__name__)
    app.title = "Mammoth Repopulation Simulator"

    # Initial figure
    init_fig, _, _ = _build_figure(plot_grid)

    # Create background simulation runner
    global SIM_RUNNER
    SIM_RUNNER = SimulationRunner(plot_grid, initializer, SIM_LOCK, interval_seconds=1.0)

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
                    style={'marginTop': '5px', 'marginBottom': '10px', 'color': '#fff'},
                    value='mammoth',
                    inputStyle={'marginRight': '5px'},
                    labelStyle={'color': '#fff', 'fontWeight': 'bold'},
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
            dcc.Store(id='placements', data={}),
            dcc.Store(id='sim-state', data={'running': False, 'day': 1, 'initialized': False}),
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
        Output('sim-interval', 'n_intervals'),
        Output('start-btn', 'children'),
        Output('start-btn', 'style'),
        Output('placement-controls', 'style'),
        Input('start-btn', 'n_clicks'),
        State('sim-state', 'data'),
        State('placements', 'data'),
        prevent_initial_call=True,
    )
    def toggle_simulation(n_clicks, sim_state, placements):
        """Start or stop the background SimulationRunner and return updated UI outputs."""
        global SIM_RUNNER
        from dash import no_update

        # If no runner available, fall back to current behavior
        if SIM_RUNNER is None:
            return sim_state, True, 0, 'Start Simulation', {}, {}

        # Stop runner
        if sim_state.get('running'):
            SIM_RUNNER.stop()
            new_state = dict(sim_state)
            new_state['running'] = False
            return new_state, True, 0, 'Start Simulation', {'marginTop': '10px', 'padding': '12px 20px', 'fontSize': '14px',
                                                           'cursor': 'pointer', 'backgroundColor': '#27ae60',
                                                           'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                                                           'fontWeight': 'bold', 'width': '100%'}, {}

        # Start runner: apply placements if needed, then start
        if not sim_state.get('initialized') and placements:
            SIM_RUNNER.apply_placements(placements)

        SIM_RUNNER.start()
        new_state = dict(sim_state)
        new_state['running'] = True
        new_state['initialized'] = SIM_RUNNER.get_state().get('initialized', new_state.get('initialized', False))
        return new_state, False, 0, 'Stop Simulation', {'marginTop': '10px', 'padding': '12px 20px', 'fontSize': '14px',
                                                        'cursor': 'pointer', 'backgroundColor': '#c0392b',
                                                        'color': '#fff', 'border': 'none', 'borderRadius': '5px',
                                                        'fontWeight': 'bold', 'width': '100%'}, {'display': 'none'}

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
        # Read state from the SimulationRunner and render UI
        global SIM_RUNNER
        if SIM_RUNNER is None:
            return sim_state, no_update, no_update

        runner_state = SIM_RUNNER.get_state()
        # If not running, return explicit state
        if not runner_state.get('running'):
            return runner_state, no_update, no_update

        # Try to acquire lock for safe read of plot_grid
        acquired = SIM_LOCK.acquire(blocking=False)
        if not acquired:
            return runner_state, no_update, no_update

        try:
            day = runner_state.get('day', sim_state.get('day', 1))
            fig, mammoth_count, wolf_count = _build_figure(plot_grid, {}, day)
            stats_children = _build_stats(plot_grid, day, mammoth_count, wolf_count)
            return runner_state, fig, stats_children
        finally:
            SIM_LOCK.release()

    return app