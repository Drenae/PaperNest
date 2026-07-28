import asyncio

import flet as ft

from app.notifications import notifications
from app.theme.buttons import PrimaryButton, GhostButton
from app.theme.dialogs import AppDialog
from app.theme.forms import BaseDropDown, PaperNestDropdownOption
from core.errors.exceptions import PaperNestError
from repositories.category_repository import category_repository
from services.documents.move import document_move_service


class MoveDialog:
    def __init__(self, page: ft.Page, document, on_moved=None):
        self.page = page
        self.document = document
        self.on_moved = on_moved
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        if self.document.document_id is None:
            notifications(self.page).error(
                "Ce document ne possède pas d’identifiant."
            )
            return

        categories = []
        for parent in category_repository.list_tree():
            if str(parent["key"]) != str(self.document.category_key):
                categories.append((parent, str(parent["name"])))
            for child in parent.get("children", []):
                if str(child["key"]) != str(self.document.category_key):
                    categories.append((child, f"{parent['name']} / {child['name']}"))

        if not categories:
            notifications(self.page).warning(
                "Aucun autre classeur n’est disponible."
            )
            return

        self.selector = BaseDropDown(
            label="Classeur de destination",
            leading_icon=ft.Icons.FOLDER_COPY_ROUNDED,
            options=[
                PaperNestDropdownOption(
                    key=str(category["key"]),
                    text=label,
                )
                for category, label in categories
            ],
        )

        self.error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        self.move_button = PrimaryButton(
            "Déplacer",
            icon=ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            on_click=self.move,
        )

        self.dialog = AppDialog(
            modal=True,
            title="Déplacer le document",
            icon=ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        self.document.name,
                        weight=ft.FontWeight.BOLD,
                    ),
                    self.selector,
                    self.error_text,
                ],
            ),
            actions=[
                GhostButton(
                    "Annuler",
                    on_click=lambda event: self.close(),
                ),
                self.move_button,
            ],
        )

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    async def move(self, event) -> None:
        if not self.selector.value:
            self.error_text.value = "Sélectionnez un classeur."
            self.page.update()
            return

        self.set_loading(True)

        try:
            destination = await asyncio.to_thread(
                document_move_service.move,
                self.document.document_id,
                str(self.selector.value),
            )

            self.close()

            if self.on_moved:
                result = self.on_moved(destination)

                if asyncio.iscoroutine(result):
                    await result

        except PaperNestError as error:
            self.show_error(str(error))

        except Exception:
            self.show_error(
                "Impossible de déplacer le document."
            )

    def set_loading(self, loading: bool) -> None:
        self.selector.disabled = loading
        self.move_button.disabled = loading
        self.page.update()

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self.set_loading(False)

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
