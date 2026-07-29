from __future__ import annotations

from collections.abc import Callable

import flet as ft
from papernestextension.controls.material.papernest_color_picker import (
    PaperNestColorPicker,
)

from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


class BaseColorPicker(PaperNestColorPicker):
    """PaperNestColorPicker configuré avec le thème de PaperNest.

    La valeur publique est fournie par l'extension au format ``#RRGGBB``.
    Le callback applicatif reçoit directement cette valeur afin de conserver
    l'API pratique utilisée par les formulaires PaperNest.
    """

    def __init__(
        self,
        *,
        label: str | ft.Control | None = "Couleur",
        value: str | None = "#1E88E5",
        on_change: Callable[[str | None], None] | None = None,
        on_clear: Callable[[str | None], None] | None = None,
        clear_button: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        expand: bool | int | None = False,
        **kwargs,
    ) -> None:
        self._external_on_change = on_change
        self._external_on_clear = on_clear

        kwargs.setdefault("picker_title", "Choisir une couleur")
        kwargs.setdefault("cancel_text", "Annuler")
        kwargs.setdefault("confirm_text", "Appliquer")
        kwargs.setdefault("hint_text", "Sélectionner une couleur")
        kwargs.setdefault("prefix_icon", ft.Icons.PALETTE_OUTLINED)
        kwargs.setdefault("filled", True)
        kwargs.setdefault("fill_color", AppColors.SURFACE)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("focused_border_width", 2)
        kwargs.setdefault("border_color", AppColors.BORDER)
        kwargs.setdefault("focused_border_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("border_radius", AppRadius.MD)
        kwargs.setdefault(
            "content_padding",
            ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=0),
        )
        kwargs.setdefault(
            "text_style",
            ft.TextStyle(color=AppColors.TEXT, size=AppText.BODY),
        )
        kwargs.setdefault(
            "label_style",
            ft.TextStyle(color=AppColors.TEXT_SECONDARY, size=AppText.CAPTION),
        )
        kwargs.setdefault(
            "hint_style",
            ft.TextStyle(color=AppColors.TEXT_MUTED, size=AppText.BODY),
        )
        kwargs.setdefault("hover_color", ft.Colors.TRANSPARENT)

        super().__init__(
            label=label,
            value=value,
            clear_button=clear_button,
            disabled=disabled,
            read_only=read_only,
            expand=expand,
            on_change=self._handle_change,
            on_clear=self._handle_clear,
            **kwargs,
        )

    def _handle_change(self, event) -> None:
        if self._external_on_change is not None:
            self._external_on_change(self.value)

    def _handle_clear(self, event) -> None:
        if self._external_on_clear is not None:
            self._external_on_clear(self.value)
        elif self._external_on_change is not None:
            self._external_on_change(self.value)


__all__ = ["BaseColorPicker"]
