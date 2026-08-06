from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any

import flet as ft

from app.theme.buttons import PrimaryButton
from app.theme.forms import PickerTextField
from app.theme.tokens import AppColors, AppRadius, AppText


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

        self._apply_picker_theme(page)

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
        # Les données brutes sont prioritaires : elles permettent de restaurer
        # la date civile avant qu'une conversion UTC ne décale le calendrier.
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

    @staticmethod
    def _civil_datetime(value: datetime) -> datetime:
        """Convertit d'abord vers l'heure locale, puis extrait la date civile."""
        if value.tzinfo is not None:
            value = value.astimezone()
        return datetime(value.year, value.month, value.day)

    @classmethod
    def _parse_value(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return cls._civil_datetime(value)
        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)

        text = str(value).strip()
        if not text:
            return None

        # Une date ISO sans heure est déjà une date civile et ne doit subir
        # aucune conversion de fuseau.
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            try:
                return datetime.strptime(text, "%Y-%m-%d")
            except ValueError:
                return None

        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return cls._civil_datetime(parsed)
        except ValueError:
            pass

        try:
            parsed = datetime.strptime(text, "%d/%m/%Y")
            return datetime(parsed.year, parsed.month, parsed.day)
        except ValueError:
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

    @staticmethod
    def _apply_picker_theme(page: ft.Page) -> None:
        """Applique le thème PaperNest au DatePicker natif de la page."""
        if page.theme is None:
            page.theme = ft.Theme()

        page.theme.date_picker_theme = ft.DatePickerTheme(
            bgcolor=AppColors.SURFACE,
            header_bgcolor=ft.Colors.GREY_900,
            header_foreground_color=AppColors.TEXT_LIGHT,
            divider_color=AppColors.BORDER,
            shadow_color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
            elevation=8,
            shape=ft.RoundedRectangleBorder(radius=AppRadius.XL),
            day_foreground_color={
                ft.ControlState.SELECTED: AppColors.TEXT,
                ft.ControlState.DEFAULT: AppColors.TEXT,
            },
            day_bgcolor={
                ft.ControlState.SELECTED: AppColors.PRIMARY,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            today_foreground_color={
                ft.ControlState.SELECTED: AppColors.TEXT,
                ft.ControlState.DEFAULT: AppColors.PRIMARY_DARK,
            },
            today_bgcolor={
                ft.ControlState.SELECTED: AppColors.PRIMARY,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            today_border_side=ft.BorderSide(1, AppColors.PRIMARY_DARK),
            year_foreground_color={
                ft.ControlState.SELECTED: AppColors.TEXT,
                ft.ControlState.DEFAULT: AppColors.TEXT,
            },
            year_bgcolor={
                ft.ControlState.SELECTED: AppColors.PRIMARY,
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
            },
            weekday_text_style=ft.TextStyle(
                size=AppText.CAPTION,
                weight=ft.FontWeight.W_600,
                color=AppColors.TEXT_SECONDARY,
            ),
            confirm_button_style=ft.ButtonStyle(
                color=AppColors.PRIMARY_DARK,
            ),
            cancel_button_style=ft.ButtonStyle(
                color=AppColors.TEXT_SECONDARY,
            ),
        )


__all__ = ["BaseDatePickerField"]
