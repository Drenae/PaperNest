from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

import flet as ft

from app.theme.buttons import PrimaryButton
from app.theme.forms import PickerTextField


class BaseDatePickerField(ft.Column):
    """Champ date PaperNest construit autour du ``ft.DatePicker`` natif.

    Le contrôle visible reste un :class:`PickerTextField`. Le dialogue de
    sélection est le DatePicker Material natif de Flet, localisé en français.
    La valeur publique est toujours une date civile représentée par un
    ``datetime`` à minuit, sans conversion UTC susceptible de décaler le jour.
    """

    def __init__(
        self,
        *,
        page: ft.Page,
        label: str | ft.Control,
        value: str | date | datetime | None = None,
        icon=ft.Icons.EVENT_ROUNDED,
        first_date: date | datetime = datetime(1900, 1, 1),
        last_date: date | datetime = datetime(2100, 12, 31),
        current_date: date | datetime | None = None,
        on_change: Callable | None = None,
        on_clear: Callable | None = None,
        disabled: bool = False,
        read_only: bool = False,
        clear_button: bool = True,
        expand: bool | int | None = True,
        help_text: str | None = None,
        confirm_text: str = "Valider",
        cancel_text: str = "Annuler",
        **kwargs,
    ) -> None:
        self.app_page = page
        self._value = self._parse_value(value)
        self._external_on_change = on_change
        self._external_on_clear = on_clear
        self._disabled = bool(disabled)
        self._read_only = bool(read_only)

        first = self._parse_value(first_date) or datetime(1900, 1, 1)
        last = self._parse_value(last_date) or datetime(2100, 12, 31)
        today = self._parse_value(current_date) or datetime.now()

        self._picker = ft.DatePicker(
            value=self._value,
            first_date=first,
            last_date=last,
            current_date=datetime(today.year, today.month, today.day),
            locale=ft.Locale("fr", "FR"),
            date_picker_mode=ft.DatePickerMode.DAY,
            entry_mode=ft.DatePickerEntryMode.CALENDAR,
            help_text=help_text or str(label),
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            error_format_text="Format de date invalide",
            error_invalid_text="Date hors limites",
            field_hint_text="jj/mm/aaaa",
            field_label_text=str(label),
            barrier_color=ft.Colors.with_opacity(0.48, ft.Colors.BLACK),
            on_change=self._handle_picker_change,
        )

        self._picker_button = PrimaryButton(
            "Choisir",
            compact=True,
            disabled=self._disabled or self._read_only,
            on_click=self._open_picker,
        )
        self._field = PickerTextField(
            picker_button=self._picker_button,
            label=label,
            value=self._format_display(self._value),
            hint_text="JJ/MM/AAAA",
            prefix_icon=icon,
            clear_button=clear_button,
            disabled=self._disabled,
            read_only=True,
            width=float("inf"),
            on_clear=self._handle_clear,
        )

        super().__init__(
            controls=[self._field],
            spacing=0,
            tight=True,
            expand=expand,
            **kwargs,
        )

    @property
    def value(self) -> datetime | None:
        return self._value

    @value.setter
    def value(self, new_value: str | date | datetime | None) -> None:
        self._value = self._parse_value(new_value)
        if hasattr(self, "_picker"):
            self._picker.value = self._value
        if hasattr(self, "_field"):
            self._field.value = self._format_display(self._value)

    @property
    def iso_value(self) -> str:
        return self._value.date().isoformat() if self._value else ""

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = bool(value)
        if hasattr(self, "_field"):
            self._field.disabled = self._disabled
            self._picker_button.disabled = self._disabled or self._read_only

    def _open_picker(self, _event: ft.ControlEvent) -> None:
        if self._disabled or self._read_only:
            return

        self._picker.value = self._value
        self.app_page.show_dialog(self._picker)

    def _handle_picker_change(self, event: ft.ControlEvent) -> None:
        selected = self._date_from_event_data(event.data)
        if selected is None:
            selected = self._parse_value(self._picker.value)
        if selected is None:
            return

        self._value = selected
        self._picker.value = selected
        self._field.value = self._format_display(selected)

        if self._external_on_change is not None:
            self._external_on_change(event)

        self.app_page.update()

    def _handle_clear(self, event: ft.ControlEvent) -> None:
        self._value = None
        self._picker.value = None
        self._field.value = ""

        if self._external_on_clear is not None:
            self._external_on_clear(event)
        elif self._external_on_change is not None:
            self._external_on_change(event)

    @staticmethod
    def _format_display(value: datetime | None) -> str:
        return value.strftime("%d/%m/%Y") if value else ""

    @classmethod
    def _parse_value(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)

        text = str(value).strip()
        if not text:
            return None

        for parser in (
            lambda: datetime.fromisoformat(text),
            lambda: datetime.strptime(text, "%d/%m/%Y"),
            lambda: datetime.strptime(text, "%Y-%m-%d"),
        ):
            try:
                parsed = parser()
                return datetime(parsed.year, parsed.month, parsed.day)
            except ValueError:
                continue
        return None

    @classmethod
    def _date_from_event_data(cls, event_data: Any) -> datetime | None:
        """Convertit les données Flet en date civile sans décalage de jour."""
        if event_data is None:
            return None

        value = event_data
        if isinstance(value, dict):
            value = value.get("value") or value.get("date")
        elif isinstance(value, str):
            text = value.strip()
            if text.startswith("{"):
                try:
                    payload = json.loads(text)
                    value = payload.get("value") or payload.get("date") or text
                except (json.JSONDecodeError, TypeError):
                    value = text

        if isinstance(value, (datetime, date)):
            return cls._parse_value(value)

        if isinstance(value, (int, float)) or (
            isinstance(value, str)
            and re.fullmatch(r"-?\d+(?:\.\d+)?", value.strip())
        ):
            timestamp = float(value)
            if abs(timestamp) > 10_000_000_000:
                timestamp /= 1000.0
            local = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone()
            return datetime(local.year, local.month, local.day)

        return cls._parse_value(value)


__all__ = ["BaseDatePickerField"]
