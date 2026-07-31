from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft
from flet import IconData
from papernestextension import (
    PaperNestGlideRail,
    PaperNestGlideRailDestination,
)

from app.admin.admin_view import AdminView
from app.dashboard.dashboard_view import DashboardView
from app.important.important_view import ImportantView
from app.search.search_view import SearchView
from app.trash.trash_view import TrashView
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing


@dataclass(frozen=True)
class NavigationDestination:
    title: str
    icon: IconData
    selected_icon: IconData
    factory: Callable[[], ft.Control]


class MainWindow:
    """Fenêtre principale et coordination de la navigation PaperNest."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_index = 0
        self.current_view: ft.Control | None = None
        self.rail: PaperNestGlideRail | None = None

        self.content = ft.Container(
            expand=True,
            margin=ft.Margin.only(left=AppSizes.SIDEBAR_COMPACT_WIDTH),
            padding=AppSpacing.XL,
            bgcolor=AppColors.BACKGROUND,
        )

        self.main_navigation = [
            NavigationDestination(
                "Accueil",
                ft.Icons.DASHBOARD_OUTLINED,
                ft.Icons.DASHBOARD_ROUNDED,
                self.create_dashboard,
            ),
            NavigationDestination(
                "Recherche",
                ft.Icons.MANAGE_SEARCH_ROUNDED,
                ft.Icons.MANAGE_SEARCH_ROUNDED,
                self.create_search_view,
            ),
            NavigationDestination(
                "Documents importants",
                ft.Icons.STAR_OUTLINE_ROUNDED,
                ft.Icons.STAR_ROUNDED,
                self.create_important_view,
            ),
            NavigationDestination(
                "Corbeille",
                ft.Icons.DELETE_OUTLINE_ROUNDED,
                ft.Icons.DELETE_ROUNDED,
                self.create_trash_view,
            ),
        ]
        self.secondary_navigation = [
            NavigationDestination(
                "Administration",
                ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED,
                self.create_admin_view,
            ),
        ]

    @property
    def navigation_items(self) -> list[NavigationDestination]:
        return self.main_navigation + self.secondary_navigation

    def build(self) -> None:
        self.page.bgcolor = AppColors.BACKGROUND
        self.page.padding = 0
        self.page.spacing = 0

        self.rail = self._build_rail()
        self.page.add(
            ft.Stack(
                expand=True,
                controls=[
                    self.content,
                    ft.Container(
                        left=0,
                        top=0,
                        bottom=0,
                        content=self.rail,
                    ),
                ],
            )
        )
        self.navigate_to(0, force=True)

    def _build_rail(self) -> PaperNestGlideRail:
        return PaperNestGlideRail(
            expand=True,
            selected_index=self.selected_index,
            collapsed_width=AppSizes.SIDEBAR_COMPACT_WIDTH,
            expanded_width=AppSizes.SIDEBAR_WIDTH,
            animation_duration=220,
            padding=AppSpacing.MD,
            bgcolor=AppColors.PANEL_DARK,
            color=ft.Colors.GREY_500,
            selected_color=AppColors.TEXT,
            selected_bgcolor=AppColors.PRIMARY,
            selected_border_color=AppColors.PRIMARY_DARK,
            hover_color=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
            divider_color=ft.Colors.GREY_800,
            shadow_color=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
            border_radius=ft.BorderRadius.only(
                top_right=AppRadius.LG,
                bottom_right=AppRadius.LG,
            ),
            item_border_radius=AppRadius.MD,
            item_spacing=AppSpacing.XS,
            hover_scale=1.025,
            hover_animation_duration=140,
            brand_icon=ft.Image(
                src="branding/papernest_symbol.svg",
                width=40,
                height=40,
                fit=ft.BoxFit.CONTAIN,
            ),
            brand_title="PaperNest",
            brand_subtitle="Documents personnels",
            destinations=[
                self._build_rail_destination(item)
                for item in self.main_navigation
            ],
            secondary_destinations=[
                self._build_rail_destination(item)
                for item in self.secondary_navigation
            ],
            on_change=self.handle_navigation_select,
        )

    @staticmethod
    def _build_rail_destination(
        item: NavigationDestination,
    ) -> PaperNestGlideRailDestination:
        return PaperNestGlideRailDestination(
            label=item.title,
            tooltip=item.title,
            icon=item.icon,
            selected_icon=item.selected_icon,
        )

    def handle_navigation_select(self, event: ft.ControlEvent) -> None:
        try:
            index = int(event.data)
        except (TypeError, ValueError):
            return
        self.navigate_to(index, force=True)

    def navigate_to(self, index: int, *, force: bool = False) -> None:
        if index < 0 or index >= len(self.navigation_items):
            return
        if not force and index == self.selected_index and self.current_view is not None:
            return

        self.dispose_current_view()
        self.selected_index = index

        if self.rail is not None:
            self.rail.selected_index = index

        self.current_view = self.navigation_items[index].factory()
        self.content.content = self.current_view
        self.page.update()

    def refresh_current_view(self) -> None:
        self.navigate_to(self.selected_index, force=True)

    def dispose_current_view(self) -> None:
        if self.current_view is None:
            return
        for method_name in ("unsubscribe", "dispose"):
            method = getattr(self.current_view, method_name, None)
            if callable(method):
                method()
        self.current_view = None

    def create_dashboard(self) -> DashboardView:
        return DashboardView(page=self.page)

    def create_search_view(self) -> SearchView:
        return SearchView(page=self.page)

    def create_important_view(self) -> ImportantView:
        return ImportantView(self.page)

    def create_trash_view(self) -> TrashView:
        return TrashView(
            page=self.page,
            on_content_changed=self.handle_trash_content_changed,
        )

    def create_admin_view(self) -> AdminView:
        return AdminView(
            page=self.page,
            on_categories_changed=self.handle_categories_changed,
            on_restore_done=self.handle_restore_done,
        )

    def handle_restore_done(self) -> None:
        self.navigate_to(0, force=True)

    def handle_categories_changed(self) -> None:
        self.page.update()

    def handle_trash_content_changed(self) -> None:
        self.page.update()
