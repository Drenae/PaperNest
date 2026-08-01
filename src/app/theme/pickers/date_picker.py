from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import flet as ft
from papernestextension import PaperNestDatePicker

from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


class BaseDatePickerField(PaperNestDatePicker):
    """PaperNestDatePicker configuré avec le thème de PaperNest."""

    def __init__(
        self,
        *,
        page: ft.Page,
        label: str | ft.Control,
        value: str | datetime | None = None,
        icon=ft.Icons.EVENT_ROUNDED,
        first_date: datetime = datetime(1900, 1, 1),
        last_date: datetime = datetime(2100, 12, 31),
        on_change: Callable | None = None,
        expand: bool | int | None = True,
        **kwargs,
    ) -> None:
        self.app_page = page
        self._external_on_change = on_change
        parsed_value = self._parse_value(value)

        kwargs.setdefault("current_date", parsed_value or datetime.now())
        kwargs.setdefault("hint_text", "JJ/MM/AAAA")
        kwargs.setdefault("clear_button", True)
        kwargs.setdefault("clear_tooltip", "Effacer la date")
        kwargs.setdefault("help_text", str(label))
        kwargs.setdefault("field_label_text", str(label))
        kwargs.setdefault("field_hint_text", "jj/mm/aaaa")
        kwargs.setdefault("confirm_text", "Valider")
        kwargs.setdefault("cancel_text", "Annuler")
        kwargs.setdefault("error_format_text", "Format de date invalide")
        kwargs.setdefault("error_invalid_text", "Date hors limites")
        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault("filled", True)
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
            value=parsed_value,
            first_date=first_date,
            last_date=last_date,
            label=label if isinstance(label, ft.Control) else ft.Text(label),
            prefix_icon=icon,
            expand=expand,
            on_change=self._handle_change,
            **kwargs,
        )

    @property
    def iso_value(self) -> str:
        return self.value.date().isoformat() if self.value else ""

    def _handle_change(self, event) -> None:
        if self._external_on_change is not None:
            self._external_on_change(event)

    @staticmethod
    def _parse_value(value: str | datetime | None) -> datetime | None:
        if isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        if value:
            try:
                parsed = datetime.fromisoformat(str(value))
                return datetime(parsed.year, parsed.month, parsed.day)
            except ValueError:
                return None
        return None


__all__ = ["BaseDatePickerField"]
