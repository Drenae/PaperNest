from __future__ import annotations

from typing import Callable, Iterable, Optional, Union

import flet as ft
from papernestextension.controls.material.papernest_dropdown import (
    PaperNestDropdown,
    PaperNestDropdownOption,
)
from papernestextension.controls.material.papernest_textfield import (
    KeyboardType,
    PaperNestTextField,
)

from app.theme.buttons import PrimaryButton, SecondaryButton
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText

LabelValue = Union[str, ft.Control, None]


def _label_control(value: LabelValue):
    if value is None or value == "":
        return None
    return value if isinstance(value, ft.Control) else ft.Text(str(value))


class _InputMixin:
    def _apply_common_input_style(self, compact: bool = False):
        self.bgcolor = AppColors.SURFACE
        self.filled = True
        self.border_width = 1
        self.focused_border_width = 2
        self.border_color = AppColors.BORDER
        self.focused_border_color = AppColors.PRIMARY_DARK
        self.border_radius = AppRadius.MD
        self.height = AppSizes.FIELD_HEIGHT_COMPACT if compact else AppSizes.FIELD_HEIGHT
        self.text_style = ft.TextStyle(color=AppColors.TEXT, size=AppText.BODY)
        self.hint_style = ft.TextStyle(color=AppColors.TEXT_MUTED, size=AppText.BODY)
        self.label_style = ft.TextStyle(color=AppColors.TEXT_SECONDARY, size=AppText.CAPTION)
        self.hover_color = ft.Colors.TRANSPARENT
        self.content_padding = ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=0)


