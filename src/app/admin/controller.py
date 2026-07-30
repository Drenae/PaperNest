from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Callable

import flet as ft

from app.admin.state import AdminState
from app.theme.file_picker import BaseFilePicker
from core.errors.exceptions import PaperNestError
from services.backup.service import BackupService
from services.files.archive import ArchiveFileService

logger = logging.getLogger(__name__)


class AdminController:
    def __init__(
        self,
        page: ft.Page,
        file_picker: BaseFilePicker,
        state: AdminState,
        on_state_changed: Callable[[], None] | None = None,
    ):
        self.page = page
        self.file_picker = file_picker
        self.state = state
        self.on_state_changed = on_state_changed

    async def load_backups(self) -> None:
        self._set_loading(True)
        try:
            backups = await asyncio.to_thread(BackupService.list_local_backups)
            self.state.set_backups(backups)
        except PaperNestError as error:
            self.state.backups_error = str(error)
        except Exception:
            logger.exception("Impossible de charger les sauvegardes.")
            self.state.backups_error = "Impossible de charger les sauvegardes."
        finally:
            self._set_loading(False)

    async def create_backup(self) -> Path:
        self._set_loading(True)
        try:
            backup_path = await asyncio.to_thread(BackupService.create_backup)
            await self.load_backups()
            return backup_path
        finally:
            self._set_loading(False)

    async def select_backup(self, on_picker_error=None) -> str | None:
        files = await self.file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["zip"],
            dialog_title="Sélectionner une sauvegarde PaperNest",
            with_data=False,
            on_error=on_picker_error,
        )
        if not files or not files[0].path:
            return None
        return files[0].path

    async def verify_backup(self, backup_path: str) -> dict:
        self._set_loading(True)
        try:
            return await asyncio.to_thread(BackupService.verify_backup, backup_path)
        finally:
            self._set_loading(False)

    def open_backup_folder(self, backup_path: str) -> None:
        ArchiveFileService.execute_native_file_open(str(Path(backup_path).parent))

    def _set_loading(self, loading: bool) -> None:
        self.state.backups_loading = loading
        self._notify_state_changed()

    def _notify_state_changed(self) -> None:
        if self.on_state_changed:
            self.on_state_changed()
