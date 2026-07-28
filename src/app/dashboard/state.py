from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DashboardState:
    selected_category: dict | None = None

    @property
    def showing_detail(self) -> bool:
        return self.selected_category is not None

    def open_category(self, category: dict) -> None:
        self.selected_category = category

    def show_dashboard(self) -> None:
        self.selected_category = None
