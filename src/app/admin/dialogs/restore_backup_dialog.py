import asyncio
import logging
from pathlib import Path

import flet as ft

from app.theme.dialogs import ConfirmDialog, DialogVariant
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors
from services.backup.service import BackupService


logger = logging.getLogger(__name__)


class RestoreBackupDialog:
    def __init__(self, page: ft.Page, backup_path: str, on_restored=None):
        self.page = page
        self.backup_path = backup_path
        self.on_restored = on_restored
        self.dialog: ConfirmDialog | None = None

    def show(self) -> None:
        backup_name = Path(self.backup_path).name

        self.error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        self.dialog = ConfirmDialog(
            modal=True,
            title="Restaurer une sauvegarde",
            icon=ft.Icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
            variant=DialogVariant.WARNING,
            on_confirm=self.restore,
            on_cancel=lambda event: self.close(),
            confirm_text="Restaurer",
            confirm_icon=ft.Icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        "La restauration remplacera les documents "
                        "et la base de données actuels."
                    ),
                    ft.Text(
                        backup_name,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Une sauvegarde de sécurité sera créée "
                        "automatiquement avant la restauration.",
                        color=AppColors.TEXT_MUTED,
                    ),
                    self.error_text,
                ],
            ),
        )
        self.restore_button = self.dialog.confirm_button

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    async def restore(self, event) -> None:
        self.restore_button.disabled = True
        self.error_text.value = ""
        self.page.update()

        try:
            result = await asyncio.to_thread(
                BackupService.restore_backup,
                self.backup_path,
            )

            self.close()

            if self.on_restored:
                callback_result = self.on_restored(result)

                if asyncio.iscoroutine(callback_result):
                    await callback_result

        except PaperNestError as error:
            self.show_error(str(error))

        except Exception:
            logger.exception(
                "Impossible de restaurer la sauvegarde %s.",
                self.backup_path,
            )

            self.show_error(
                "Impossible de restaurer la sauvegarde."
            )

    def show_error(self, message: str) -> None:
        self.error_text.value = message
        self.restore_button.disabled = False
        self.page.update()

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()
