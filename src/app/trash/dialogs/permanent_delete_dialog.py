import asyncio
import logging

import flet as ft

from app.theme.buttons import GhostButton, DangerButton
from app.theme.dialogs import AppDialog

from core.errors.exceptions import PaperNestError
from services.trash.service import TrashService, TrashedDocument


logger = logging.getLogger(__name__)


class PermanentDeleteDialog:
    def __init__(self, page: ft.Page, document: TrashedDocument, on_deleted=None):
        self.page = page
        self.document = document
        self.on_deleted = on_deleted
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        delete_button = DangerButton(
            "Supprimer définitivement",
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
        )

        error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        async def delete(event) -> None:
            delete_button.disabled = True
            error_text.value = ""
            self.page.update()

            try:
                await asyncio.to_thread(
                    TrashService.permanently_delete,
                    self.document.trash_id,
                )

                self.close()

                if self.on_deleted:
                    result = self.on_deleted(self.document)

                    if asyncio.iscoroutine(result):
                        await result

            except PaperNestError as error:
                error_text.value = str(error)
                delete_button.disabled = False
                self.page.update()

            except Exception:
                logger.exception(
                    "Impossible de supprimer définitivement %s.",
                    self.document.trash_id,
                )

                error_text.value = (
                    "Impossible de supprimer définitivement le document."
                )

                delete_button.disabled = False
                self.page.update()

        delete_button.on_click = delete

        self.dialog = AppDialog(
            modal=True,
            title="Supprimer définitivement",
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"Le document « {self.document.display_name} » "
                        "sera supprimé définitivement."
                    ),
                    ft.Text(
                        "Cette action est irréversible.",
                        color=ft.Colors.RED_600,
                        weight=ft.FontWeight.BOLD,
                    ),
                    error_text,
                ],
            ),
            actions=[
                GhostButton(
                    "Annuler",
                    on_click=lambda event: self.close(),
                ),
                delete_button,
            ],
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
