from __future__ import annotations

import asyncio
import logging

import flet as ft

from app.admin.builder import AdminBuilder
from app.admin.components.backup_panel import BackupPanel
from app.admin.components.category_panel import CategoryPanel
from app.admin.controller import AdminController
from app.admin.dialogs.category_editor_dialog import CategoryEditorDialog
from app.admin.dialogs.delete_category_dialog import DeleteCategoryDialog
from app.admin.dialogs.restore_backup_dialog import RestoreBackupDialog
from app.admin.state import AdminState
from app.notifications import notifications
from app.theme.file_picker import BaseFilePicker
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppSpacing

logger = logging.getLogger(__name__)


class AdminView(ft.Column):
    """Administration centralisée : sauvegardes et gestion des classeurs."""

    def __init__(
        self,
        page: ft.Page,
        on_categories_changed=None,
        on_restore_done=None,
    ):
        self.app_page = page
        self.on_categories_changed = on_categories_changed
        self.on_restore_done = on_restore_done
        self.state = AdminState()

        self.backup_file_picker = BaseFilePicker(
            drag_and_drop=False,
            click_to_pick=False,
            allow_multiple=False,
            allowed_extensions=["zip"],
            show_file_list=False,
            show_file_size=False,
            show_constraints=False,
            content=ft.Container(width=0, height=0),
            width=0,
            height=0,
        )
        self.controller = AdminController(
            page=page,
            file_picker=self.backup_file_picker,
            state=self.state,
            on_state_changed=self.render,
        )

        self.backup_panel = BackupPanel(
            state=self.state,
            file_picker=self.backup_file_picker,
            on_create=self.create_backup,
            on_select=self.select_backup,
            on_refresh=lambda _event: self.app_page.run_task(self.controller.load_backups),
            on_open_folder=self.open_backup_folder,
            on_verify=self.verify_backup,
            on_restore=self.show_restore_dialog,
        )
        self.category_panel = CategoryPanel(
            page=self.app_page,
            on_add_parent=self.show_create_dialog,
            on_add_child=self.show_create_subcategory_dialog,
            on_rename=self.show_edit_dialog,
            on_delete=self.show_delete_dialog,
        )

        super().__init__(
            expand=True,
            spacing=AppSpacing.LG,
            scroll=ft.ScrollMode.AUTO,
            controls=AdminBuilder.build_layout(self.backup_panel, self.category_panel),
        )
        self.app_page.run_task(self.controller.load_backups)

    def create_backup(self, _event=None) -> None:
        self.app_page.run_task(self.run_create_backup)

    async def run_create_backup(self) -> None:
        try:
            backup_path = await self.controller.create_backup()
            notifications(self.app_page).success(f"Sauvegarde créée : {backup_path.name}")
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))
        except Exception:
            logger.exception("Impossible de créer la sauvegarde.")
            notifications(self.app_page).error("Impossible de créer la sauvegarde.")

    async def select_backup(self, _event=None) -> None:
        backup_path = await self.controller.select_backup(self.handle_picker_error)
        if backup_path:
            await self.backup_file_picker.clear_files()
            self.show_restore_dialog(backup_path)

    def handle_picker_error(self, error: RuntimeError) -> None:
        message = str(error)
        if "TimeoutException" in message or "Timeout waiting" in message:
            notifications(self.app_page).warning(
                "Le sélecteur de fichiers n’a pas répondu. Fermez toute fenêtre de sélection encore ouverte puis réessayez."
            )
        else:
            notifications(self.app_page).error("Impossible d’ouvrir le sélecteur de fichiers.")

    def verify_backup(self, backup_path: str) -> None:
        self.app_page.run_task(self.run_verify_backup, backup_path)

    async def run_verify_backup(self, backup_path: str) -> None:
        try:
            manifest = await self.controller.verify_backup(backup_path)
            count = int(manifest["document_count"])
            label = "document" if count == 1 else "documents"
            notifications(self.app_page).success(f"Sauvegarde valide : {count} {label}.")
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))
        except Exception:
            logger.exception("Impossible de vérifier la sauvegarde.")
            notifications(self.app_page).error("Impossible de vérifier la sauvegarde.")

    def open_backup_folder(self, backup_path: str) -> None:
        try:
            self.controller.open_backup_folder(backup_path)
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))

    def show_restore_dialog(self, backup_path: str) -> None:
        RestoreBackupDialog(
            page=self.app_page,
            backup_path=backup_path,
            on_restored=self.handle_backup_restored,
        ).show()

    async def handle_backup_restored(self, result: dict) -> None:
        count = int(result["document_count"])
        label = "document" if count == 1 else "documents"
        notifications(self.app_page).success(f"Restauration terminée : {count} {label}.")
        await self.controller.load_backups()
        if self.on_restore_done:
            callback_result = self.on_restore_done()
            if asyncio.iscoroutine(callback_result):
                await callback_result

    def show_create_dialog(self, _event=None) -> None:
        CategoryEditorDialog(page=self.app_page, on_saved=self.handle_category_saved).show()

    def show_create_subcategory_dialog(self, parent: dict) -> None:
        CategoryEditorDialog(
            page=self.app_page,
            parent=parent,
            on_saved=self.handle_category_saved,
        ).show()

    def show_edit_dialog(self, category: dict) -> None:
        CategoryEditorDialog(
            page=self.app_page,
            category=category,
            on_saved=self.handle_category_saved,
        ).show()

    async def handle_category_saved(self, category: dict) -> None:
        notifications(self.app_page).success(
            f"Le classeur « {category['name']} » a été enregistré."
        )
        self.notify_categories_changed()

    def show_delete_dialog(self, category: dict) -> None:
        DeleteCategoryDialog(
            page=self.app_page,
            category=category,
            on_deleted=self.handle_category_deleted,
        ).show()

    async def handle_category_deleted(self, category: dict) -> None:
        notifications(self.app_page).success(
            f"Le classeur « {category['name']} » a été supprimé."
        )
        self.notify_categories_changed()

    def notify_categories_changed(self) -> None:
        if self.on_categories_changed:
            result = self.on_categories_changed()
            if asyncio.iscoroutine(result):
                self.app_page.run_task(lambda: result)
        self.category_panel.refresh()

    def render(self) -> None:
        self.backup_panel.render()
        if self.state.backups_error:
            notifications(self.app_page).error(self.state.backups_error)
        self.safe_update()

    def unsubscribe(self) -> None:
        self.category_panel.unsubscribe()

    def safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
