from __future__ import annotations

from datetime import datetime

import flet as ft
from papernestextension.controls.material.papernest_date_picker import PaperNestDatePicker

from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


class BaseDatePickerField(ft.Row):
    """Adaptateur PaperNest conservant une valeur publique au format ISO.

    Le rendu, l'ouverture du calendrier, le focus, le clavier et l'effacement
    sont gérés directement par ``PaperNestDatePicker``. L'adaptateur conserve
    temporairement l'interface historique utilisée par les formulaires de
    PaperNest pendant la migration progressive.
    """

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

        self.picker = PaperNestDatePicker(
            value=self._parse_value(value),
            first_date=first_date,
            last_date=last_date,
            current_date=self._parse_value(value) or datetime.now(),
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
            label_style=ft.TextStyle(
                color=AppColors.TEXT_SECONDARY,
                size=AppText.CAPTION,
            ),
            hover_color=ft.Colors.TRANSPARENT,
            content_padding=ft.Padding.symmetric(
                horizontal=AppSpacing.MD,
                vertical=0,
            ),
            expand=True,
            on_change=self._handle_change,
            on_cleared=self._handle_cleared,
        )

        super().__init__(
            expand=expand,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.picker],
            **kwargs,
        )

    @property
    def value(self) -> str:
        return self._format_value(self.picker.value)

    @value.setter
    def value(self, value: str | datetime | None) -> None:
        self.picker.value = self._parse_value(value)
        self._safe_update()

    @property
    def disabled(self) -> bool:
        return bool(self.picker.disabled)

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self.picker.disabled = bool(value)

    def open_picker(self, _event=None) -> None:
        if not self.disabled:
            self.app_page.run_task(self.picker.open)

    def clear(self, _event=None) -> None:
        if not self.disabled:
            self.app_page.run_task(self.picker.clear)

    def _handle_change(self, event) -> None:
        if self.external_on_change:
            self.external_on_change(event)

    def _handle_cleared(self, _event) -> None:
        # Flutter déclenche ensuite ``change`` avec une valeur vide. Le rappel
        # externe est donc envoyé une seule fois par ``_handle_change``.
        self._safe_update()

    def _safe_update(self) -> None:
        try:
            if self.page is not None:
                self.update()
        except RuntimeError:
            pass

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

    @staticmethod
    def _format_value(value: datetime | None) -> str:
        return value.date().isoformat() if value else ""
