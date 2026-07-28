from __future__ import annotations

from typing import Optional, Union

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSizes,
    AppSpacing,
    AppTheme,
)


ButtonContent = Union[str, ft.Control]


class AppButton(ft.Button):
    def __init__(
        self,
        text: ButtonContent | None = None,
        on_click=None,
        icon=None,
        bgcolor=AppColors.PRIMARY,
        color=AppColors.TEXT,
        width: Optional[float] = None,
        expand: bool = False,
        disabled: bool = False,
        loading: bool = False,
        compact: bool = False,
        tooltip: str = "",
        **kwargs,
    ):
        if text is None and "content" in kwargs: text = kwargs.pop("content")
        if text is None: text = ""

        self._label = text
        self._source_icon = icon
        self._loading = loading
        self._compact = compact

        content = (text if isinstance(text, ft.Control) else ft.Text(text, size=13 if compact else 14, weight=ft.FontWeight.W_600, max_lines=1))
        style = kwargs.pop("style", ft.ButtonStyle(shape=AppTheme.button_shape(AppRadius.MD), padding=ft.Padding.symmetric(horizontal=(AppSpacing.MD if compact else AppSpacing.LG), vertical=0)))

        super().__init__(
            content=content,
            icon=None if loading else icon,
            on_click=on_click,
            bgcolor=bgcolor,
            color=color,
            width=width,
            height=(AppSizes.BUTTON_HEIGHT_COMPACT if compact else AppSizes.BUTTON_HEIGHT),
            expand=expand,
            disabled=disabled or loading,
            tooltip=tooltip,
            style=style,
            **kwargs,
        )

        if loading:
            self.content = ft.Row(spacing=AppSpacing.SM, alignment=ft.MainAxisAlignment.CENTER, controls=[ft.ProgressRing(width=16, height=16, stroke_width=2, color=color), content])


class PrimaryButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.PRIMARY)
        kwargs.setdefault("color", AppColors.TEXT)
        super().__init__(text=text, **kwargs)


class SecondaryButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.PANEL)
        kwargs.setdefault("color", AppColors.TEXT)
        super().__init__(text=text, **kwargs)


class SuccessButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.SUCCESS)
        kwargs.setdefault("color", AppColors.TEXT_LIGHT)
        super().__init__(text=text, **kwargs)


class DangerButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.ERROR)
        kwargs.setdefault("color", AppColors.TEXT_LIGHT)
        super().__init__(text=text, **kwargs)


class GhostButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", ft.Colors.TRANSPARENT)
        kwargs.setdefault("color", AppColors.TEXT)
        super().__init__(text=text, **kwargs)


class OutlineButton(AppButton):
    def __init__(self, text: ButtonContent, **kwargs):
        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault("color", AppColors.TEXT)
        kwargs.setdefault(
            "style",
            ft.ButtonStyle(
                shape=AppTheme.button_shape(AppRadius.MD),
                padding=ft.Padding.symmetric(horizontal=AppSpacing.LG, vertical=0),
                side=ft.BorderSide(1, AppColors.BORDER),
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
            content_controls.append(ft.Icon(icon, size=AppSizes.ICON_SM, color=color))

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