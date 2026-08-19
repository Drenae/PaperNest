from __future__ import annotations

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppSpacing,
)
from app.theme.badges import (
    BadgeVariant,
    CountBadge,
)
from app.theme.cards import (
    AppCard,
    AppSection,
    CardDensity,
    CardOrientation,
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

    def render(self, categories: list[dict]) -> None:
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

    def build_category_card(
        self,
        category: dict,
    ) -> AppCard:
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

        return AppCard(
            title=category_name,
            subtitle=subtitle,
            icon=icon,
            icon_color=icon_color,
            icon_bgcolor=icon_background,
            badge=CountBadge(
                document_count,
                variant=(
                    BadgeVariant.PRIMARY
                    if document_count > 0
                    else BadgeVariant.NEUTRAL
                ),
            ),
            orientation=CardOrientation.HORIZONTAL,
            density=CardDensity.NORMAL,
            shadow=False,
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
