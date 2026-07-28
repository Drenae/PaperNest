from __future__ import annotations

import flet as ft

from app.theme.tokens import AppSpacing
from app.theme.cards import PageHeader
from app.search.components.search_panel import SearchPanel


class SearchView(ft.Column):
    """Vue dédiée à la recherche globale de documents."""

    def __init__(self, page: ft.Page):
        self.app_page = page
        self.search_panel = SearchPanel(page=page)

        super().__init__(
            expand=True,
            spacing=AppSpacing.LG,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                PageHeader(
                    icon=ft.Icons.MANAGE_SEARCH_ROUNDED,
                    title="Recherche",
                    subtitle=(
                        "Retrouvez vos documents dans tous les classeurs "
                        "avec des filtres précis."
                    ),
                    actions=[
                        self.search_panel.saved_search_filter,
                        self.search_panel.save_button,
                        self.search_panel.delete_saved_button,
                    ],
                ),
                self.search_panel,
            ],
        )

    def dispose(self) -> None:
        dispose = getattr(self.search_panel, "dispose", None)
        if callable(dispose):
            dispose()
