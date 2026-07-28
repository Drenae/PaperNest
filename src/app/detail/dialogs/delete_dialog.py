import asyncio

import flet as ft

from app.notifications import notifications
from app.theme.buttons import GhostButton, DangerButton
from app.theme.dialogs import AppDialog
from core.errors.exceptions import PaperNestError
from services.documents.delete import document_delete_service


class DeleteDialog:
    def __init__(self, page: ft.Page, document, on_deleted=None):
        self.page = page
        self.document = document
        self.on_deleted = on_deleted
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        if self.document.document_id is None:
            notifications(self.page).error(
                "Ce document ne possède pas d’identifiant."
            )
            return

        self.error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        self.delete_button = DangerButton(
            "Mettre à la corbeille",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            on_click=self.delete,
        )

        self.dialog = AppDialog(
            modal=True,
            title="Mettre à la corbeille",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        "Le document suivant sera déplacé "
                        "dans la corbeille PaperNest :"
                    ),
                    ft.Text(
                        self.document.name,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Il pourra être restauré depuis l’écran Corbeille.",
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
                self.delete_button,
            ],
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    async def delete(self, event) -> None:
        self.delete_button.disabled = True
        self.error_text.value = ""
        self.page.update()

        try:
            await asyncio.to_thread(
                document_delete_service.move_to_trash,
                self.document.document_id,
            )

            self.close()

            if self.on_deleted:
                result = self.on_deleted()

                if asyncio.iscoroutine(result):
                    await result

        except PaperNestError as error:
            self.show_error(str(error))

        except Exception:
            self.show_error(
                "Impossible de déplacer le document dans la corbeille."
            )

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self.delete_button.disabled = False
        self.page.update()

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
