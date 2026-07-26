import threading
import time
from typing import Dict, Any, Optional
from app.models.Plot.PlotGrid import PlotGrid
from app.setup.grid_initializer import GridInitializer


class SimulationRunner:
    """Background thread that owns the simulation state and advances days.

    - Holds a reference to the PlotGrid and GridInitializer externally (passed in).
    - Updates the PlotGrid inside its loop while holding a lock supplied by caller.
    """

    @staticmethod
    def _validate_instance(value: Any, expected_type: type, name: str) -> None:
        """Validate that a value is an instance of the expected type."""
        if not isinstance(value, expected_type):
            raise TypeError(f"{name} must be an instance of {expected_type.__name__}, got: {type(value).__name__}")

    @staticmethod
    def _validate_lock(value: Any, name: str) -> None:
        """Validate that a value behaves like a threading lock (duck-typed for Lock/RLock)."""
        if not (hasattr(value, 'acquire') and callable(value.acquire)
                and hasattr(value, 'release') and callable(value.release)):
            raise TypeError(f"{name} must be a lock-like object with acquire()/release() methods, got: {type(value).__name__}")

    @staticmethod
    def _validate_positive_number(value: Any, name: str) -> None:
        """Validate that a value is a positive number."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got: {type(value).__name__}")
        if value <= 0:
            raise ValueError(f"{name} must be positive, got: {value}")

    def __init__(self, plot_grid: PlotGrid, initializer: GridInitializer, lock: threading.Lock, interval_seconds: float = 1.0):
        self._validate_instance(plot_grid, PlotGrid, "plot_grid")
        self._validate_instance(initializer, GridInitializer, "initializer")
        self._validate_lock(lock, "lock")
        self._validate_positive_number(interval_seconds, "interval_seconds")

        self.plot_grid = plot_grid
        self.initializer = initializer
        self.lock = lock
        self.interval = interval_seconds
        self._thread = None
        self._stop_event = threading.Event()
        self._running = False
        self._state = {'running': False, 'day': 1, 'initialized': False}
        self._last_counts = (0, 0)

    def _apply_placements_unlocked(self, placements: Dict) -> None:
        """Apply a dict of placements to the plot grid.

        Caller is responsible for holding self.lock before calling this method.
        """
        if not placements:
            return
        for key, info in placements.items():
            r, c = map(int, key.split(','))
            plot = self.plot_grid.get_plot(r, c)
            if plot is None:
                continue
            if isinstance(info, dict):
                density = info.get('density', 2.0)
                species = info.get('species', 'mammoth')
            else:
                density = info
                species = 'mammoth'

            if species == 'mammoth':
                self.initializer.add_mammoth_to_plot(plot, population_per_km2=density)
            elif species == 'wolf':
                self.initializer.add_wolf_to_plot(plot, population_per_km2=density)
        self._state['initialized'] = True

    def start(self, placements=None):
        # Apply initial placements if provided
        if placements and not self._state['initialized']:
            acquired = self.lock.acquire(timeout=5.0)
            try:
                self._apply_placements_unlocked(placements)
            finally:
                try:
                    if self.lock.locked():
                        self.lock.release()
                except Exception:
                    pass

        if self._running:
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._running = True
        self._state['running'] = True
        self._thread.start()

    def stop(self):
        if not self._running:
            return
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._running = False
        self._state['running'] = False

    def _run_loop(self):
        while not self._stop_event.is_set():
            # advance one day while holding lock
            try:
                acquired = self.lock.acquire(timeout=5.0)
                if not acquired:
                    # could not acquire lock, skip this tick
                    time.sleep(self.interval)
                    continue
                self._state['day'] += 1
                self.plot_grid.update_all_plots(day=self._state['day'])
            finally:
                try:
                    if self.lock.locked():
                        self.lock.release()
                except Exception:
                    pass
            time.sleep(self.interval)

    def get_state(self) -> Dict[str, Any]:
        # Return a copy of the state and a small summary
        return dict(self._state)

    def is_running(self) -> bool:
        return self._running

    def apply_placements(self, placements):
        # Apply placements immediately under lock
        acquired = self.lock.acquire(timeout=5.0)
        try:
            self._apply_placements_unlocked(placements)
        finally:
            try:
                if self.lock.locked():
                    self.lock.release()
            except Exception:
                pass