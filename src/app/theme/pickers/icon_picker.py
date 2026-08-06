from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

import flet as ft

from app.theme.buttons import PrimaryButton, SecondaryButton
from app.theme.dialogs import AppDialog, DialogVariant
from app.theme.forms import PickerTextField, SearchTextField
from app.theme.tokens import AppColors, AppRadius, AppSpacing, AppText


@dataclass(frozen=True, slots=True)
class PaperNestIconPickerOption:
    """Option proposée par :class:`BaseIconPicker`.

    ``value`` est la valeur métier enregistrée par PaperNest. ``icon`` contient
    l'icône Flet affichée dans le champ et dans la galerie.
    """

    label: str
    value: str
    icon: Any = None


class BaseIconPicker(ft.Column):
    """Sélecteur d'icône PaperNest composé entièrement côté Python."""

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
        clear_button: bool = False,
        picker_title: str = "Choisir une icône",
        picker_description: str | None = "Sélectionnez une icône pour le classeur.",
        confirm_text: str = "Appliquer",
        cancel_text: str = "Annuler",
        dialog_width: float = 820,
        grid_max_extent: float = 190,
        grid_child_aspect_ratio: float = 2.5,
        grid_spacing: float = AppSpacing.SM,
        grid_run_spacing: float = AppSpacing.SM,
        option_icon_size: float = 24,
        **kwargs,
    ) -> None:
        self.options = [option for option in options if option.value]
        values = {option.value for option in self.options}
        self.fallback_value = (
            fallback_value
            if fallback_value in values
            else (self.options[0].value if self.options else None)
        )
        self._value = value if value in values else self.fallback_value
        self._temporary_value = self._value
        self._external_on_change = on_change
        self._disabled = bool(disabled)
        self._read_only = bool(read_only)
        self._picker_title = picker_title
        self._picker_description = picker_description
        self._confirm_text = confirm_text
        self._cancel_text = cancel_text
        self._dialog_width = dialog_width
        self._grid_max_extent = grid_max_extent
        self._grid_child_aspect_ratio = grid_child_aspect_ratio
        self._grid_spacing = grid_spacing
        self._grid_run_spacing = grid_run_spacing
        self._option_icon_size = option_icon_size
        self._dialog: AppDialog | None = None
        self._grid: ft.GridView | None = None
        self._search_field: SearchTextField | None = None
        self._filtered_options = list(self.options)

        self._preview_icon = ft.Icon(
            self._icon_for_option(self._selected_option),
            size=20,
            color=AppColors.PRIMARY_DARK,
        )
        self._picker_button = PrimaryButton(
            "Choisir",
            compact=True,
            disabled=self._disabled or self._read_only or not self.options,
            on_click=self._open_picker,
        )
        self._field = PickerTextField(
            picker_button=self._picker_button,
            label=label,
            value=self._selected_option.label if self._selected_option else "",
            hint_text="Sélectionner une icône",
            prefix_icon=self._preview_icon,
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
    def value(self) -> str | None:
        return self._value

    @value.setter
    def value(self, new_value: str | None) -> None:
        self._value = self._normalize_value(new_value)
        if hasattr(self, "_field"):
            self._sync_field()

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = bool(value)
        if hasattr(self, "_field"):
            self._field.disabled = self._disabled
            self._picker_button.disabled = (
                self._disabled or self._read_only or not self.options
            )

    @property
    def _selected_option(self) -> PaperNestIconPickerOption | None:
        return self._option_for_value(self._value)

    def _normalize_value(self, value: str | None) -> str | None:
        if self._option_for_value(value) is not None:
            return value
        return self.fallback_value

    def _option_for_value(self, value: str | None) -> PaperNestIconPickerOption | None:
        if value is None:
            return None
        return next((option for option in self.options if option.value == value), None)

    @staticmethod
    def _icon_for_option(option: PaperNestIconPickerOption | None):
        return (
            option.icon
            if option is not None and option.icon is not None
            else ft.Icons.EMOJI_SYMBOLS_ROUNDED
        )

    def _sync_field(self) -> None:
        option = self._selected_option
        self._field.value = option.label if option else ""
        self._preview_icon.icon = self._icon_for_option(option)

    def _open_picker(self, event: ft.ControlEvent) -> None:
        if self._disabled or self._read_only or not self.options:
            return

        page = event.page
        self._temporary_value = self._value
        self._filtered_options = list(self.options)
        self._search_field = SearchTextField(
            hint_text="Rechercher une icône…",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            on_search=lambda _event: self._filter_options(page),
            width=float("inf"),
        )
        self._grid = self._build_grid(page)

        controls: list[ft.Control] = []
        if self._picker_description:
            controls.append(
                ft.Text(
                    self._picker_description,
                    size=AppText.BODY,
                    color=AppColors.TEXT_SECONDARY,
                )
            )
        controls.extend([self._search_field, self._grid])

        self._dialog = AppDialog(
            title=self._picker_title,
            icon=ft.Icons.EMOJI_SYMBOLS_ROUNDED,
            variant=DialogVariant.PRIMARY,
            width=self._dialog_width,
            content=ft.Column(
                controls=controls,
                spacing=AppSpacing.MD,
                tight=True,
            ),
            actions=[
                SecondaryButton(
                    self._cancel_text,
                    icon=ft.Icons.CLOSE_ROUNDED,
                    on_click=lambda _event: self._close_dialog(page),
                ),
                PrimaryButton(
                    self._confirm_text,
                    icon=ft.Icons.CHECK_ROUNDED,
                    on_click=lambda _event: self._apply_value(page),
                ),
            ],
        )
        page.overlay.append(self._dialog)
        self._dialog.open = True
        page.update()

    def _filter_options(self, page: ft.Page) -> None:
        query = (
            (self._search_field.value or "").strip().casefold()
            if self._search_field is not None
            else ""
        )
        self._filtered_options = [
            option
            for option in self.options
            if not query
            or query in option.label.casefold()
            or query in option.value.casefold()
        ]
        self._refresh_grid(page)

    def _build_grid(self, page: ft.Page) -> ft.GridView:
        return ft.GridView(
            controls=[
                self._build_option_tile(option, page)
                for option in self._filtered_options
            ],
            max_extent=self._grid_max_extent,
            child_aspect_ratio=self._grid_child_aspect_ratio,
            spacing=self._grid_spacing,
            run_spacing=self._grid_run_spacing,
            height=390,
        )

    def _refresh_grid(self, page: ft.Page) -> None:
        if self._grid is not None:
            if self._filtered_options:
                self._grid.controls = [
                    self._build_option_tile(option, page)
                    for option in self._filtered_options
                ]
            else:
                self._grid.controls = [
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            "Aucune icône ne correspond à la recherche.",
                            color=AppColors.TEXT_MUTED,
                        ),
                    )
                ]
        page.update()

    def _build_option_tile(
        self,
        option: PaperNestIconPickerOption,
        page: ft.Page,
    ) -> ft.Container:
        selected = option.value == self._temporary_value
        return ft.Container(
            padding=ft.Padding.symmetric(
                horizontal=AppSpacing.MD,
                vertical=AppSpacing.SM,
            ),
            border_radius=AppRadius.MD,
            bgcolor=AppColors.PRIMARY_SOFT if selected else ft.Colors.TRANSPARENT,
            border=ft.Border.all(
                2 if selected else 1,
                AppColors.PRIMARY_DARK if selected else AppColors.BORDER,
            ),
            ink=True,
            on_click=lambda _event, selected_option=option: self._select_temporary(
                selected_option.value,
                page,
            ),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        self._icon_for_option(option),
                        size=self._option_icon_size,
                        color=AppColors.PRIMARY_DARK,
                    ),
                    ft.Text(
                        option.label,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        size=AppText.BODY,
                        weight=(
                            ft.FontWeight.W_600
                            if selected
                            else ft.FontWeight.NORMAL
                        ),
                        color=(
                            AppColors.PRIMARY_DARK
                            if selected
                            else AppColors.TEXT
                        ),
                        expand=True,
                    ),
                    *(
                        [
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE_ROUNDED,
                                size=18,
                                color=AppColors.PRIMARY_DARK,
                            )
                        ]
                        if selected
                        else []
                    ),
                ],
                spacing=AppSpacing.SM,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _select_temporary(self, value: str, page: ft.Page) -> None:
        self._temporary_value = value
        self._refresh_grid(page)

    def _apply_value(self, page: ft.Page) -> None:
        if self._temporary_value is None:
            return

        changed = self._temporary_value != self._value
        self._value = self._temporary_value
        self._sync_field()
        self._close_dialog(page, update=False)

        if changed and self._external_on_change is not None:
            self._external_on_change(self._value)

        page.update()

    def _handle_clear(self, _event: ft.ControlEvent) -> None:
        self._value = None
        self._temporary_value = self.fallback_value
        self._sync_field()
        if self._external_on_change is not None:
            self._external_on_change(self._value)

    def _close_dialog(self, page: ft.Page, *, update: bool = True) -> None:
        if self._dialog is not None:
            self._dialog.open = False
        if update:
            page.update()


__all__ = ["BaseIconPicker", "PaperNestIconPickerOption"]
