from __future__ import annotations

from enum import Enum
from typing import Iterable, Optional

import flet as ft

from app.theme.buttons import DangerButton, PrimaryButton, SecondaryButton
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText


class DialogVariant(str, Enum):
    """Variantes visuelles propres à PaperNest."""

    STANDARD = "standard"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class DialogHeader(ft.Container):
    """En-tête PaperNest entièrement construit côté Python."""

    def __init__(
        self,
        *,
        title: str | ft.Control,
        subtitle: str | ft.Control | None = None,
        icon=None,
        title_action: Optional[ft.Control] = None,
        bgcolor=AppColors.PANEL_DARK,
        icon_bgcolor=AppColors.PANEL_DARK_SOFT,
        icon_color=AppColors.TEXT_LIGHT,
        icon_size: float = AppSizes.ICON_MD,
        icon_container_size: float = 38,
        icon_border_radius: float = AppRadius.MD,
        spacing: float = AppSpacing.MD,
        padding: ft.PaddingValue = ft.Padding.symmetric(
            horizontal=AppSpacing.XL,
            vertical=AppSpacing.MD,
        ),
        title_text_style: Optional[ft.TextStyle] = None,
        subtitle_text_style: Optional[ft.TextStyle] = None,
        **kwargs,
    ):
        title_control = (
            title
            if isinstance(title, ft.Control)
            else ft.Text(
                title,
                style=title_text_style
                or ft.TextStyle(
                    size=AppText.SECTION_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT_LIGHT,
                ),
            )
        )

        subtitle_control: Optional[ft.Control] = None
        if subtitle is not None:
            subtitle_control = (
                subtitle
                if isinstance(subtitle, ft.Control)
                else ft.Text(
                    subtitle,
                    style=subtitle_text_style
                    or ft.TextStyle(
                        size=AppText.CAPTION,
                        color=ft.Colors.GREY_400,
                    ),
                )
            )

        icon_control: Optional[ft.Control] = None
        if icon is not None:
            raw_icon = (
                icon
                if isinstance(icon, ft.Control)
                else ft.Icon(icon, size=icon_size, color=icon_color)
            )
            icon_control = ft.Container(
                width=icon_container_size,
                height=icon_container_size,
                alignment=ft.Alignment.CENTER,
                bgcolor=icon_bgcolor,
                border_radius=icon_border_radius,
                content=raw_icon,
            )

        title_controls: list[ft.Control] = [title_control]
        if subtitle_control is not None:
            title_controls.append(subtitle_control)

        row_controls: list[ft.Control] = []
        if icon_control is not None:
            row_controls.append(icon_control)
        row_controls.append(
            ft.Column(
                controls=title_controls,
                spacing=2,
                tight=True,
                expand=True,
            )
        )
        if title_action is not None:
            row_controls.append(title_action)

        super().__init__(
            bgcolor=bgcolor,
            padding=padding,
            content=ft.Row(
                controls=row_controls,
                spacing=spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **kwargs,
        )


class AppDialog(ft.AlertDialog):
    """AlertDialog Flet natif habillé entièrement côté Python."""

    def __init__(
        self,
        *,
        title: str | ft.Control,
        subtitle: str | ft.Control | None = None,
        content: Optional[ft.Control] = None,
        icon=None,
        variant: DialogVariant = DialogVariant.STANDARD,
        actions: Optional[Iterable[ft.Control]] = None,
        title_action: Optional[ft.Control] = None,
        width: float = AppSizes.DIALOG_WIDTH,
        max_height: Optional[float] = None,
        modal: bool = False,
        dismissible: bool = True,
        scrollable: bool = False,
        **kwargs,
    ):
        palette = self._get_palette(variant)

        header_bgcolor = kwargs.pop("header_bgcolor", AppColors.PANEL_DARK)
        icon_bgcolor = kwargs.pop(
            "icon_bgcolor",
            palette["icon_background"],
        )
        icon_color = kwargs.pop("icon_color", palette["icon_color"])
        icon_size = kwargs.pop("icon_size", AppSizes.ICON_MD)
        icon_container_size = kwargs.pop("icon_container_size", 38)
        icon_border_radius = kwargs.pop(
            "icon_border_radius",
            AppRadius.MD,
        )
        header_spacing = kwargs.pop("header_spacing", AppSpacing.MD)
        header_padding = kwargs.pop(
            "header_padding",
            ft.Padding.symmetric(
                horizontal=AppSpacing.XL,
                vertical=AppSpacing.MD,
            ),
        )
        title_text_style = kwargs.pop(
            "title_text_style",
            ft.TextStyle(
                size=AppText.SECTION_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_LIGHT,
            ),
        )
        subtitle_text_style = kwargs.pop(
            "subtitle_text_style",
            ft.TextStyle(
                size=AppText.CAPTION,
                color=ft.Colors.GREY_400,
            ),
        )
        actions_spacing = kwargs.pop("actions_spacing", AppSpacing.SM)

        dialog_header = DialogHeader(
            title=title,
            subtitle=subtitle,
            icon=icon,
            title_action=title_action,
            bgcolor=header_bgcolor,
            icon_bgcolor=icon_bgcolor,
            icon_color=icon_color,
            icon_size=icon_size,
            icon_container_size=icon_container_size,
            icon_border_radius=icon_border_radius,
            spacing=header_spacing,
            padding=header_padding,
            title_text_style=title_text_style,
            subtitle_text_style=subtitle_text_style,
        )

        effective_width = getattr(content, "width", None) or width
        dialog_content = content

        if content is not None:
            if scrollable:
                dialog_content = ft.Container(
                    width=effective_width,
                    height=max_height or 600,
                    content=ft.Column(
                        controls=[content],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                )
            else:
                dialog_content = ft.Container(
                    width=effective_width,
                    content=content,
                )

        action_controls = list(actions or [])
        if actions_spacing and len(action_controls) > 1:
            action_controls = [
                ft.Container(
                    margin=ft.Margin.only(left=actions_spacing if index else 0),
                    content=action,
                )
                for index, action in enumerate(action_controls)
            ]

        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault(
            "barrier_color",
            ft.Colors.with_opacity(0.48, ft.Colors.BLACK),
        )
        kwargs.setdefault(
            "shadow_color",
            ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
        )
        kwargs.setdefault(
            "shape",
            ft.RoundedRectangleBorder(radius=AppRadius.XL),
        )
        kwargs.setdefault("clip_behavior", ft.ClipBehavior.ANTI_ALIAS)
        kwargs.setdefault("title_padding", ft.Padding.all(0))
        kwargs.setdefault(
            "content_padding",
            ft.Padding.only(
                left=AppSpacing.XL,
                right=AppSpacing.XL,
                top=AppSpacing.LG,
                bottom=AppSpacing.MD,
            ),
        )
        kwargs.setdefault(
            "actions_padding",
            ft.Padding.only(
                left=AppSpacing.XL,
                right=AppSpacing.XL,
                top=AppSpacing.SM,
                bottom=AppSpacing.LG,
            ),
        )
        kwargs.setdefault("actions_alignment", ft.MainAxisAlignment.END)

        # Le contrôle natif ne possède pas de propriété dismissible séparée.
        # Un dialogue non dismissible est donc rendu modal.
        effective_modal = modal or not dismissible

        super().__init__(
            title=dialog_header,
            content=dialog_content,
            actions=action_controls,
            modal=effective_modal,
            scrollable=False,
            **kwargs,
        )

    @staticmethod
    def _get_palette(variant: DialogVariant) -> dict[str, str]:
        return {
            DialogVariant.STANDARD: {
                "icon_background": AppColors.PANEL_DARK_SOFT,
                "icon_color": AppColors.TEXT_LIGHT,
            },
            DialogVariant.PRIMARY: {
                "icon_background": AppColors.PRIMARY,
                "icon_color": AppColors.TEXT,
            },
            DialogVariant.SUCCESS: {
                "icon_background": AppColors.SUCCESS,
                "icon_color": AppColors.TEXT_LIGHT,
            },
            DialogVariant.WARNING: {
                "icon_background": AppColors.WARNING,
                "icon_color": AppColors.TEXT_LIGHT,
            },
            DialogVariant.DANGER: {
                "icon_background": AppColors.ERROR,
                "icon_color": AppColors.TEXT_LIGHT,
            },
        }[variant]


class ConfirmDialog(AppDialog):
    def __init__(
        self,
        *,
        title: str,
        message: str,
        on_confirm,
        on_cancel,
        icon=ft.Icons.HELP_OUTLINE_ROUNDED,
        confirm_text: str = "Confirmer",
        cancel_text: str = "Annuler",
        variant: DialogVariant = DialogVariant.PRIMARY,
        confirm_icon=ft.Icons.CHECK_ROUNDED,
        **kwargs,
    ):
        super().__init__(
            title=title,
            icon=icon,
            variant=variant,
            content=ft.Text(
                message,
                size=AppText.BODY,
                color=AppColors.TEXT_SECONDARY,
            ),
            actions=[
                SecondaryButton(
                    cancel_text,
                    icon=ft.Icons.CLOSE_ROUNDED,
                    on_click=on_cancel,
                ),
                PrimaryButton(
                    confirm_text,
                    icon=confirm_icon,
                    on_click=on_confirm,
                ),
            ],
            **kwargs,
        )


class DangerDialog(AppDialog):
    def __init__(
        self,
        *,
        title: str,
        message: str,
        on_confirm,
        on_cancel,
        confirm_text: str = "Supprimer définitivement",
        cancel_text: str = "Annuler",
        details: Optional[ft.Control] = None,
        **kwargs,
    ):
        controls: list[ft.Control] = [
            ft.Text(
                message,
                size=AppText.BODY,
                color=AppColors.TEXT_SECONDARY,
            )
        ]
        if details is not None:
            controls.append(
                ft.Container(
                    padding=AppSpacing.MD,
                    bgcolor=AppColors.ERROR_SOFT,
                    border_radius=AppRadius.MD,
                    border=ft.Border.all(1, AppColors.ERROR_LIGHT),
                    content=details,
                )
            )
        controls.append(
            ft.Row(
                spacing=AppSpacing.SM,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Icon(
                        ft.Icons.WARNING_AMBER_ROUNDED,
                        size=AppSizes.ICON_SM,
                        color=AppColors.ERROR,
                    ),
                    ft.Text(
                        "Cette action est irréversible.",
                        size=AppText.CAPTION,
                        weight=ft.FontWeight.W_600,
                        color=AppColors.ERROR,
                        expand=True,
                    ),
                ],
            )
        )
        super().__init__(
            title=title,
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            variant=DialogVariant.DANGER,
            content=ft.Column(
                spacing=AppSpacing.MD,
                tight=True,
                controls=controls,
            ),
            actions=[
                SecondaryButton(
                    cancel_text,
                    icon=ft.Icons.CLOSE_ROUNDED,
                    on_click=on_cancel,
                ),
                DangerButton(
                    confirm_text,
                    icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                    on_click=on_confirm,
                ),
            ],
            **kwargs,
        )


class FormDialog(AppDialog):
    def __init__(
        self,
        *,
        title: str,
        form: ft.Control,
        on_submit,
        on_cancel,
        submit_text: str = "Enregistrer",
        cancel_text: str = "Annuler",
        icon=ft.Icons.EDIT_NOTE_ROUNDED,
        submit_icon=ft.Icons.SAVE_ROUNDED,
        submit_disabled: bool = False,
        loading: bool = False,
        variant: DialogVariant = DialogVariant.PRIMARY,
        **kwargs,
    ):
        self.submit_button = PrimaryButton(
            submit_text,
            icon=submit_icon,
            on_click=on_submit,
            disabled=submit_disabled,
            loading=loading,
        )
        super().__init__(
            title=title,
            icon=icon,
            variant=variant,
            content=form,
            actions=[
                SecondaryButton(
                    cancel_text,
                    icon=ft.Icons.CLOSE_ROUNDED,
                    on_click=on_cancel,
                ),
                self.submit_button,
            ],
            **kwargs,
        )

    def set_loading(self, loading: bool, *, update: bool = True) -> None:
        self.submit_button.set_loading(
            loading,
            loading_text="Enregistrement…",
            update=update,
        )
