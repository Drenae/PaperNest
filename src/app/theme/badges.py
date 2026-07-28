from __future__ import annotations

from enum import Enum

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSizes,
    AppSpacing,
    AppText,
)


class BadgeVariant(str, Enum):
    NEUTRAL = "neutral"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    DARK = "dark"


class BadgeSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"


class Badge(ft.Container):
    """Badge générique PaperNest."""

    def __init__(
        self,
        text: str,
        *,
        icon=None,
        variant: BadgeVariant = BadgeVariant.NEUTRAL,
        size: BadgeSize = BadgeSize.MEDIUM,
        bgcolor=None,
        color=None,
        border_color=None,
        tooltip: str = "",
        on_click=None,
        width: float | None = None,
        **kwargs,
    ):
        palette = self._get_palette(variant)

        resolved_bgcolor = bgcolor or palette["background"]
        resolved_color = color or palette["foreground"]
        resolved_border = border_color or palette["border"]

        is_small = size == BadgeSize.SMALL

        controls: list[ft.Control] = []

        if icon is not None:
            controls.append(
                ft.Icon(
                    icon,
                    size=14 if is_small else AppSizes.ICON_SM,
                    color=resolved_color,
                )
            )

        controls.append(
            ft.Text(
                text,
                size=11 if is_small else AppText.CAPTION,
                weight=ft.FontWeight.W_600,
                color=resolved_color,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )

        super().__init__(
            content=ft.Row(
                spacing=AppSpacing.XXS,
                tight=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
            ),
            padding=ft.Padding.symmetric(
                horizontal=(AppSpacing.SM if is_small else AppSpacing.MD),
                vertical=(AppSpacing.XXS if is_small else AppSpacing.XS),
            ),
            bgcolor=resolved_bgcolor,
            border=ft.Border.all(1, resolved_border),
            border_radius=AppRadius.PILL,
            tooltip=tooltip,
            on_click=on_click,
            ink=on_click is not None,
            width=width,
            **kwargs,
        )

    @staticmethod
    def _get_palette(variant: BadgeVariant) -> dict[str, str]:
        return {
            BadgeVariant.NEUTRAL: {
                "background": AppColors.SURFACE_ALT,
                "foreground": AppColors.TEXT_SECONDARY,
                "border": AppColors.BORDER_LIGHT,
            },
            BadgeVariant.PRIMARY: {
                "background": AppColors.PRIMARY_LIGHT,
                "foreground": AppColors.TEXT,
                "border": AppColors.PRIMARY,
            },
            BadgeVariant.SUCCESS: {
                "background": AppColors.SUCCESS_LIGHT,
                "foreground": AppColors.SUCCESS,
                "border": AppColors.SUCCESS,
            },
            BadgeVariant.WARNING: {
                "background": AppColors.WARNING_LIGHT,
                "foreground": AppColors.WARNING,
                "border": AppColors.WARNING,
            },
            BadgeVariant.DANGER: {
                "background": AppColors.ERROR_LIGHT,
                "foreground": AppColors.ERROR,
                "border": AppColors.ERROR,
            },
            BadgeVariant.INFO: {
                "background": AppColors.INFO_LIGHT,
                "foreground": AppColors.INFO,
                "border": AppColors.INFO,
            },
            BadgeVariant.DARK: {
                "background": AppColors.PANEL_DARK,
                "foreground": AppColors.TEXT_LIGHT,
                "border": AppColors.PANEL_DARK,
            },
        }[variant]


class StatusBadge(Badge):
    def __init__(
        self,
        text: str,
        *,
        variant: BadgeVariant = BadgeVariant.NEUTRAL,
        icon=None,
        **kwargs,
    ):
        super().__init__(text=text, icon=icon, variant=variant, **kwargs)


class CountBadge(Badge):
    def __init__(
        self,
        value: int | str,
        *,
        variant: BadgeVariant = BadgeVariant.PRIMARY,
        **kwargs,
    ):
        super().__init__(text=str(value), variant=variant, size=BadgeSize.SMALL, **kwargs)


class TagBadge(Badge):
    def __init__(
        self,
        text: str,
        *,
        on_click=None,
        on_remove=None,
        removable: bool = False,
        selected: bool = False,
        **kwargs,
    ):
        self.tag_text = text
        self.on_remove = on_remove

        variant = BadgeVariant.PRIMARY if selected else BadgeVariant.NEUTRAL

        if removable and on_remove is not None:
            palette = self._get_palette(variant)

            ft.Container.__init__(
                self,
                content=ft.Row(
                    spacing=AppSpacing.XXS,
                    tight=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            text,
                            size=AppText.CAPTION,
                            weight=ft.FontWeight.W_600,
                            color=AppColors.TEXT,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_size=14,
                            icon_color=AppColors.TEXT_MUTED,
                            tooltip=f"Supprimer le tag {text}",
                            width=22,
                            height=22,
                            padding=0,
                            on_click=on_remove,
                            style=ft.ButtonStyle(shape=ft.CircleBorder()),
                        ),
                    ],
                ),
                padding=ft.Padding.only(
                    left=AppSpacing.MD,
                    right=AppSpacing.XXS,
                    top=AppSpacing.XXS,
                    bottom=AppSpacing.XXS,
                ),
                bgcolor=palette["background"],
                border=ft.Border.all(1, palette["border"]),
                border_radius=AppRadius.PILL,
                on_click=on_click,
                ink=on_click is not None,
                **kwargs,
            )
            return

        super().__init__(
            text=text,
            icon=ft.Icons.SELL_OUTLINED,
            variant=variant,
            on_click=on_click,
            width=180,
            **kwargs,
        )