class BaseTextField(_InputMixin, PaperNestTextField):
    def __init__(
        self,
        label: LabelValue = None,
        icon=None,
        compact: bool = False,
        expand: Optional[bool] = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = _label_control(label)
        if icon is not None:
            self.prefix_icon = icon
        self.expand = expand
        self._apply_common_input_style(compact=compact)
        self.height = None


class SearchTextField(BaseTextField):
    def __init__(
        self,
        hint_text: str = "Rechercher…",
        on_search=None,
        debounce_ms: int = 350,
        **kwargs,
    ):
        kwargs.setdefault("hint_text", hint_text)
        kwargs.setdefault("search_mode", True)
        kwargs.setdefault("clear_button", True)
        kwargs.setdefault("debounce_ms", debounce_ms)
        kwargs.setdefault("select_all_on_focus", True)
        kwargs.setdefault("on_search", on_search)
        kwargs.setdefault("label", None)
        super().__init__(**kwargs)


class PasswordTextField(BaseTextField):
    def __init__(self, label: LabelValue = "Mot de passe", **kwargs):
        kwargs.setdefault("password", True)
        kwargs.setdefault("can_reveal_password", True)
        kwargs.setdefault("icon", ft.Icons.LOCK_OUTLINE_ROUNDED)
        super().__init__(label=label, **kwargs)


class BaseTextArea(BaseTextField):
    def __init__(
        self,
        label: LabelValue = None,
        min_lines: int = 3,
        max_lines: int = 6,
        **kwargs,
    ):
        kwargs.setdefault("multiline", True)
        kwargs.setdefault("min_lines", min_lines)
        kwargs.setdefault("max_lines", max_lines)
        kwargs.setdefault("height", None)
        super().__init__(label=label, **kwargs)
        self.height = None
        self.content_padding = AppSpacing.MD


class BaseNumberField(BaseTextField):
    def __init__(self, label: LabelValue = None, **kwargs):
        kwargs.setdefault("keyboard_type", KeyboardType.NUMBER)
        super().__init__(label=label, **kwargs)


class BaseDropDown(_InputMixin, PaperNestDropdown):
    def __init__(
        self,
        label: LabelValue = None,
        icon=None,
        leading_icon=None,
        compact: bool = False,
        expand: Optional[bool | int] = None,
        **kwargs,
    ):
        on_select = kwargs.pop("on_select", None)
        if on_select is not None and "on_change" not in kwargs:
            kwargs["on_change"] = on_select
        dense = kwargs.pop("dense", None)
        if dense is not None:
            compact = bool(dense)
        super().__init__(**kwargs)
        self.label = _label_control(label)
        field_icon = icon if icon is not None else leading_icon
        if field_icon is not None:
            self.prefix_icon = field_icon
        if expand is not None:
            self.expand = expand
        self._apply_common_input_style(compact=compact)
        self.menu_background_color = AppColors.SURFACE
        self.menu_border_color = AppColors.BORDER
        self.menu_border_width = 1
        self.menu_border_radius = AppRadius.MD
        self.menu_padding = ft.Padding.symmetric(horizontal=5, vertical=8)
        self.menu_item_padding = ft.Padding.symmetric(
            horizontal=AppSpacing.MD,
            vertical=AppSpacing.SM,
        )


class SearchDropDown(BaseDropDown):
    """Dropdown spécialisé pour les filtres de recherche."""

    def __init__(self, **kwargs):
        kwargs.setdefault("clear_button", True)
        kwargs.setdefault("clear_button_tooltip", "Réinitialiser le filtre")
        super().__init__(**kwargs)


class BaseCheckbox(ft.Checkbox):
    def __init__(
        self,
        label: LabelValue = None,
        value: bool = False,
        on_change=None,
        **kwargs,
    ):
        super().__init__(
            label=_label_control(label),
            value=value,
            on_change=on_change,
            active_color=AppColors.PRIMARY_DARK,
            check_color=AppColors.TEXT,
            **kwargs,
        )


class BaseSwitch(ft.Switch):
    def __init__(
        self,
        label: LabelValue = None,
        value: bool = False,
        on_change=None,
        **kwargs,
    ):
        super().__init__(
            label=_label_control(label),
            value=value,
            on_change=on_change,
            active_color=AppColors.PRIMARY_DARK,
            **kwargs,
        )


class BaseRadio(ft.Radio):
    def __init__(self, value: str, label: LabelValue = None, **kwargs):
        super().__init__(
            value=value,
            label=_label_control(label),
            active_color=AppColors.PRIMARY_DARK,
            fill_color=AppColors.PRIMARY_DARK,
            **kwargs,
        )


class BaseRadioGroup(ft.RadioGroup):
    def __init__(
        self,
        options: Iterable[tuple[str, LabelValue]],
        value: Optional[str] = None,
        on_change=None,
        horizontal: bool = False,
        spacing: int = AppSpacing.MD,
        **kwargs,
    ):
        radio_controls = [BaseRadio(value=key, label=label) for key, label in options]
        layout: ft.Control
        if horizontal:
            layout = ft.Row(spacing=spacing, wrap=True, controls=radio_controls)
        else:
            layout = ft.Column(spacing=spacing, tight=True, controls=radio_controls)
        super().__init__(content=layout, value=value, on_change=on_change, **kwargs)


class BaseIconField(ft.Column):
    """Champ compact ouvrant une galerie d’icônes responsive."""

    def __init__(
        self,
        page: ft.Page,
        options: dict[str, str],
        label: str = "Icône",
        value: str | None = None,
        on_change: Callable[[str], None] | None = None,
        disabled: bool = False,
        expand: bool = False,
        **kwargs,
    ):
        self.app_page = page
        self.options = dict(options)
        self.external_on_change = on_change
        self._value = value if value in self.options.values() else next(iter(self.options.values()))
        self._temporary_value = self._value
        self._disabled = disabled
        self.dialog = None
        self.icon_grid = None

        self.preview_icon = ft.Icon(
            self._resolve_icon(self._value),
            color=AppColors.PRIMARY_DARK,
            size=AppSizes.ICON_MD,
        )
        self.value_text = ft.Text(
            self._label_for_value(self._value),
            size=AppText.BODY,
            weight=ft.FontWeight.W_600,
            color=AppColors.TEXT,
        )
        self.field = ft.Container(
            height=AppSizes.FIELD_HEIGHT,
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD),
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=AppRadius.MD,
            bgcolor=AppColors.SURFACE,
            on_click=self.open_picker,
            content=ft.Row(
                spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        alignment=ft.Alignment.CENTER,
                        border_radius=AppRadius.SM,
                        bgcolor=AppColors.PRIMARY_SOFT,
                        content=self.preview_icon,
                    ),
                    self.value_text,
                    ft.Container(expand=True),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT_ROUNDED,
                        size=AppSizes.ICON_SM,
                        color=AppColors.TEXT_MUTED,
                    ),
                ],
            ),
        )

        super().__init__(
            spacing=AppSpacing.XS,
            tight=True,
            expand=expand,
            controls=[FormLabel(label), self.field],
            **kwargs,
        )
        self.disabled = disabled

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if value not in self.options.values():
            return
        self._value = value
        self._temporary_value = value
        self._refresh_field()

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = bool(value)
        self.field.disabled = self._disabled
        self.field.opacity = 0.55 if self._disabled else 1.0

    def open_picker(self, _event=None) -> None:
        if self.disabled:
            return
        from app.theme.dialogs import AppDialog

        self._temporary_value = self._value
        self.icon_grid = ft.GridView(
            expand=False,
            height=390,
            max_extent=190,
            child_aspect_ratio=2.5,
            spacing=AppSpacing.SM,
            run_spacing=AppSpacing.SM,
            controls=self._build_icon_tiles(),
        )
        self.dialog = AppDialog(
            title="Choisir une icône",
            icon=ft.Icons.EMOJI_SYMBOLS_ROUNDED,
            width=820,
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.MD,
                controls=[
                    ft.Text(
                        "Sélectionnez une icône pour le classeur.",
                        size=AppText.BODY,
                        color=AppColors.TEXT_SECONDARY,
                    ),
                    self.icon_grid,
                ],
            ),
            actions=[
                SecondaryButton("Annuler", on_click=self._close_dialog),
                PrimaryButton(
                    "Appliquer",
                    icon=ft.Icons.CHECK_ROUNDED,
                    on_click=self._apply_icon,
                ),
            ],
        )
        self.app_page.overlay.append(self.dialog)
        self.dialog.open = True
        self.app_page.update()

    def _build_icon_tiles(self) -> list[ft.Control]:
        return [
            self._build_icon_tile(label, icon_name)
            for label, icon_name in self.options.items()
        ]

    def _build_icon_tile(self, label: str, icon_name: str) -> ft.Control:
        selected = icon_name == self._temporary_value
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.SM),
            border_radius=AppRadius.MD,
            bgcolor=AppColors.PRIMARY_SOFT if selected else AppColors.SURFACE,
            border=ft.Border.all(
                2 if selected else 1,
                AppColors.PRIMARY_DARK if selected else AppColors.BORDER,
            ),
            ink=True,
            on_click=lambda _event, value=icon_name: self._select_icon(value),
            content=ft.Row(
                spacing=AppSpacing.SM,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        self._resolve_icon(icon_name),
                        size=AppSizes.ICON_MD,
                        color=AppColors.PRIMARY_DARK,
                    ),
                    ft.Text(
                        label,
                        size=AppText.BODY,
                        color=AppColors.TEXT,
                        weight=ft.FontWeight.W_600 if selected else ft.FontWeight.NORMAL,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_ROUNDED,
                        size=AppSizes.ICON_SM,
                        color=AppColors.PRIMARY_DARK,
                        visible=selected,
                    ),
                ],
            ),
        )

    def _select_icon(self, value: str) -> None:
        self._temporary_value = value
        if self.icon_grid is not None:
            self.icon_grid.controls = self._build_icon_tiles()
        try:
            if self.dialog is not None:
                self.dialog.update()
        except RuntimeError:
            pass

    def _apply_icon(self, _event=None) -> None:
        self._value = self._temporary_value
        self._refresh_field()
        self._close_dialog()
        if self.external_on_change:
            self.external_on_change(self._value)

    def _close_dialog(self, _event=None) -> None:
        if self.dialog is None:
            return
        self.dialog.open = False
        try:
            self.app_page.update()
        except RuntimeError:
            pass

    def _refresh_field(self) -> None:
        self.preview_icon.icon = self._resolve_icon(self._value)
        self.value_text.value = self._label_for_value(self._value)
        try:
            if self.page is not None:
                self.update()
        except RuntimeError:
            pass

    def _label_for_value(self, value: str) -> str:
        return next(
            (label for label, icon_name in self.options.items() if icon_name == value),
            "Icône",
        )

    @staticmethod
    def _resolve_icon(icon_name: str):
        return getattr(ft.Icons, icon_name, ft.Icons.FOLDER_ROUNDED)


