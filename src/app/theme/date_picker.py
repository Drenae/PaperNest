from __future__ import annotations

from datetime import datetime

import flet as ft
from papernestextension import PaperNestDatePicker

from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


class _IsoDateTime(datetime):
    """Datetime natif fournissant aussi la représentation ISO attendue par PaperNest."""

    def strip(self) -> str:
        return self.date().isoformat()


class BaseDatePickerField(PaperNestDatePicker):
    """PaperNestDatePicker thématisé, sans conteneur intermédiaire."""

    def __init__(
        self,
        page: ft.Page,
        label: str,
        value: str | datetime | None = None,
        icon=ft.Icons.EVENT_ROUNDED,
        first_date: datetime = datetime(1900, 1, 1),
        last_date: datetime = datetime(2100, 12, 31),
        on_change=None,
        expand: bool = True,
        **kwargs,
    ):
        self.app_page = page
        self.external_on_change = on_change
        parsed_value = self._parse_value(value)
        super().__init__(
            value=parsed_value,
            first_date=first_date,
            last_date=last_date,
            current_date=parsed_value or datetime.now(),
            label=ft.Text(label),
            hint_text="JJ/MM/AAAA",
            prefix_icon=icon,
            clear_button=True,
            clear_tooltip="Effacer la date",
            help_text=label,
            field_label_text=label,
            field_hint_text="jj/mm/aaaa",
            confirm_text="Valider",
            cancel_text="Annuler",
            error_format_text="Format de date invalide",
            error_invalid_text="Date hors limites",
            bgcolor=AppColors.SURFACE,
            filled=True,
            border_width=1,
            focused_border_width=2,
            border_color=AppColors.BORDER,
            focused_border_color=AppColors.PRIMARY_DARK,
            border_radius=AppRadius.MD,
            text_style=ft.TextStyle(color=AppColors.TEXT, size=AppText.BODY),
            hint_style=ft.TextStyle(color=AppColors.TEXT_MUTED, size=AppText.BODY),
            label_style=ft.TextStyle(color=AppColors.TEXT_SECONDARY, size=AppText.CAPTION),
            hover_color=ft.Colors.TRANSPARENT,
            content_padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=0),
            expand=expand,
            on_change=self._handle_change,
            **kwargs,
        )

    @property
    def iso_value(self) -> str:
        return self.value.date().isoformat() if self.value else ""

    def _handle_change(self, event) -> None:
        if self.value and not isinstance(self.value, _IsoDateTime):
            self.value = self._parse_value(self.value)
        if self.external_on_change:
            self.external_on_change(event)

    @staticmethod
    def _parse_value(value: str | datetime | None) -> _IsoDateTime | None:
        if isinstance(value, datetime):
            return _IsoDateTime(value.year, value.month, value.day)
        if value:
            try:
                parsed = datetime.fromisoformat(str(value))
                return _IsoDateTime(parsed.year, parsed.month, parsed.day)
            except ValueError:
                return None
        return None
