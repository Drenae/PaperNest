from __future__ import annotations

import flet as ft

from core.events.event_bus import (
    CategoryCreated,
    CategoryDeleted,
    CategoryRenamed,
    DocumentDeleted,
    DocumentImported,
    DocumentMoved,
    DocumentRestored,
    event_bus,
)
from app.theme.tokens import (
    AppColors,
    AppSpacing,
)
from repositories.category_repository import category_repository
from app.theme.cards import (
    AppSection,
    ListTileCard,
)
from app.theme.empty_state import EmptyState


def _resolve_category_color(value, fallback):
    color = str(value or "").strip()
    if color.startswith("#"):
        return color
    return getattr(ft.Colors, color, fallback)


class CabinetPanel(AppSection):
    """Grille responsive des classeurs du dashboard."""

    def __init__(
        self,
        on_category_click,
    ):
        self.on_category_click = on_category_click

        self._subscribed = False
        self._mounted = False

        self.category_grid = ft.ResponsiveRow(
            spacing=AppSpacing.MD,
            run_spacing=AppSpacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        super().__init__(
            title="Mes classeurs",
            icon=ft.Icons.FOLDER_COPY_ROUNDED,
            content=self.category_grid,
        )

        self.subscribe()

        self.refresh_grid_ui(
            update_page=False,
        )

    def did_mount(self) -> None:
        self._mounted = True

        self.subscribe()

        self.refresh_grid_ui(
            update_page=True,
        )

    def will_unmount(self) -> None:
        self._mounted = False
        self.unsubscribe()

    def dispose(self) -> None:
        self._mounted = False
        self.unsubscribe()

    def subscribe(self) -> None:
        if self._subscribed:
            return

        for event_type in (
            CategoryCreated,
            CategoryRenamed,
            CategoryDeleted,
            DocumentImported,
            DocumentMoved,
            DocumentDeleted,
            DocumentRestored,
        ):
            event_bus.subscribe(
                event_type,
                self._handle_event,
            )

        self._subscribed = True

    def unsubscribe(self) -> None:
        if not self._subscribed:
            return

        for event_type in (
            CategoryCreated,
            CategoryRenamed,
            CategoryDeleted,
            DocumentImported,
            DocumentMoved,
            DocumentDeleted,
            DocumentRestored,
        ):
            event_bus.unsubscribe(
                event_type,
                self._handle_event,
            )

        self._subscribed = False

    def _handle_event(
        self,
        _event,
    ) -> None:
        self.refresh_grid_ui(
            update_page=True,
        )

    def refresh_grid_ui(
        self,
        update_page: bool = True,
    ) -> None:
        categories = category_repository.list_roots()

        self.category_grid.controls.clear()

        if not categories:
            self.category_grid.controls.append(
                ft.Container(
                    col=12,
                    content=self.build_empty_state(),
                )
            )

        else:
            for category in categories:
                self.category_grid.controls.append(
                    ft.Container(
                        col={
                            "xs": 12,
                            "sm": 12,
                            "md": 6,
                            "lg": 4,
                            "xl": 3,
                        },
                        content=self.build_category_card(
                            category
                        ),
                    )
                )

        if update_page and self._mounted:
            self.update()

    def build_category_card(
        self,
        category: dict,
    ) -> ListTileCard:
        category_name = str(
            category.get("name")
            or category.get("label")
            or "Classeur"
        )

        icon_name = str(
            category.get("icon")
            or "FOLDER_ROUNDED"
        )

        icon = getattr(
            ft.Icons,
            icon_name,
            ft.Icons.FOLDER_ROUNDED,
        )

        color_name = str(
            category.get("color")
            or ""
        )

        icon_color = _resolve_category_color(
            color_name,
            AppColors.PRIMARY_DARK,
        )

        background_name = str(
            category.get("bg")
            or category.get("bgcolor")
            or ""
        )

        icon_background = _resolve_category_color(
            background_name,
            AppColors.PRIMARY_LIGHT,
        )

        document_count = int(
            category.get("document_count")
            or category.get("count")
            or category.get("value")
            or 0
        )

        subcategory_count = int(category.get("subcategory_count", 0))
        subtitle = None
        if subcategory_count > 0:
            subtitle = (
                f"{subcategory_count} sous-catégorie"
                f"{'s' if subcategory_count != 1 else ''}"
            )

        count_color = (
            AppColors.PRIMARY_DARK
            if document_count > 0
            else AppColors.TEXT_MUTED
        )
        count_background = (
            AppColors.PRIMARY_LIGHT
            if document_count > 0
            else AppColors.SURFACE_ALT
        )

        return ListTileCard(
            title=category_name,
            subtitle=subtitle,
            icon=icon,
            icon_color=icon_color,
            icon_bgcolor=icon_background,
            trailing=ft.CircleAvatar(
                content=ft.Text(
                    str(document_count),
                    color=count_color,
                    weight=ft.FontWeight.BOLD,
                ),
                color=count_color,
                bgcolor=count_background,
                radius=16,
            ),
            on_click=(
                lambda _event, item=category:
                self.on_category_click(item)
            ),
            tooltip=(
                f"Ouvrir le classeur {category_name}"
            ),
        )

    @staticmethod
    def build_empty_state() -> EmptyState:
        return EmptyState.empty(
            icon=ft.Icons.CREATE_NEW_FOLDER_OUTLINED,
            title="Aucun classeur disponible",
            message=(
                "Créez un classeur depuis la configuration "
                "pour commencer à organiser vos documents."
            ),
            compact=True,
            bordered=True,
        )
