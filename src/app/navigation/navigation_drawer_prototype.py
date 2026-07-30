from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import flet as ft
from flet import IconData

from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText


@dataclass(frozen=True)
class DrawerItem:
    """Destination minimale utilisée par le prototype natif."""

    title: str
    icon: IconData
    selected_icon: IconData | None = None


class NativeNavigationDrawerPrototype:
    """Prototype non intégré du futur drawer PaperNest.

    Ce module n'altère pas la sidebar actuelle. Il sert uniquement à vérifier
    jusqu'où le contrôle Flet natif peut reproduire le rendu PaperNest avant
    toute décision de migration ou de fork.
    """

    def __init__(
        self,
        *,
        page: ft.Page,
        main_items: Iterable[DrawerItem],
        secondary_items: Iterable[DrawerItem],
        selected_index: int,
        on_select: Callable[[int], None],
    ) -> None:
        self.page = page
        self.main_items = list(main_items)
        self.secondary_items = list(secondary_items)
        self.selected_index = selected_index
        self.on_select = on_select
        self.drawer = self._build_drawer()

    def _build_brand(self) -> ft.Control:
        """En-tête provisoire en attendant le logo PNG validé."""

        return ft.Container(
            height=82,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD),
            alignment=ft.Alignment.CENTER_LEFT,
            content=ft.Row(
                spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=46,
                        height=46,
                        alignment=ft.Alignment.CENTER,
                        border_radius=AppRadius.LG,
                        bgcolor=AppColors.PRIMARY,
                        content=ft.Icon(
                            ft.Icons.FOLDER_COPY_ROUNDED,
                            size=26,
                            color=AppColors.TEXT,
                        ),
                    ),
                    ft.Column(
                        tight=True,
                        spacing=1,
                        controls=[
                            ft.Text(
                                "PaperNest",
                                size=19,
                                weight=ft.FontWeight.BOLD,
                                color=AppColors.TEXT_LIGHT,
                            ),
                            ft.Text(
                                "Documents personnels",
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                    ),
                ],
            ),
        )

    @staticmethod
    def _destination(item: DrawerItem) -> ft.NavigationDrawerDestination:
        return ft.NavigationDrawerDestination(
            icon=item.icon,
            selected_icon=item.selected_icon or item.icon,
            label=ft.Text(
                item.title,
                size=AppText.BODY,
                weight=ft.FontWeight.W_600,
                color=AppColors.TEXT_LIGHT,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        )

    def _build_drawer(self) -> ft.NavigationDrawer:
        controls: list[ft.Control] = [
            self._build_brand(),
            ft.Divider(height=1, color=ft.Colors.GREY_800),
        ]

        controls.extend(self._destination(item) for item in self.main_items)

        if self.secondary_items:
            controls.extend(
                [
                    ft.Container(height=AppSpacing.MD),
                    ft.Divider(height=1, color=ft.Colors.GREY_800),
                ]
            )
            controls.extend(self._destination(item) for item in self.secondary_items)

        return ft.NavigationDrawer(
            controls=controls,
            selected_index=self.selected_index,
            width=AppSizes.SIDEBAR_WIDTH,
            bgcolor=AppColors.PANEL_DARK,
            elevation=8,
            shadow_color=ft.Colors.BLACK54,
            tile_padding=ft.Padding.symmetric(horizontal=AppSpacing.MD),
            indicator_color=AppColors.PRIMARY,
            indicator_shape=ft.RoundedRectangleBorder(radius=AppRadius.MD),
            on_change=self._handle_change,
            on_dismiss=self._handle_dismiss,
        )

    def _handle_change(self, event: ft.ControlEvent) -> None:
        index = int(event.data)
        self.selected_index = index
        self.on_select(index)
        self.close()

    def _handle_dismiss(self, _event: ft.ControlEvent) -> None:
        self.drawer.selected_index = self.selected_index

    def install(self) -> None:
        """Installe le prototype comme drawer de la page sans l'ouvrir."""

        self.page.drawer = self.drawer

    def open(self) -> None:
        """Ouvre le drawer natif installé sur la page."""

        if self.page.drawer is not self.drawer:
            self.install()
        self.page.show_drawer()

    def close(self) -> None:
        """Ferme le drawer natif."""

        self.page.close_drawer()

    def select(self, index: int) -> None:
        """Synchronise la destination sélectionnée depuis la navigation métier."""

        self.selected_index = index
        self.drawer.selected_index = index
        if self.drawer.page is not None:
            self.drawer.update()
