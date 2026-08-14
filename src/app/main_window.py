from __future__ import annotations

import flet as ft

from app.navigation.navigation import NavigationManager
from app.theme.tokens import AppColors, AppSizes, AppSpacing, AppTheme


class MainWindow:
    """Fenêtre principale et cycle de vie de la vue affichée."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_index = 0
        self.current_view: ft.Control | None = None

        self.content = ft.Container(
            expand=True,
            margin=ft.Margin.only(left=AppSizes.SIDEBAR_COMPACT_WIDTH),
            padding=AppSpacing.XL,
            bgcolor=AppColors.BACKGROUND,
            gradient=AppTheme.workspace_gradient(),
        )

        self.navigation = NavigationManager(
            page=page,
            on_select=self.handle_navigation_select,
            on_dashboard_detail_changed=self.handle_dashboard_detail_changed,
            on_categories_changed=self.handle_categories_changed,
            on_restore_done=self.handle_restore_done,
            on_trash_content_changed=self.handle_trash_content_changed,
        )

    def build(self) -> None:
        self.page.bgcolor = AppColors.BACKGROUND
        self.page.padding = 0
        self.page.spacing = 0

        rail = self.navigation.build(self.selected_index)
        self.page.add(
            ft.Stack(
                expand=True,
                controls=[
                    self.content,
                    ft.Container(
                        left=0,
                        top=0,
                        bottom=0,
                        content=rail,
                    ),
                ],
            )
        )
        self.navigate_to(0, force=True)

    def handle_navigation_select(self, index: int) -> None:
        self.navigate_to(index, force=True)

    def navigate_to(self, index: int, *, force: bool = False) -> None:
        if index < 0 or index >= len(self.navigation.destinations):
            return
        if not force and index == self.selected_index and self.current_view is not None:
            return

        self.dispose_current_view()
        self.selected_index = index
        self.navigation.select(index)

        self.current_view = self.navigation.create_view(index)
        self.content.content = self.current_view
        self.page.update()

    def refresh_current_view(self) -> None:
        self.navigate_to(self.selected_index, force=True)

    def handle_dashboard_detail_changed(self, showing_detail: bool) -> None:
        # Le détail d'un classeur est une sous-vue de l'accueil, pas la page
        # d'accueil elle-même. Désélectionner temporairement le rail permet à
        # un clic sur « Accueil » de déclencher de nouveau sa navigation.
        self.navigation.select(-1 if showing_detail else 0)

    def dispose_current_view(self) -> None:
        if self.current_view is None:
            return
        for method_name in ("unsubscribe", "dispose"):
            method = getattr(self.current_view, method_name, None)
            if callable(method):
                method()
        self.current_view = None

    def handle_restore_done(self) -> None:
        self.navigate_to(0, force=True)

    def handle_categories_changed(self) -> None:
        self.page.update()

    def handle_trash_content_changed(self) -> None:
        self.page.update()
