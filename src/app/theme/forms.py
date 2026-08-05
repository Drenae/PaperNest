from __future__ import annotations

from typing import Iterable, Optional, Union

import flet as ft
from papernestextension.controls.material.papernest_dropdown import (
    PaperNestDropdown,
    PaperNestDropdownOption,
)
from papernestextension.controls.material.papernest_textfield import (
    KeyboardType,
    PaperNestTextField,
)

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


class PickerTextField(BaseTextField):
    """Champ en lecture seule avec bouton de sélection fourni côté Python."""

    def __init__(self, picker_button: ft.Control, **kwargs):
        kwargs.setdefault("read_only", True)
        kwargs.setdefault("picker", True)
        kwargs.setdefault("picker_button", picker_button)
        kwargs.setdefault("clear_button", True)
        super().__init__(**kwargs)


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
