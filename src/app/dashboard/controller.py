from __future__ import annotations

from collections.abc import Callable

from app.dashboard.state import DashboardState


class DashboardController:
    def __init__(self, state: DashboardState, on_state_changed: Callable[[], None] | None = None) -> None:
        self.state = state
        self.on_state_changed = on_state_changed

    def open_category(self, category: dict) -> None:
        self.state.open_category(category)
        self._notify_state_changed()

    def show_dashboard(self) -> None:
        self.state.show_dashboard()
        self._notify_state_changed()

    def _notify_state_changed(self) -> None:
        if self.on_state_changed is not None:
            self.on_state_changed()