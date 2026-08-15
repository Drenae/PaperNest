from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import flet as ft
from flet_color_pickers import MaterialPicker

from app.theme.buttons import PrimaryButton
from app.theme.dialogs import FormDialog
from app.theme.forms import PickerTextField
from app.theme.tokens import AppSpacing


_HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-F]{6}$")
_DEFAULT_COLOR = "#1E88E5"


class BaseColorPicker(PickerTextField):
    """Champ couleur PaperNest composé entièrement côté Python.

    Le champ est un :class:`PickerTextField`. Son bouton ouvre un
    :class:`AppDialog` contenant directement le ``MaterialPicker`` fourni par
    ``flet-color-pickers``. La couleur choisie reste temporaire jusqu'à la
    validation explicite du dialogue.
    """

    def __init__(
        self,
        *,
        label: str | ft.Control | None = "Couleur",
        value: str | None = _DEFAULT_COLOR,
        on_change: Callable[[str | None], None] | None = None,
        on_clear: Callable[[str | None], None] | None = None,
        clear_button: bool = False,
        disabled: bool = False,
        read_only: bool = False,
        expand: bool | int | None = False,
        picker_title: str = "Choisir une couleur",
        confirm_text: str = "Appliquer",
        cancel_text: str = "Annuler",
        enable_label: bool = False,
        portrait_only: bool = False,
        **kwargs,
    ) -> None:
        self._external_on_change = on_change
        self._external_on_clear = on_clear
        self._picker_title = picker_title
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._enable_label = enable_label
        self._portrait_only = portrait_only
        self._temporary_value = self.normalize_value(value)
        self._dialog: AppDialog | None = None

        self._swatch = ft.Icon(
            ft.Icons.CIRCLE,
            size=35,
            color=self._temporary_value,
        )
        self._picker_button = PrimaryButton(
            "Choisir la couleur",
            compact=True,
            disabled=disabled or read_only,
            on_click=self._open_picker,
        )

        kwargs.setdefault("hint_text", "Sélectionner une couleur")
        kwargs.setdefault("prefix_icon", self._swatch)
        kwargs.setdefault("width", float("inf"))

        super().__init__(
            picker_button=self._picker_button,
            label=label,
            value=self._temporary_value,
            clear_button=clear_button,
            disabled=disabled,
            read_only=True,
            expand=expand,
            on_clear=self._handle_clear,
            **kwargs,
        )

    @staticmethod
    def _normalize_hex(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        if not text or text.lower() == "none":
            return None

        if not text.startswith("#"):
            return text

        digits = text[1:]
        if re.fullmatch(r"[0-9a-fA-F]{3}", digits):
            digits = "".join(character * 2 for character in digits)
        elif re.fullmatch(r"[0-9a-fA-F]{8}", digits):
            # Flet peut sérialiser une couleur sous la forme #AARRGGBB.
            # PaperNest conserve volontairement uniquement la partie RGB.
            digits = digits[2:]
        elif not re.fullmatch(r"[0-9a-fA-F]{6}", digits):
            return text

        return f"#{digits.upper()}"

    @classmethod
    def normalize_value(
        cls,
        value: Any,
        default: str = _DEFAULT_COLOR,
    ) -> str:
        """Retourne une valeur publique stricte au format ``#RRGGBB``."""
        normalized_default = cls._normalize_hex(default)
        if not normalized_default or not _HEX_COLOR_PATTERN.fullmatch(
            normalized_default.upper()
        ):
            normalized_default = _DEFAULT_COLOR

        normalized = cls._normalize_hex(value)
        if not normalized:
            return normalized_default

        normalized = normalized.upper()
        if not _HEX_COLOR_PATTERN.fullmatch(normalized):
            return normalized_default

        return normalized

    def before_update(self) -> None:
        super().before_update()
        self._picker_button.disabled = bool(self.disabled)

        if self.value:
            normalized = self.normalize_value(self.value)
            if normalized != self.value:
                self.value = normalized
            self._swatch.color = normalized
        else:
            self._swatch.color = ft.Colors.TRANSPARENT

    def _open_picker(self, event: ft.ControlEvent) -> None:
        if self.disabled:
            return

        page = event.page
        self._temporary_value = self.normalize_value(self.value)

        picker = MaterialPicker(
            color=self._temporary_value,
            enable_label=self._enable_label,
            portrait_only=self._portrait_only,
            on_color_change=self._handle_temporary_change,
        )

        self._dialog = FormDialog(
            title=self._picker_title,
            icon=ft.Icons.PALETTE_OUTLINED,
            width=560,
            form=ft.Container(
                width=520,
                padding=ft.Padding.symmetric(vertical=AppSpacing.SM),
                content=picker,
            ),
            on_submit=lambda _event: self._apply_value(page),
            on_cancel=lambda _event: self._close_dialog(page),
            submit_text=self._confirm_text,
            cancel_text=self._cancel_text,
            submit_icon=ft.Icons.CHECK_ROUNDED,
        )
        page.overlay.append(self._dialog)
        self._dialog.open = True
        page.update()

    def _handle_temporary_change(self, event: ft.ControlEvent) -> None:
        self._temporary_value = self.normalize_value(event.data)

    def _apply_value(self, page: ft.Page) -> None:
        self.value = self.normalize_value(self._temporary_value)
        self._swatch.color = self.value
        self._close_dialog(page, update=False)

        if self._external_on_change is not None:
            self._external_on_change(self.value)

        page.update()

    def _handle_clear(self, _event: ft.ControlEvent) -> None:
        self.value = None
        self._temporary_value = _DEFAULT_COLOR
        self._swatch.color = ft.Colors.TRANSPARENT

        if self._external_on_clear is not None:
            self._external_on_clear(self.value)
        elif self._external_on_change is not None:
            self._external_on_change(self.value)

    def _close_dialog(self, page: ft.Page, *, update: bool = True) -> None:
        if self._dialog is not None:
            self._dialog.open = False
        if update:
            page.update()


__all__ = ["BaseColorPicker"]
