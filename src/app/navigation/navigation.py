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
from app.settings.settings_view import SettingsView
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing
from app.trash.trash_view import TrashView


@dataclass(frozen=True)
class NavigationDestination:
    title: str
    icon: IconData
    selected_icon: IconData
    factory: Callable[[], ft.Control]


class NavigationManager:
    """Définit les destinations et construit la navigation principale."""

    def __init__(
        self,
        *,
        page: ft.Page,
        on_select: Callable[[int], None],
        on_dashboard_detail_changed: Callable[[bool], None],
        on_categories_changed: Callable[[], None],
        on_restore_done: Callable[[], None],
        on_trash_content_changed: Callable[[], None],
    ) -> None:
        self.page = page
        self.on_select = on_select
        self.on_dashboard_detail_changed = on_dashboard_detail_changed
        self.on_categories_changed = on_categories_changed
        self.on_restore_done = on_restore_done
        self.on_trash_content_changed = on_trash_content_changed
        self.rail: PaperNestGlideRail | None = None

        self.main_destinations = [
            NavigationDestination(
                "Accueil",
                ft.Icons.DASHBOARD_OUTLINED,
                ft.Icons.DASHBOARD_ROUNDED,
                self._create_dashboard,
            ),
            NavigationDestination(
                "Recherche",
                ft.Icons.MANAGE_SEARCH_ROUNDED,
                ft.Icons.MANAGE_SEARCH_ROUNDED,
                self._create_search,
            ),
            NavigationDestination(
                "Documents importants",
                ft.Icons.STAR_OUTLINE_ROUNDED,
                ft.Icons.STAR_ROUNDED,
                self._create_important,
            ),
            NavigationDestination(
                "Corbeille",
                ft.Icons.DELETE_OUTLINE_ROUNDED,
                ft.Icons.DELETE_ROUNDED,
                self._create_trash,
            ),
        ]
        self.secondary_destinations = [
            NavigationDestination(
                "Paramètres",
                ft.Icons.SETTINGS_OUTLINED,
                ft.Icons.SETTINGS_ROUNDED,
                self._create_settings,
            ),
            NavigationDestination(
                "Administration",
                ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED,
                self._create_admin,
            )
        ]

    @property
    def destinations(self) -> list[NavigationDestination]:
        return self.main_destinations + self.secondary_destinations

    def build(self, selected_index: int = 0) -> PaperNestGlideRail:
        self.rail = PaperNestGlideRail(
            expand=True,
            selected_index=selected_index,
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
                width=30,
                height=30,
                fit=ft.BoxFit.CONTAIN,
            ),
            brand_title=ft.Text(
                "PaperNest",
                color=AppColors.TEXT_LIGHT,
                size=16,
                weight=ft.FontWeight.BOLD,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            brand_subtitle=ft.Text(
                "Documents personnels",
                color=AppColors.PRIMARY,
                size=11,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            destinations=[
                self._build_destination(item)
                for item in self.main_destinations
            ],
            secondary_destinations=[
                self._build_destination(item)
                for item in self.secondary_destinations
            ],
            on_change=self._handle_change,
        )
        return self.rail

    def select(self, index: int) -> None:
        if self.rail is not None:
            self.rail.selected_index = index

    def create_view(self, index: int) -> ft.Control:
        return self.destinations[index].factory()

    def _handle_change(self, event: ft.ControlEvent) -> None:
        try:
            index = int(event.data)
        except (TypeError, ValueError):
            return
        self.on_select(index)

    @staticmethod
    def _build_destination(
        item: NavigationDestination,
    ) -> PaperNestGlideRailDestination:
        return PaperNestGlideRailDestination(
            label=item.title,
            tooltip=item.title,
            icon=item.icon,
            selected_icon=item.selected_icon,
        )

    def _create_dashboard(self) -> DashboardView:
        return DashboardView(
            page=self.page,
            on_detail_changed=self.on_dashboard_detail_changed,
        )

    def _create_search(self) -> SearchView:
        return SearchView(page=self.page)

    def _create_important(self) -> ImportantView:
        return ImportantView(self.page)

    def _create_trash(self) -> TrashView:
        return TrashView(
            page=self.page,
            on_content_changed=self.on_trash_content_changed,
        )

    def _create_admin(self) -> AdminView:
        return AdminView(
            page=self.page,
            on_categories_changed=self.on_categories_changed,
            on_restore_done=self.on_restore_done,
        )

    def _create_settings(self) -> SettingsView:
        return SettingsView(page=self.page)


__all__ = ["NavigationDestination", "NavigationManager"]
