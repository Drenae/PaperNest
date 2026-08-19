from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StagedFile:
    file_id: int
    path: Path
    category_key: str | None = None


@dataclass
class DashboardState:
    selected_category: dict | None = None
    categories: list[dict] = field(default_factory=list)
    available_categories: list[dict] = field(default_factory=list)
    staged_files: list[StagedFile] = field(default_factory=list)
    loading: bool = False
    progress: float = 0
    summary_text: str = ""
    keep_duplicates: bool = False

    @property
    def showing_detail(self) -> bool:
        return self.selected_category is not None

    def open_category(self, category: dict) -> None:
        self.selected_category = category

    def show_dashboard(self) -> None:
        self.selected_category = None

    def set_categories(
        self,
        categories: list[dict],
        available_categories: list[dict],
    ) -> None:
        self.categories = list(categories)
        self.available_categories = list(available_categories)

    def set_staged_files(self, files: list[StagedFile]) -> None:
        self.staged_files = list(files)

    def clear_staged_files(self) -> None:
        self.staged_files.clear()
        self.keep_duplicates = False
        self.progress = 0
        self.summary_text = ""
