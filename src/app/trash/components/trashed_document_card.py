from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.theme.buttons import IconAction

from services.trash.service import TrashedDocument
from app.shared.document_card import (
    DocumentCard,
    DocumentCardVariant,
)


class TrashedDocumentCard(DocumentCard):
    """
    Adaptateur de la carte universelle pour un document placé
    dans la corbeille.

    La présentation est déléguée à DocumentCard tandis que les actions
    propres à la corbeille restent injectées par TrashView.
    """

    def __init__(
        self,
        document: TrashedDocument,
        selected: bool,
        on_selected: Callable,
        on_open_folder: Callable,
        on_restore: Callable,
        on_delete: Callable,
    ):
        self.document = document

        self.on_document_selected = on_selected
        self.on_open_folder = on_open_folder
        self.on_restore = on_restore
        self.on_delete = on_delete

        super().__init__(
            title=document.display_name,
            extension=document.extension,
            metadata=self._build_metadata(),
            tags=document.tags,
            variant=DocumentCardVariant.TRASH,
            selected=selected,
            selectable=True,
            selection_value=selected,
            status_text=document.expiration_label,
            status_color=self._resolve_expiration_color(),
            progress=document.expiration_progress,
            tooltip=(
                f"Document supprimé : {document.display_name}"
            ),
            on_selected=self._handle_selection,
            actions=[
                self._build_open_folder_button(),
                self._build_restore_button(),
                self._build_delete_button(),
            ],
        )

    def _build_metadata(self) -> list[str]:
        metadata = [
            f"Classeur : {self.document.original_category_name}",
            f"Taille : {self.document.formatted_size}",
            f"Supprimé le : {self.document.deleted_at_display}",
        ]

        if self.document.person_name:
            metadata.append(
                f"Personne : {self.document.person_name}"
            )

        return metadata

    def _build_open_folder_button(self) -> ft.IconButton:
        return IconAction(
            icon=ft.Icons.FOLDER_OPEN_ROUNDED,
            icon_color=ft.Colors.BLUE_700,
            tooltip="Ouvrir le dossier de corbeille",
            on_click=self._handle_open_folder,
        )

    def _build_restore_button(self) -> ft.IconButton:
        return IconAction(
            icon=ft.Icons.RESTORE_FROM_TRASH_ROUNDED,
            icon_color=ft.Colors.GREEN_700,
            tooltip="Restaurer le document",
            on_click=self._handle_restore,
        )

    def _build_delete_button(self) -> ft.IconButton:
        return IconAction(
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            icon_color=ft.Colors.RED_600,
            tooltip="Supprimer définitivement",
            on_click=self._handle_delete,
        )

    def _handle_selection(
        self,
        selected: bool,
    ) -> None:
        self.on_document_selected(
            self.document,
            selected,
        )

    def _handle_open_folder(
        self,
        _event=None,
    ) -> None:
        self.on_open_folder(
            self.document
        )

    def _handle_restore(
        self,
        _event=None,
    ) -> None:
        self.on_restore(
            self.document
        )

    def _handle_delete(
        self,
        _event=None,
    ) -> None:
        self.on_delete(
            self.document
        )

    def _resolve_expiration_color(self):
        if self.document.expiration_level == "danger":
            return ft.Colors.RED_600

        if self.document.expiration_level == "warning":
            return ft.Colors.ORANGE_700

        return ft.Colors.GREEN_700
