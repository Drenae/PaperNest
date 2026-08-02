import asyncio
from pathlib import Path

import flet as ft
from papernestextension.controls.material.papernest_textfield import PaperNestTextFieldState

from app.theme.buttons import PrimaryButton, GhostButton
from app.theme.forms import BaseTextField
from app.theme.dialogs import AppDialog, DialogVariant

from core.errors.exceptions import PaperNestError
from services.documents.rename import document_rename_service


class RenameDialog:
    def __init__(self, page: ft.Page, document, on_renamed=None):
        self.page = page
        self.document = document
        self.on_renamed = on_renamed
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        if self.document.document_id is None:
            return

        current_path = Path(self.document.absolute_path)

        name_field = BaseTextField(
            label="Nouveau nom",
            value=current_path.stem.replace("_", " "),
            autofocus=True,
            prefix_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            on_submit=self.rename,
        )

        self.error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        self.rename_button = PrimaryButton(
            "Renommer",
            icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            on_click=self.rename,
        )

        self.name_field = name_field

        self.dialog = AppDialog(
            modal=True,
            title="Renommer le document",
            icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            variant=DialogVariant.PRIMARY,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        self.document.name,
                        weight=ft.FontWeight.BOLD,
                    ),
                    name_field,
                    ft.Text(
                        f"L’extension {current_path.suffix} sera conservée.",
                        size=12,
                        color=ft.Colors.GREY_600,
                    ),
                    self.error_text,
                ],
            ),
            actions=[
                GhostButton(
                    "Annuler",
                    on_click=lambda event: self.close(),
                ),
                self.rename_button,
            ],
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    async def rename(self, event) -> None:
        new_name = self.name_field.value.strip() if self.name_field.value else ""

        if not new_name:
            self.name_field.state = PaperNestTextFieldState.ERROR
            self.name_field.state_message = "Le nouveau nom est obligatoire."
            self.page.update()
            return

        self.name_field.state = PaperNestTextFieldState.NORMAL
        self.name_field.state_message = None
        self.error_text.value = ""

        self.set_loading(True)

        try:
            destination = await asyncio.to_thread(
                document_rename_service.rename,
                self.document.document_id,
                new_name,
            )

            self.close()

            if self.on_renamed:
                result = self.on_renamed(destination)

                if asyncio.iscoroutine(result):
                    await result

        except PaperNestError as error:
            self.show_error(str(error))

        except Exception:
            self.show_error(
                "Impossible de renommer le document."
            )

    def set_loading(self, loading: bool) -> None:
        self.name_field.disabled = loading
        self.rename_button.disabled = loading
        self.page.update()

    def show_error(self, message: str) -> None:
        self.name_field.state = PaperNestTextFieldState.ERROR
        self.name_field.state_message = message
        self.error_text.value = ""
        self.set_loading(False)

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
