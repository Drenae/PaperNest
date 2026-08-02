import asyncio
import logging

import flet as ft

from app.theme.buttons import PrimaryButton, GhostButton
from app.theme.forms import BaseDropDown, PaperNestDropdownOption
from app.theme.dialogs import AppDialog, DialogVariant

from core.errors.exceptions import PaperNestError
from services.trash.service import TrashService

logger = logging.getLogger(__name__)


class BatchTrashDialog:
    def __init__(self, page: ft.Page, trash_ids: list[str], mode: str, on_completed=None):
        self.page = page
        self.trash_ids = list(dict.fromkeys(trash_ids))
        self.mode = mode
        self.on_completed = on_completed
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        restoring = self.mode == "restore"
        categories = TrashService.get_available_categories() if restoring else []
        selector = BaseDropDown(
            label="Classeur de destination",
            visible=restoring,
            options=[PaperNestDropdownOption(key=str(category["key"]), text=str(category["name"])) for category in categories],
        )
        error_text = ft.Text("", size=12, color=ft.Colors.RED_600)
        action_button = PrimaryButton(
            "Restaurer la sélection" if restoring else "Supprimer la sélection",
            icon=ft.Icons.RESTORE_FROM_TRASH_ROUNDED if restoring else ft.Icons.DELETE_FOREVER_ROUNDED,
            bgcolor=ft.Colors.GREEN_700 if restoring else ft.Colors.RED_600,
        )

        async def execute(event) -> None:
            action_button.disabled = True
            error_text.value = ""
            self.page.update()
            try:
                if restoring:
                    count, errors = await asyncio.to_thread(TrashService.restore_many, self.trash_ids, str(selector.value) if selector.value else None)
                else:
                    count, errors = await asyncio.to_thread(TrashService.permanently_delete_many, self.trash_ids)
                self.close()
                if self.on_completed:
                    result = self.on_completed(count, errors, self.mode)
                    if asyncio.iscoroutine(result):
                        await result
            except PaperNestError as error:
                error_text.value = str(error)
                action_button.disabled = False
                self.page.update()
            except Exception:
                logger.exception("Action multiple impossible dans la corbeille.")
                error_text.value = "L’action multiple n’a pas pu être terminée."
                action_button.disabled = False
                self.page.update()

        action_button.on_click = execute
        self.dialog = AppDialog(
            modal=True,
            title="Restaurer plusieurs documents" if restoring else "Suppression définitive",
            icon=(
                ft.Icons.RESTORE_FROM_TRASH_ROUNDED
                if restoring
                else ft.Icons.DELETE_FOREVER_ROUNDED
            ),
            variant=(
                DialogVariant.SUCCESS
                if restoring
                else DialogVariant.DANGER
            ),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(f"{len(self.trash_ids)} document(s) sélectionné(s)."),
                    selector,
                    ft.Text("Cette action est irréversible.", visible=not restoring, color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
                    error_text,
                ],
            ),
            actions=[GhostButton("Annuler", on_click=lambda event: self.close()), action_button],
        )
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self) -> None:
        if self.dialog:
            self.dialog.open = False
            self.page.update()
