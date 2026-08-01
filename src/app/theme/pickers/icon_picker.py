from __future__ import annotations

from collections.abc import Callable, Iterable

import flet as ft
from papernestextension import PaperNestIconPicker, PaperNestIconPickerOption

from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


class BaseIconPicker(PaperNestIconPicker):
    """PaperNestIconPicker configuré avec le thème de PaperNest."""

    def __init__(
        self,
        *,
        options: Iterable[PaperNestIconPickerOption],
        value: str | None = None,
        fallback_value: str = "FOLDER_ROUNDED",
        label: str | ft.Control | None = "Icône",
        on_change: Callable[[str | None], None] | None = None,
        disabled: bool = False,
        read_only: bool = False,
        expand: bool | int | None = False,
        **kwargs,
    ) -> None:
        self._external_on_change = on_change

        kwargs.setdefault("hint_text", "Sélectionner une icône")
        kwargs.setdefault("picker_title", "Choisir une icône")
        kwargs.setdefault(
            "picker_description",
            "Sélectionnez une icône pour le classeur.",
        )
        kwargs.setdefault("cancel_text", "Annuler")
        kwargs.setdefault("confirm_text", "Appliquer")
        kwargs.setdefault("suffix_icon", ft.Icons.CHEVRON_RIGHT_ROUNDED)
        kwargs.setdefault("icon_size", 24)
        kwargs.setdefault("option_icon_size", 24)
        kwargs.setdefault("color", AppColors.TEXT)
        kwargs.setdefault("icon_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("selected_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("selected_bgcolor", AppColors.PRIMARY_SOFT)
        kwargs.setdefault("selected_border_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("hover_color", ft.Colors.with_opacity(0.08, AppColors.PRIMARY))
        kwargs.setdefault("fill_color", AppColors.SURFACE)
        kwargs.setdefault("border_color", AppColors.BORDER)
        kwargs.setdefault("focused_border_color", AppColors.PRIMARY_DARK)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("focused_border_width", 2)
        kwargs.setdefault("border_radius", AppRadius.MD)
        kwargs.setdefault(
            "content_padding",
            ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=12),
        )
        kwargs.setdefault(
            "text_style",
            ft.TextStyle(
                color=AppColors.TEXT,
                size=AppText.BODY,
                weight=ft.FontWeight.W_600,
            ),
        )
        kwargs.setdefault(
            "label_style",
            ft.TextStyle(
                color=AppColors.TEXT_SECONDARY,
                size=AppText.CAPTION,
                weight=ft.FontWeight.W_600,
            ),
        )
        kwargs.setdefault(
            "hint_style",
            ft.TextStyle(color=AppColors.TEXT_MUTED, size=AppText.BODY),
        )
        kwargs.setdefault("dialog_width", 820)
        kwargs.setdefault("grid_max_extent", 190)
        kwargs.setdefault("grid_child_aspect_ratio", 2.5)
        kwargs.setdefault("grid_spacing", AppSpacing.SM)
        kwargs.setdefault("grid_run_spacing", AppSpacing.SM)
        kwargs.setdefault("option_border_radius", AppRadius.MD)
        kwargs.setdefault(
            "option_padding",
            ft.Padding.symmetric(
                horizontal=AppSpacing.MD,
                vertical=AppSpacing.SM,
            ),
        )

        super().__init__(
            options=list(options),
            value=value,
            fallback_value=fallback_value,
            label=label,
            disabled=disabled,
            read_only=read_only,
            expand=expand,
            on_change=self._handle_change,
            **kwargs,
        )

    def _handle_change(self, _event) -> None:
        if self._external_on_change is not None:
            self._external_on_change(self.value)


__all__ = ["BaseIconPicker", "PaperNestIconPickerOption"]
