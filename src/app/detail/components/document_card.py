from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

import flet as ft

from app.detail.dialogs.delete_dialog import DeleteDialog
from app.detail.dialogs.metadata_dialog import MetadataDialog
from app.detail.dialogs.move_dialog import MoveDialog
from app.detail.dialogs.rename_dialog import RenameDialog
from app.notifications import notifications
from app.theme.cards import AppCard, CardVariant
from app.theme.buttons import IconAction
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors
from services.files.archive import ArchiveFileService
from services.documents.metadata import metadata_service


class DocumentCard(AppCard):
    """
    Adaptateur métier de la carte universelle pour DetailView.

    Cette classe conserve les actions propres à la gestion d’un document,
    tandis que BaseDocumentCard assure uniquement la présentation.
    """

    def __init__(
        self,
        page: ft.Page,
        document,
        searching: bool = False,
        selected: bool = False,
        on_preview=None,
        on_changed=None,
    ):
        self.app_page = page
        self.document = document
        self.searching = searching
        self.on_preview = on_preview
        self.on_changed = on_changed

        super().__init__(
            title=self.document.name,
            extension=self.document.extension,
            metadata=self._build_metadata(),
            tags=self.document.tags,
            variant=(
                CardVariant.SEARCH
                if searching
                else CardVariant.DOCUMENT
            ),
            selected=selected,
            favorite=self.document.is_favorite,
            tooltip=(
                f"Afficher l’aperçu de {self.document.name}"
            ),
            on_click=self.preview_document,
            actions=[
                self._build_favorite_action(),
                self._build_metadata_action(),
            ],
            menu_items=self._build_menu_items(),
        )

    def _build_metadata(self) -> list[str]:
        parts = [
            f"Taille : {self.document.file_size}"
        ]

        if self.document.person_name:
            parts.append(
                f"Personne : {self.document.person_name}"
            )

        if self.document.document_date:
            parts.append(
                f"Date : {self._format_date(self.document.document_date)}"
            )

        if self.document.due_date:
            parts.append(
                f"Échéance : {self._format_date(self.document.due_date)}"
            )

        if self.document.amount:
            parts.append(
                f"Montant : {self._format_amount(self.document.amount)}"
            )

        if (
            self.searching
            and self.document.match_reason
        ):
            parts.append(
                self.document.match_reason
            )

        return parts

    def _build_favorite_action(self) -> ft.IconButton:
        is_favorite = bool(
            self.document.is_favorite
        )

        return IconAction(
            icon=(
                ft.Icons.STAR_ROUNDED
                if is_favorite
                else ft.Icons.STAR_BORDER_ROUNDED
            ),
            icon_color=(
                ft.Colors.AMBER_600
                if is_favorite
                else AppColors.TEXT_MUTED
            ),
            tooltip=(
                "Retirer des favoris"
                if is_favorite
                else "Ajouter aux favoris"
            ),
            on_click=self.toggle_favorite,
        )

    def _build_metadata_action(self) -> ft.IconButton:
        return IconAction(
            icon=ft.Icons.INFO_OUTLINE_ROUNDED,
            icon_color=AppColors.SECONDARY,
            tooltip="Informations du document",
            on_click=self.handle_metadata_click,
        )

    def _build_menu_items(
        self,
    ) -> list[ft.PopupMenuItem]:
        return [
            ft.PopupMenuItem(
                content=self._menu_content(
                    ft.Icons.OPEN_IN_NEW_ROUNDED,
                    "Ouvrir dans Windows",
                ),
                on_click=self.handle_open_click,
            ),
            ft.PopupMenuItem(
                content=self._menu_content(
                    ft.Icons.DRIVE_FILE_RENAME_OUTLINE,
                    "Renommer",
                ),
                on_click=self.handle_rename_click,
            ),
            ft.PopupMenuItem(
                content=self._menu_content(
                    ft.Icons.DRIVE_FILE_MOVE_ROUNDED,
                    "Déplacer",
                ),
                on_click=self.handle_move_click,
            ),
            ft.PopupMenuItem(
                content=self._menu_content(
                    ft.Icons.FOLDER_OPEN_ROUNDED,
                    "Ouvrir le dossier",
                ),
                on_click=self.handle_open_folder_click,
            ),
            ft.PopupMenuItem(
                content=ft.Divider(
                    height=1,
                    color=AppColors.BORDER,
                ),
                disabled=True,
            ),
            ft.PopupMenuItem(
                content=self._menu_content(
                    ft.Icons.DELETE_OUTLINE_ROUNDED,
                    "Mettre à la corbeille",
                    ft.Colors.RED_500,
                ),
                on_click=self.handle_delete_click,
            ),
        ]

    @staticmethod
    def _menu_content(
        icon,
        label: str,
        color=None,
    ) -> ft.Row:
        resolved_color = (
            color
            if color is not None
            else AppColors.TEXT_MAIN
        )

        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    icon,
                    size=18,
                    color=resolved_color,
                ),
                ft.Text(
                    label,
                    color=resolved_color,
                ),
            ],
        )

    def preview_document(
        self,
        event=None,
    ) -> None:
        if self.on_preview is not None:
            self.on_preview(
                self.document
            )

    def handle_metadata_click(
        self,
        event=None,
    ) -> None:
        self.show_metadata_dialog()

    def handle_open_click(
        self,
        event=None,
    ) -> None:
        self.open_document()

    def handle_rename_click(
        self,
        event=None,
    ) -> None:
        self.show_rename_dialog()

    def handle_move_click(
        self,
        event=None,
    ) -> None:
        self.show_move_dialog()

    def handle_open_folder_click(
        self,
        event=None,
    ) -> None:
        self.open_parent_folder()

    def handle_delete_click(
        self,
        event=None,
    ) -> None:
        self.show_delete_dialog()

    def toggle_favorite(
        self,
        event=None,
    ) -> None:
        if self.document.document_id is None:
            notifications(
                self.app_page
            ).error(
                "Ce document ne possède pas d’identifiant."
            )
            return

        self.app_page.run_task(
            self._run_toggle_favorite
        )

    async def _run_toggle_favorite(
        self,
    ) -> None:
        try:
            new_value = await asyncio.to_thread(
                metadata_service.toggle_favorite,
                self.document.document_id,
            )

            notifications(
                self.app_page
            ).success(
                (
                    "Document ajouté aux favoris."
                    if new_value
                    else "Document retiré des favoris."
                )
            )

            await self._notify_changed()

        except PaperNestError as error:
            notifications(
                self.app_page
            ).error(
                str(error)
            )

        except Exception:
            notifications(
                self.app_page
            ).error(
                "Impossible de modifier le favori."
            )

    def show_metadata_dialog(
        self,
    ) -> None:
        dialog = MetadataDialog(
            page=self.app_page,
            document=self.document,
            on_saved=self._handle_metadata_saved,
        )

        self.app_page.run_task(
            dialog.show
        )

    async def _handle_metadata_saved(
        self,
    ) -> None:
        await self._notify_changed()

    def show_rename_dialog(
        self,
    ) -> None:
        RenameDialog(
            page=self.app_page,
            document=self.document,
            on_renamed=self._handle_renamed,
        ).show()

    async def _handle_renamed(
        self,
        destination: Path,
    ) -> None:
        notifications(
            self.app_page
        ).success(
            f"Document renommé : {destination.name}"
        )

        await self._notify_changed()

    def show_move_dialog(
        self,
    ) -> None:
        MoveDialog(
            page=self.app_page,
            document=self.document,
            on_moved=self._handle_moved,
        ).show()

    async def _handle_moved(
        self,
        destination: Path,
    ) -> None:
        notifications(
            self.app_page
        ).success(
            (
                "Document déplacé vers "
                f"{destination.parent.name}."
            )
        )

        await self._notify_changed()

    def show_delete_dialog(
        self,
    ) -> None:
        DeleteDialog(
            page=self.app_page,
            document=self.document,
            on_deleted=self._handle_deleted,
        ).show()

    async def _handle_deleted(
        self,
    ) -> None:
        notifications(
            self.app_page
        ).success(
            "Document placé dans la corbeille."
        )

        await self._notify_changed()

    async def _notify_changed(
        self,
    ) -> None:
        if self.on_changed is None:
            return

        result = self.on_changed()

        if asyncio.iscoroutine(result):
            await result

    def open_document(
        self,
    ) -> None:
        try:
            ArchiveFileService.execute_native_file_open(
                self.document.absolute_path
            )

        except PaperNestError as error:
            notifications(
                self.app_page
            ).error(
                str(error)
            )

    def open_parent_folder(
        self,
    ) -> None:
        try:
            parent_directory = Path(
                self.document.absolute_path
            ).parent

            ArchiveFileService.execute_native_file_open(
                str(parent_directory)
            )

        except PaperNestError as error:
            notifications(
                self.app_page
            ).error(
                str(error)
            )

    @staticmethod
    def _format_date(
        value: str,
    ) -> str:
        try:
            return date.fromisoformat(
                value
            ).strftime(
                "%d/%m/%Y"
            )

        except (TypeError, ValueError):
            return str(
                value or ""
            )

    @staticmethod
    def _format_amount(
        value: str,
    ) -> str:
        try:
            formatted = (
                f"{Decimal(value):,.2f}"
            )

            formatted = (
                formatted
                .replace(",", " ")
                .replace(".", ",")
            )

            return f"{formatted} €"

        except Exception:
            return f"{value} €"
