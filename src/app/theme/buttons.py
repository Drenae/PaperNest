from __future__ import annotations

from typing import Optional, Union

import flet as ft
from papernestextension import PaperNestButton, PaperNestButtonStyle

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSizes,
    AppSpacing,
    AppTheme,
)

ButtonContent = Union[str, ft.Control]


class AppButton(PaperNestButton):
    def __init__(
        self,
        text: ButtonContent | None = None,
        on_click=None,
        icon=None,
        bgcolor=AppColors.PRIMARY,
        color=AppColors.TEXT,
        gradient: ft.Gradient | None = None,
        width: Optional[float] = None,
        expand: bool = False,
        disabled: bool = False,
        loading: bool = False,
        loading_text: str | None = None,
        compact: bool = False,
        tooltip: str = "",
        **kwargs,
    ):
        if text is None and "content" in kwargs:
            text = kwargs.pop("content")
        if text is None:
            text = ""

        self._label = text
        self._source_icon = icon
        self._loading = loading
        self._compact = compact

        content = (
            text
            if isinstance(text, ft.Control)
            else ft.Text(
                text,
                size=13 if compact else 14,
                weight=ft.FontWeight.W_600,
                max_lines=1,
            )
        )

        style = kwargs.pop(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )

        super().__init__(
            content=content,
            icon=icon,
            on_click=on_click,
            bgcolor=bgcolor,
            color=color,
            gradient=gradient,
            width=width,
            height=(
                AppSizes.BUTTON_HEIGHT_COMPACT
                if compact
                else AppSizes.BUTTON_HEIGHT
            ),
            expand=expand,
            disabled=disabled,
            loading=loading,
            loading_text=loading_text,
            tooltip=tooltip,
            style=style,
            hover_scale=kwargs.pop("hover_scale", 1.02),
            hover_offset_y=kwargs.pop("hover_offset_y", -1),
            click_scale=kwargs.pop("click_scale", 0.97),
            animation_duration=kwargs.pop("animation_duration", 140),
            **kwargs,
        )


class PrimaryButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        compact = kwargs.get("compact", False)
        kwargs.setdefault("bgcolor", AppColors.PRIMARY)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.PRIMARY,
                AppColors.PRIMARY_DARK,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT)
        kwargs.setdefault(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                side=ft.BorderSide(2, AppColors.PRIMARY_DARK),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )
        super().__init__(text=text, **kwargs)


class SecondaryButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.PANEL)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.PANEL,
                AppColors.PANEL_STRONG,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT)
        super().__init__(text=text, **kwargs)


class SuccessButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        compact = kwargs.get("compact", False)
        kwargs.setdefault("bgcolor", AppColors.SUCCESS)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.SUCCESS,
                AppColors.SUCCESS_DARK,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT_LIGHT)
        kwargs.setdefault(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                side=ft.BorderSide(2, AppColors.SUCCESS_DARK),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )
        super().__init__(text=text, **kwargs)


class WarningButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        compact = kwargs.get("compact", False)
        kwargs.setdefault("bgcolor", AppColors.WARNING)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.WARNING,
                AppColors.WARNING_DARK,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT_LIGHT)
        kwargs.setdefault(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                side=ft.BorderSide(2, AppColors.WARNING_DARK),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )
        super().__init__(text=text, **kwargs)


class DangerButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        compact = kwargs.get("compact", False)
        kwargs.setdefault("bgcolor", AppColors.ERROR)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.ERROR,
                AppColors.ERROR_DARK,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT_LIGHT)
        kwargs.setdefault(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                side=ft.BorderSide(2, AppColors.ERROR_DARK),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )
        super().__init__(text=text, **kwargs)


class GhostButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", ft.Colors.TRANSPARENT)
        kwargs.setdefault("gradient", None)
        kwargs.setdefault("color", AppColors.TEXT)
        super().__init__(text=text, **kwargs)


class OutlineButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        compact = kwargs.get("compact", False)
        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault(
            "gradient",
            AppTheme.button_gradient(
                AppColors.SURFACE,
                AppColors.BACKGROUND,
            ),
        )
        kwargs.setdefault("color", AppColors.TEXT)
        kwargs.setdefault(
            "style",
            PaperNestButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(
                    horizontal=AppSpacing.MD if compact else AppSpacing.LG,
                    vertical=0,
                ),
                side=ft.BorderSide(1, AppColors.BORDER),
                mouse_cursor={
                    ft.ControlState.DISABLED: ft.MouseCursor.BASIC,
                    ft.ControlState.DEFAULT: ft.MouseCursor.CLICK,
                },
            ),
        )
        super().__init__(text=text, **kwargs)


class IconAction(ft.IconButton):
    def __init__(
        self,
        icon,
        tooltip: str = "",
        color=AppColors.TEXT,
        on_click=None,
        icon_color=None,
        bgcolor=ft.Colors.TRANSPARENT,
        disabled: bool = False,
        compact: bool = False,
        **kwargs,
    ):
        super().__init__(
            icon=icon,
            tooltip=tooltip,
            icon_color=(icon_color if icon_color is not None else color),
            bgcolor=bgcolor,
            on_click=on_click,
            disabled=disabled,
            width=34 if compact else 40,
            height=34 if compact else 40,
            style=ft.ButtonStyle(shape=ft.CircleBorder()),
            **kwargs,
        )


class MenuAction(ft.PopupMenuItem):
    def __init__(
        self,
        text: str,
        icon=None,
        on_click=None,
        color=AppColors.TEXT,
        disabled: bool = False,
        **kwargs,
    ):
        content_controls = []

        if icon is not None:
            content_controls.append(
                ft.Icon(icon, size=AppSizes.ICON_SM, color=color)
            )

        content_controls.append(ft.Text(text, size=14, color=color))

        super().__init__(
            content=ft.Row(
                spacing=AppSpacing.SM,
                controls=content_controls,
            ),
            on_click=on_click,
            disabled=disabled,
            **kwargs,
        )
