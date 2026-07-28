from __future__ import annotations

from enum import Enum
from typing import Optional

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSizes,
    AppSpacing,
    AppText,
)
from app.theme.buttons import PrimaryButton, SecondaryButton


class EmptyStateVariant(str, Enum):
    NEUTRAL = "neutral"
    PRIMARY = "primary"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"


class EmptyState(ft.Container):
    """État vide, erreur ou information affiché dans les vues."""

    def __init__(
        self,
        *,
        icon,
        title: str,
        message: str = "",
        variant: EmptyStateVariant = EmptyStateVariant.NEUTRAL,
        action_text: Optional[str] = None,
        action_icon=None,
        on_action=None,
        secondary_action_text: Optional[str] = None,
        secondary_action_icon=None,
        on_secondary_action=None,
        compact: bool = False,
        padding: Optional[int] = None,
        bgcolor=None,
        bordered: bool = False,
        expand: Optional[bool] = None,
        **kwargs,
    ):
        palette = self._get_palette(variant)

        resolved_padding = padding or (
            AppSpacing.XL
            if compact
            else AppSpacing.XXXL
        )

        controls: list[ft.Control] = [
            ft.Container(
                width=56 if compact else 72,
                height=56 if compact else 72,
                alignment=ft.Alignment.CENTER,
                border_radius=AppRadius.XL,
                bgcolor=palette["icon_background"],
                content=ft.Icon(
                    icon,
                    size=AppSizes.ICON_LG if compact else 36,
                    color=palette["icon_color"],
                ),
            ),
            ft.Text(
                title,
                size=AppText.CARD_TITLE if compact else AppText.SECTION_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if message:
            controls.append(
                ft.Container(
                    content=ft.Text(
                        message,
                        size=AppText.CAPTION if compact else AppText.BODY,
                        color=AppColors.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )

        action_controls: list[ft.Control] = []

        if (
            secondary_action_text
            and on_secondary_action is not None
        ):
            action_controls.append(
                SecondaryButton(
                    text=secondary_action_text,
                    icon=secondary_action_icon,
                    on_click=on_secondary_action,
                    compact=compact,
                )
            )

        if action_text and on_action is not None:
            action_controls.append(
                PrimaryButton(
                    text=action_text,
                    icon=action_icon,
                    on_click=on_action,
                    compact=compact,
                )
            )

        if action_controls:
            controls.append(
                ft.Row(
                    spacing=AppSpacing.SM,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                    controls=action_controls,
                )
            )

        super().__init__(
            alignment=ft.Alignment.CENTER,
            padding=resolved_padding,
            bgcolor=bgcolor,
            border=(
                ft.Border.all(
                    1,
                    AppColors.BORDER_LIGHT,
                )
                if bordered
                else None
            ),
            border_radius=AppRadius.LG,
            expand=expand,
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.MD,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
            ),
            **kwargs,
        )

    @staticmethod
    def _get_palette(
        variant: EmptyStateVariant,
    ) -> dict[str, str]:
        palettes = {
            EmptyStateVariant.NEUTRAL: {
                "icon_background": AppColors.SURFACE_ALT,
                "icon_color": AppColors.TEXT_MUTED,
            },
            EmptyStateVariant.PRIMARY: {
                "icon_background": AppColors.PRIMARY_LIGHT,
                "icon_color": AppColors.PRIMARY_DARK,
            },
            EmptyStateVariant.ERROR: {
                "icon_background": AppColors.ERROR_LIGHT,
                "icon_color": AppColors.ERROR,
            },
            EmptyStateVariant.SUCCESS: {
                "icon_background": AppColors.SUCCESS_LIGHT,
                "icon_color": AppColors.SUCCESS,
            },
            EmptyStateVariant.WARNING: {
                "icon_background": AppColors.WARNING_LIGHT,
                "icon_color": AppColors.WARNING,
            },
        }

        return palettes[variant]

    @classmethod
    def empty(
        cls,
        *,
        title: str,
        message: str = "",
        icon=ft.Icons.INBOX_OUTLINED,
        action_text: Optional[str] = None,
        action_icon=ft.Icons.ADD_ROUNDED,
        on_action=None,
        **kwargs,
    ) -> "EmptyState":
        return cls(
            icon=icon,
            title=title,
            message=message,
            variant=EmptyStateVariant.NEUTRAL,
            action_text=action_text,
            action_icon=action_icon,
            on_action=on_action,
            **kwargs,
        )

    @classmethod
    def error(
        cls,
        *,
        message: str,
        title: str = "Une erreur est survenue",
        action_text: Optional[str] = None,
        action_icon=ft.Icons.REFRESH_ROUNDED,
        on_action=None,
        **kwargs,
    ) -> "EmptyState":
        return cls(
            icon=ft.Icons.ERROR_OUTLINE_ROUNDED,
            title=title,
            message=message,
            variant=EmptyStateVariant.ERROR,
            action_text=action_text,
            action_icon=action_icon,
            on_action=on_action,
            **kwargs,
        )

    @classmethod
    def success(
        cls,
        *,
        title: str,
        message: str = "",
        action_text: Optional[str] = None,
        action_icon=ft.Icons.CHECK_ROUNDED,
        on_action=None,
        **kwargs,
    ) -> "EmptyState":
        return cls(
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
            title=title,
            message=message,
            variant=EmptyStateVariant.SUCCESS,
            action_text=action_text,
            action_icon=action_icon,
            on_action=on_action,
            **kwargs,
        )

    @classmethod
    def warning(
        cls,
        *,
        title: str,
        message: str = "",
        action_text: Optional[str] = None,
        action_icon=ft.Icons.WARNING_AMBER_ROUNDED,
        on_action=None,
        **kwargs,
    ) -> "EmptyState":
        return cls(
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            title=title,
            message=message,
            variant=EmptyStateVariant.WARNING,
            action_text=action_text,
            action_icon=action_icon,
            on_action=on_action,
            **kwargs,
        )


class LoadingState(ft.Container):
    """État de chargement commun aux vues."""

    def __init__(
        self,
        message: str = "Chargement en cours…",
        *,
        compact: bool = False,
        padding: Optional[int] = None,
        expand: Optional[bool] = None,
        **kwargs,
    ):
        resolved_padding = padding or (
            AppSpacing.XL
            if compact
            else AppSpacing.XXXL
        )

        super().__init__(
            alignment=ft.Alignment.CENTER,
            padding=resolved_padding,
            expand=expand,
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.MD,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(
                        width=30 if compact else 38,
                        height=30 if compact else 38,
                        stroke_width=3,
                        color=AppColors.PRIMARY_DARK,
                    ),
                    ft.Text(
                        message,
                        size=AppText.CAPTION if compact else AppText.BODY,
                        color=AppColors.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
            **kwargs,
        )