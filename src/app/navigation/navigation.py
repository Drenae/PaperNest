from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import flet as ft
from flet import IconData

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSizes,
    AppSpacing,
    AppText,
)


@dataclass(frozen=True)
class NavigationItem:
    title: str
    icon: IconData


class NavigationButton(ft.Container):
    def __init__(self, *, index: int, item: NavigationItem, selected: bool, compact: bool, on_select: Callable[[int], None]):
        self.navigation_index = index
        self.navigation_item = item
        self.compact = compact
        self.on_select = on_select

        self.icon_control = ft.Icon(
            item.icon,
            size=AppSizes.ICON_MD,
        )

        self.label_control = ft.Text(
            item.title,
            size=AppText.BODY,
            weight=ft.FontWeight.W_600,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            visible=not compact,
        )

        super().__init__(
            height=48,
            padding=ft.Padding.symmetric(
                horizontal=(
                    AppSpacing.MD
                    if not compact
                    else AppSpacing.SM
                ),
                vertical=AppSpacing.SM,
            ),
            border_radius=AppRadius.MD,
            alignment=ft.Alignment.CENTER,
            tooltip=item.title if compact else "",
            ink=True,
            on_click=self._handle_click,
            content=ft.Row(
                spacing=AppSpacing.MD,
                alignment=(
                    ft.MainAxisAlignment.START
                    if not compact
                    else ft.MainAxisAlignment.CENTER
                ),
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.icon_control,
                    self.label_control,
                ],
            ),
        )

        self.set_selected(selected)

    def _handle_click(self, _event) -> None:
        self.on_select(self.navigation_index)

    def set_selected(self, selected: bool) -> None:
        self.bgcolor = (
            AppColors.PRIMARY
            if selected
            else ft.Colors.TRANSPARENT
        )

        self.icon_control.color = (
            AppColors.TEXT
            if selected
            else ft.Colors.GREY_500
        )

        self.label_control.color = (
            AppColors.TEXT
            if selected
            else ft.Colors.GREY_300
        )

        self.border = (
            ft.Border.all(
                1,
                AppColors.PRIMARY_DARK,
            )
            if selected
            else None
        )


class SidebarNavigation(ft.Container):
    """Navigation latérale réutilisable de PaperNest."""

    def __init__(
        self,
        *,
        main_items: Iterable[NavigationItem],
        secondary_items: Iterable[NavigationItem],
        selected_index: int,
        on_select: Callable[[int], None],
        compact: bool = False,
    ):
        self.main_items = list(main_items)
        self.secondary_items = list(secondary_items)
        self.selected_index = selected_index
        self.on_select = on_select
        self.compact = compact

        self.navigation_buttons: list[NavigationButton] = []

        super().__init__(
            width=(
                AppSizes.SIDEBAR_COMPACT_WIDTH
                if compact
                else AppSizes.SIDEBAR_WIDTH
            ),
            bgcolor=AppColors.PANEL_DARK,
            padding=AppSpacing.MD,
            content=self._build_content(),
        )

    def _build_content(self) -> ft.Control:
        return ft.Column(
            expand=True,
            spacing=AppSpacing.MD,
            controls=[
                self._build_brand(),
                ft.Divider(
                    height=1,
                    color=ft.Colors.GREY_800,
                ),
                ft.Column(
                    spacing=AppSpacing.XS,
                    controls=self._build_group(
                        self.main_items,
                        start_index=0,
                    ),
                ),
                ft.Container(expand=True),
                ft.Divider(
                    height=1,
                    color=ft.Colors.GREY_800,
                ),
                ft.Column(
                    spacing=AppSpacing.XS,
                    controls=self._build_group(
                        self.secondary_items,
                        start_index=len(self.main_items),
                    ),
                ),
            ],
        )

    def _build_brand(self) -> ft.Container:
        brand_icon = ft.Container(
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
        )

        if self.compact:
            content: ft.Control = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[brand_icon],
            )

        else:
            content = ft.Row(
                spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    brand_icon,
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
            )

        return ft.Container(
            height=64,
            padding=ft.Padding.symmetric(
                horizontal=AppSpacing.XS,
            ),
            alignment=ft.Alignment.CENTER_LEFT,
            content=content,
        )

    def _build_group(
        self,
        items: list[NavigationItem],
        *,
        start_index: int,
    ) -> list[NavigationButton]:
        controls: list[NavigationButton] = []

        for offset, item in enumerate(items):
            index = start_index + offset

            button = NavigationButton(
                index=index,
                item=item,
                selected=index == self.selected_index,
                compact=self.compact,
                on_select=self.on_select,
            )

            controls.append(button)
            self.navigation_buttons.append(button)

        return controls

    def select(self, index: int) -> None:
        self.selected_index = index

        for button in self.navigation_buttons:
            button.set_selected(
                button.navigation_index == index
            )

        if self.page is not None:
            self.update()