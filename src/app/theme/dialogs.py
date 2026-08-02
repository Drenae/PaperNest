from __future__ import annotations

from typing import Iterable, Optional

import flet as ft
from papernestextension import PaperNestAlertDialog, PaperNestDialogVariant

from app.theme.buttons import DangerButton, PrimaryButton, SecondaryButton
from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText


# Compatibilité avec les imports existants de PaperNest.
DialogVariant = PaperNestDialogVariant


class AppDialog(PaperNestAlertDialog):
    """PaperNestAlertDialog configuré avec le thème de PaperNest."""

    def __init__(
        self,
        *,
        title: str | ft.Control,
        content: Optional[ft.Control] = None,
        icon=None,
        variant: DialogVariant = DialogVariant.STANDARD,
        actions: Optional[Iterable[ft.Control]] = None,
        title_action: Optional[ft.Control] = None,
        width: float = AppSizes.DIALOG_WIDTH,
        modal: bool = False,
        dismissible: bool = True,
        scrollable: bool = False,
        **kwargs,
    ):
        kwargs.setdefault("title", title)
        kwargs.setdefault("content", content)
        kwargs.setdefault("icon", icon)
        kwargs.setdefault("variant", variant)
        kwargs.setdefault("actions", list(actions or []))
        kwargs.setdefault("title_action", title_action)
        kwargs.setdefault("width", width)
        kwargs.setdefault("modal", modal)
        kwargs.setdefault("dismissible", dismissible)
        kwargs.setdefault("scrollable", scrollable)

        kwargs.setdefault("bgcolor", AppColors.SURFACE)
        kwargs.setdefault("header_bgcolor", ft.Colors.GREY_900)
        kwargs.setdefault("header_color", AppColors.TEXT_LIGHT)
        kwargs.setdefault("barrier_color", ft.Colors.with_opacity(0.48, ft.Colors.BLACK))
        kwargs.setdefault("shadow_color", ft.Colors.with_opacity(0.22, ft.Colors.BLACK))
        kwargs.setdefault("shape", ft.RoundedRectangleBorder(radius=AppRadius.XL))
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
        kwargs.setdefault(
            "title_text_style",
            ft.TextStyle(
                size=AppText.SECTION_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_LIGHT,
            ),
        )

        super().__init__(**kwargs)


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
