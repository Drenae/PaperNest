from __future__ import annotations

from enum import Enum
from typing import Iterable, Optional

import flet as ft
from papernestextension import PaperNestAlertDialog

from app.theme.buttons import DangerButton, PrimaryButton, SecondaryButton
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText


class DialogVariant(str, Enum):
    """Variantes visuelles propres à PaperNest.

    PaperNestAlertDialog ne connaît aucun variant. Cet enum choisit uniquement
    la palette de la pastille d'icône dans le wrapper Python de l'application.
    """

    STANDARD = "standard"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class AppDialog(PaperNestAlertDialog):
    """PaperNestAlertDialog configuré avec le thème de PaperNest."""

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

        kwargs.setdefault("title", title)
        kwargs.setdefault("subtitle", subtitle)
        kwargs.setdefault("content", content)
        kwargs.setdefault("icon", icon)
        kwargs.setdefault("actions", list(actions or []))
        kwargs.setdefault("title_action", title_action)
        kwargs.setdefault("width", width)
        kwargs.setdefault("max_height", max_height)
        kwargs.setdefault("modal", modal)
        kwargs.setdefault("dismissible", dismissible)
        kwargs.setdefault("scrollable", scrollable)

        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault("header_bgcolor", AppColors.PANEL_DARK)
        kwargs.setdefault("icon_bgcolor", palette["icon_background"])
        kwargs.setdefault("icon_color", palette["icon_color"])
        kwargs.setdefault("icon_size", AppSizes.ICON_MD)
        kwargs.setdefault("icon_container_size", 38)
        kwargs.setdefault("icon_border_radius", AppRadius.MD)
        kwargs.setdefault("header_spacing", AppSpacing.MD)
        kwargs.setdefault(
            "barrier_color",
            ft.Colors.with_opacity(0.48, ft.Colors.BLACK),
        )
        kwargs.setdefault(
            "shadow_color",
            ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
        )
        kwargs.setdefault("shape", ft.RoundedRectangleBorder(radius=AppRadius.XL))
        kwargs.setdefault("clip_behavior", ft.ClipBehavior.ANTI_ALIAS)
        kwargs.setdefault(
            "header_padding",
            ft.Padding.symmetric(
                horizontal=AppSpacing.XL,
                vertical=AppSpacing.MD,
            ),
        )
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
        kwargs.setdefault("actions_spacing", AppSpacing.SM)
        kwargs.setdefault(
            "title_text_style",
            ft.TextStyle(
                size=AppText.SECTION_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_LIGHT,
            ),
        )
        kwargs.setdefault(
            "subtitle_text_style",
            ft.TextStyle(
                size=AppText.CAPTION,
                color=ft.Colors.GREY_400,
            ),
        )

        super().__init__(**kwargs)

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
