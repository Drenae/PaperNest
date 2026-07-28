import asyncio
import logging

import flet as ft

from app.notifications import notifications
from app.theme.buttons import GhostButton, SuccessButton
from app.theme.dialogs import AppDialog
from app.theme.forms import BaseDropDown, PaperNestDropdownOption
from core.errors.exceptions import PaperNestError
from services.trash.service import TrashService, TrashedDocument

logger = logging.getLogger(__name__)


class RestoreDialog:
    def __init__(self, page: ft.Page, document: TrashedDocument, on_restored=None):
        self.page = page
        self.document = document
        self.on_restored = on_restored
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        categories = TrashService.get_available_categories()

        if not categories:
            notifications(self.page).warning("Aucun classeur n’est disponible " "pour restaurer ce document.")
            return

        original_exists = any(str(category["key"]) == self.document.original_category_key for category in categories)

        selector = BaseDropDown(
            label="Classeur de destination",
            expand=True,
            leading_icon=ft.Icons.FOLDER_COPY_ROUNDED,
            value=(self.document.original_category_key if original_exists else None),
            options=[
                PaperNestDropdownOption(
                    key=str(category["key"]),
                    text=str(category["name"]),
                    leading_icon=getattr(ft.Icons, str(category.get("icon") or ""), (ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED if category.get("parent_key") else ft.Icons.FOLDER_ROUNDED))
                )
                for category in categories
            ],
        )

        error_text = ft.Text("", size=12, color=ft.Colors.RED_600)

        restore_button = SuccessButton("Restaurer", icon=ft.Icons.RESTORE_FROM_TRASH_ROUNDED)

        async def restore(event) -> None:
            if not selector.value:
                error_text.value = ("Sélectionnez un classeur de destination.")
                self.page.update()
                return
            restore_button.disabled = True
            error_text.value = ""
            self.page.update()
            try:
                destination = await asyncio.to_thread(TrashService.restore_document, self.document.trash_id, str(selector.value))
                self.close()
                if self.on_restored:
                    result = self.on_restored(destination)
                    if asyncio.iscoroutine(result):
                        await result
            except PaperNestError as error:
                error_text.value = str(error)
                restore_button.disabled = False
                self.page.update()
            except Exception:
                logger.exception("Impossible de restaurer %s.", self.document.trash_id)
                error_text.value = ("Impossible de restaurer le document.")
                restore_button.disabled = False
                self.page.update()
        restore_button.on_click = restore

        self.dialog = AppDialog(
            modal=True,
            title="Restaurer le document",
            icon=ft.Icons.RESTORE_FROM_TRASH_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(self.document.display_name, weight=ft.FontWeight.BOLD),
                    selector,
                    error_text,
                ],
            ),
            actions=[
                GhostButton("Annuler", on_click=lambda event: self.close()),
                restore_button,
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
