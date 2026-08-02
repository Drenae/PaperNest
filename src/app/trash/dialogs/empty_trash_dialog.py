import asyncio
import logging

import flet as ft

from app.theme.buttons import GhostButton, DangerButton
from app.theme.dialogs import AppDialog, DialogVariant

from core.errors.exceptions import PaperNestError
from services.trash.service import TrashService


logger = logging.getLogger(__name__)


class EmptyTrashDialog:
    def __init__(self, page: ft.Page, on_emptied=None):
        self.page = page
        self.on_emptied = on_emptied
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        delete_button = DangerButton("Vider la corbeille", icon=ft.Icons.DELETE_FOREVER_ROUNDED)
        error_text = ft.Text("", size=12, color=ft.Colors.RED_600)

        async def empty(event) -> None:
            delete_button.disabled = True
            error_text.value = ""
            self.page.update()

            try:
                deleted_count = await asyncio.to_thread(TrashService.empty_trash)
                self.close()
                if self.on_emptied:
                    result = self.on_emptied(deleted_count)
                    if asyncio.iscoroutine(result):
                        await result
            except PaperNestError as error:
                error_text.value = str(error)
                delete_button.disabled = False
                self.page.update()
            except Exception:
                logger.exception("Impossible de vider la corbeille.")
                error_text.value = ("Impossible de vider la corbeille.")
                delete_button.disabled = False
                self.page.update()
        delete_button.on_click = empty

        self.dialog = AppDialog(
            modal=True,
            title="Vider la corbeille",
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            variant=DialogVariant.DANGER,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text("Tous les documents présents dans la corbeille seront supprimés définitivement."),
                    ft.Text("Cette action est irréversible.", color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
                    error_text,
                ],
            ),
            actions=[GhostButton("Annuler", on_click=lambda event: self.close()), delete_button],
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self) -> None:
        if self.dialog is None:
            return
        self.dialog.open = False
        self.page.update()