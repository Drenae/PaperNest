from __future__ import annotations

from enum import Enum
from typing import Iterable, Optional

import flet as ft

from app.theme.tokens import AppColors, AppRadius, AppSizes, AppSpacing, AppText
from app.theme.buttons import DangerButton, PrimaryButton, SecondaryButton


class DialogVariant(str, Enum):
    STANDARD = "standard"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class AppDialog(ft.AlertDialog):
    """Dialogue PaperNest compact et compatible avec Flet 0.85.3."""

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
        palette = self._get_palette(variant)
        header = self._build_header(
            title=title,
            icon=icon,
            palette=palette,
            title_action=title_action,
        )

        dialog_content = ft.Container(
            width=width,
            content=ft.Column(
                tight=True,
                spacing=0,
                controls=[content] if content else [],
            ),
            expand=False,
        )

        super().__init__(
            modal=modal,
            title=header,
            content=dialog_content,
            actions=list(actions or []),
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=AppColors.SURFACE,
            shadow_color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
            shape=ft.RoundedRectangleBorder(radius=AppRadius.XL),
            title_padding=0,
            content_padding=ft.Padding.only(
                left=AppSpacing.XL,
                right=AppSpacing.XL,
                top=AppSpacing.LG,
                bottom=AppSpacing.MD,
            ),
            actions_padding=ft.Padding.only(
                left=AppSpacing.XL,
                right=AppSpacing.XL,
                top=AppSpacing.SM,
                bottom=AppSpacing.LG,
            ),
            scrollable=scrollable,
            barrier_color=ft.Colors.with_opacity(0.48, ft.Colors.BLACK),
            on_dismiss=None if dismissible else self._prevent_dismiss,
            **kwargs,
        )

    @staticmethod
    def _build_header(*, title, icon, palette, title_action=None) -> ft.Container:
        if isinstance(title, str):
            controls: list[ft.Control] = []
            if icon is not None:
                controls.append(
                    ft.Container(
                        width=38,
                        height=38,
                        alignment=ft.Alignment.CENTER,
                        border_radius=AppRadius.MD,
                        bgcolor=palette["icon_background"],
                        content=ft.Icon(
                            icon,
                            size=AppSizes.ICON_MD,
                            color=palette["icon_color"],
                        ),
                    )
                )
            controls.append(
                ft.Text(
                    title,
                    size=AppText.SECTION_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT_LIGHT,
                )
            )
            title_control: ft.Control = ft.Row(
                spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=AppSpacing.MD,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=controls,
                        expand=True,
                    ),
                    *([title_action] if title_action is not None else []),
                ],
            )
        else:
            title_control = title

        return ft.Container(
            bgcolor=AppColors.PANEL_DARK,
            padding=ft.Padding.symmetric(
                horizontal=AppSpacing.XL,
                vertical=AppSpacing.MD,
            ),
            border_radius=ft.BorderRadius.only(
                top_left=AppRadius.XL,
                top_right=AppRadius.XL,
            ),
            content=title_control,
        )

    @staticmethod
    def _prevent_dismiss(_event) -> None:
        return

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
            content=ft.Text(message, size=AppText.BODY, color=AppColors.TEXT_SECONDARY),
            actions=[
                SecondaryButton(cancel_text, icon=ft.Icons.CLOSE_ROUNDED, on_click=on_cancel),
                PrimaryButton(confirm_text, icon=confirm_icon, on_click=on_confirm),
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
            ft.Text(message, size=AppText.BODY, color=AppColors.TEXT_SECONDARY)
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
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=AppSizes.ICON_SM, color=AppColors.ERROR),
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
            content=ft.Column(spacing=AppSpacing.MD, tight=True, controls=controls),
            actions=[
                SecondaryButton(cancel_text, icon=ft.Icons.CLOSE_ROUNDED, on_click=on_cancel),
                DangerButton(confirm_text, icon=ft.Icons.DELETE_FOREVER_ROUNDED, on_click=on_confirm),
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
                SecondaryButton(cancel_text, icon=ft.Icons.CLOSE_ROUNDED, on_click=on_cancel),
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