class FormLabel(ft.Text):
    def __init__(self, value: str, required: bool = False, **kwargs):
        text = f"{value} *" if required else value
        super().__init__(
            text,
            size=AppText.CAPTION,
            weight=ft.FontWeight.W_600,
            color=AppColors.TEXT_SECONDARY,
            **kwargs,
        )


class FormHelperText(ft.Text):
    def __init__(self, value: str, **kwargs):
        super().__init__(value, size=AppText.CAPTION, color=AppColors.TEXT_MUTED, **kwargs)


class FormErrorText(ft.Text):
    def __init__(self, value: str, **kwargs):
        super().__init__(value, size=AppText.CAPTION, color=AppColors.ERROR, **kwargs)


class FormGroup(ft.Column):
    def __init__(
        self,
        control: ft.Control,
        label: Optional[str] = None,
        helper_text: Optional[str] = None,
        error_text: Optional[str] = None,
        required: bool = False,
        spacing: int = AppSpacing.XS,
        **kwargs,
    ):
        controls = []
        if label:
            controls.append(FormLabel(label, required=required))
        controls.append(control)
        if error_text:
            controls.append(FormErrorText(error_text))
        elif helper_text:
            controls.append(FormHelperText(helper_text))
        super().__init__(spacing=spacing, controls=controls, **kwargs)


class FormRow(ft.ResponsiveRow):
    def __init__(
        self,
        controls: Iterable[ft.Control],
        spacing: int = AppSpacing.MD,
        **kwargs,
    ):
        super().__init__(
            controls=list(controls),
            spacing=spacing,
            run_spacing=spacing,
            **kwargs,
        )
