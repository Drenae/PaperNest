import asyncio
import logging

import flet as ft

from core.errors.exceptions import PaperNestError
from services.categories.service import category_service
from app.theme.dialogs import DangerDialog

logger = logging.getLogger(__name__)


class DeleteCategoryDialog:
    def __init__(self, page: ft.Page, category: dict, on_deleted=None):
        self.page = page
        self.category = category
        self.on_deleted = on_deleted
        self.dialog: DangerDialog | None = None

    def show(self) -> None:
        document_count = int(
            self.category.get("document_count", 0)
        )

        if document_count == 0:
            self._show_empty_category_dialog()
        else:
            self._show_non_empty_category_dialog(document_count)

    def _show_empty_category_dialog(self) -> None:
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
                    category_service.delete_empty_category,
                    str(self.category["key"]),
                )

                self.close()
                await self._notify_deleted()

            except PaperNestError as error:
                error_text.value = str(error)
                delete_button.disabled = False
                self.page.update()

            except Exception:
                logger.exception(
                    "Impossible de supprimer le classeur %s.",
                    self.category.get("key"),
                )

                error_text.value = "Impossible de supprimer le classeur."
                delete_button.disabled = False
                self.page.update()

        self.dialog = DangerDialog(
            modal=True,
            title="Supprimer le classeur",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            message=f"Supprimer définitivement le classeur « {self.category['name']} » ?",
            on_confirm=delete,
            on_cancel=lambda event: self.close(),
            confirm_text="Supprimer",
            confirm_icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"Supprimer définitivement le classeur "
                        f"« {self.category['name']} » ?"
                    ),
                    ft.Text(
                        "Ce classeur ne contient aucun document.",
                        color=ft.Colors.GREY_600,
                    ),
                    error_text,
                ],
            ),
        )
        delete_button = self.dialog.confirm_button

        self._open()

    def _show_non_empty_category_dialog(self, document_count: int) -> None:
        action_selector = ft.RadioGroup(
            value="trash",
            content=ft.Column(
                controls=[
                    ft.Radio(
                        value="trash",
                        label=(
                            "Placer le classeur et ses documents "
                            "dans la corbeille"
                        ),
                    ),
                    ft.Radio(
                        value="unsorted",
                        label=(
                            "Déplacer les documents dans "
                            "le dossier Non classés"
                        ),
                    ),
                ],
            ),
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
                if action_selector.value == "unsorted":
                    await asyncio.to_thread(
                        category_service.delete_and_move_documents,
                        str(self.category["key"]),
                    )
                else:
                    await asyncio.to_thread(
                        category_service.delete_and_trash_documents,
                        str(self.category["key"]),
                    )

                self.close()
                await self._notify_deleted()

            except PaperNestError as error:
                error_text.value = str(error)
                delete_button.disabled = False
                self.page.update()

            except Exception:
                logger.exception(
                    "Impossible de supprimer le classeur %s.",
                    self.category.get("key"),
                )

                error_text.value = "Impossible de supprimer le classeur."
                delete_button.disabled = False
                self.page.update()

        label = (
            f"{document_count} document"
            if document_count == 1
            else f"{document_count} documents"
        )

        self.dialog = DangerDialog(
            modal=True,
            title="Supprimer un classeur non vide",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            message=f"Le classeur « {self.category['name']} » contient {label}.",
            on_confirm=delete,
            on_cancel=lambda event: self.close(),
            confirm_text="Supprimer",
            confirm_icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        f"Le classeur « {self.category['name']} » "
                        f"contient {label}."
                    ),
                    action_selector,
                    error_text,
                ],
            ),
        )
        delete_button = self.dialog.confirm_button

        self._open()

    async def _notify_deleted(self) -> None:
        if not self.on_deleted:
            return

        result = self.on_deleted(self.category)

        if asyncio.iscoroutine(result):
            await result

    def _open(self) -> None:
        if self.dialog is None:
            return

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
