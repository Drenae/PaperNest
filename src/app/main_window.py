from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft
from flet import IconData

from app.admin.admin_view import AdminView
from app.dashboard.dashboard_view import DashboardView
from app.important.important_view import ImportantView
from app.navigation.navigation import NavigationItem as SidebarNavigationItem, SidebarNavigation
from app.search.search_view import SearchView
from app.theme.forms import BaseFilePicker
from app.trash.trash_view import TrashView
from app.theme.tokens import AppColors, AppSpacing


@dataclass(frozen=True)
class NavigationDestination:
    title: str
    icon: IconData
    factory: Callable[[], ft.Control]


class MainWindow:
    COMPACT_BREAKPOINT = 900

    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_index = 0
        self.current_view: ft.Control | None = None
        self.is_compact = False
        self.sidebar: SidebarNavigation | None = None
        self.layout: ft.Row | None = None

        self.file_picker = BaseFilePicker()
        self.page.services.append(self.file_picker)
        self.content = ft.Container(expand=True, padding=AppSpacing.XL, bgcolor=AppColors.BACKGROUND)

        self.main_navigation = [
            NavigationDestination("Accueil", ft.Icons.DASHBOARD_OUTLINED, self.create_dashboard),
            NavigationDestination("Recherche", ft.Icons.MANAGE_SEARCH_ROUNDED, self.create_search_view),
            NavigationDestination("Documents importants", ft.Icons.STAR_OUTLINE_ROUNDED, self.create_important_view),
            NavigationDestination("Corbeille", ft.Icons.DELETE_OUTLINE_ROUNDED, self.create_trash_view),
        ]
        self.secondary_navigation = [
            NavigationDestination("Administration", ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, self.create_admin_view),
        ]

    @property
    def navigation_items(self) -> list[NavigationDestination]:
        return self.main_navigation + self.secondary_navigation

    def build(self) -> None:
        self.page.bgcolor = AppColors.BACKGROUND
        self.page.padding = 0
        self.page.spacing = 0
        self.is_compact = self._should_use_compact_sidebar()
        self.sidebar = self._build_sidebar()
        self.layout = ft.Row(expand=True, spacing=0, controls=[self.sidebar, self.content])
        self.page.on_resize = self.handle_page_resize
        self.page.add(self.layout)
        self.navigate_to(0, force=True)

    def _build_sidebar(self) -> SidebarNavigation:
        return SidebarNavigation(
            main_items=[SidebarNavigationItem(title=item.title, icon=item.icon) for item in self.main_navigation],
            secondary_items=[SidebarNavigationItem(title=item.title, icon=item.icon) for item in self.secondary_navigation],
            selected_index=self.selected_index,
            on_select=self.handle_navigation_select,
            compact=self.is_compact,
        )

    def _should_use_compact_sidebar(self) -> bool:
        return self.page.width is not None and self.page.width < self.COMPACT_BREAKPOINT

    def handle_navigation_select(self, index: int) -> None:
        self.navigate_to(index, force=True)

    def navigate_to(self, index: int, *, force: bool = False) -> None:
        if index < 0 or index >= len(self.navigation_items):
            return
        if not force and index == self.selected_index and self.current_view is not None:
            return
        self.dispose_current_view()
        self.selected_index = index
        if self.sidebar is not None:
            self.sidebar.select(index)
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

    def handle_page_resize(self, _event) -> None:
        compact = self._should_use_compact_sidebar()
        if compact == self.is_compact:
            return
        self.is_compact = compact
        if self.layout is None:
            return
        self.sidebar = self._build_sidebar()
        self.layout.controls[0] = self.sidebar
        self.page.update()

    def create_dashboard(self) -> DashboardView:
        return DashboardView(page=self.page, file_picker=self.file_picker)

    def create_search_view(self) -> SearchView:
        return SearchView(page=self.page)

    def create_important_view(self) -> ImportantView:
        return ImportantView(self.page)

    def create_trash_view(self) -> TrashView:
        return TrashView(page=self.page, on_content_changed=self.handle_trash_content_changed)

    def create_admin_view(self) -> AdminView:
        return AdminView(
            page=self.page,
            file_picker=self.file_picker,
            on_categories_changed=self.handle_categories_changed,
            on_restore_done=self.handle_restore_done,
        )

    def handle_restore_done(self) -> None:
        self.navigate_to(0, force=True)

    def handle_categories_changed(self) -> None:
        self.page.update()

    def handle_trash_content_changed(self) -> None:
        self.page.update()
