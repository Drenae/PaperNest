from __future__ import annotations

from typing import Callable

import flet as ft
from papernestextension import PaperNestFilePicker

from app.theme.tokens import AppColors

FilePickerErrorHandler = Callable[[RuntimeError], None]


class BaseFilePicker(PaperNestFilePicker):
    """PaperNestFilePicker thématisé pour les parcours de l'application."""

    def __init__(self, **kwargs):
        kwargs.setdefault("icon_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("hover_border_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("hover_background_color", AppColors.PRIMARY_SOFT)
        kwargs.setdefault("drag_border_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("drag_background_color", AppColors.PRIMARY_SOFT)
        kwargs.setdefault("success_border_color", ft.Colors.GREEN_600)
        kwargs.setdefault("success_background_color", ft.Colors.GREEN_50)
        kwargs.setdefault("error_border_color", AppColors.ERROR)
        kwargs.setdefault("error_background_color", ft.Colors.RED_50)
        super().__init__(**kwargs)

    async def pick_files(
        self,
        *,
        on_error: FilePickerErrorHandler | None = None,
        **kwargs,
    ):
        try:
            return await super().pick_files(**kwargs)
        except RuntimeError as error:
            if on_error is not None:
                on_error(error)
            return []


__all__ = ["BaseFilePicker", "FilePickerErrorHandler"]
