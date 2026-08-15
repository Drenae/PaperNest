from __future__ import annotations

import flet as ft

from app.admin.builder import AdminBuilder
from app.admin.state import AdminState
from app.theme.buttons import IconAction, OutlineButton, PrimaryButton
from app.theme.cards import AppSection
from app.theme.pickers import BaseFilePicker
from app.theme.status_bar import StatusBar
from app.theme.tokens import AppColors, AppSpacing


class BackupPanel(AppSection):
    def __init__(
        self,
        state: AdminState,
        file_picker: BaseFilePicker,
        on_create,
        on_select,
        on_refresh,
        on_open_folder,
        on_verify,
        on_restore,
    ):
        self.state = state
        self.file_picker = file_picker
        self.on_open_folder = on_open_folder
        self.on_verify = on_verify
        self.on_restore = on_restore
        self.on_refresh = on_refresh

        self.create_button = PrimaryButton(
            "Créer une sauvegarde",
            icon=ft.Icons.BACKUP_ROUNDED,
            on_click=on_create,
        )
        self.restore_button = OutlineButton(
            "Restaurer",
            icon=ft.Icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
            on_click=on_select,
        )
        self.refresh_button = IconAction(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.YELLOW,
            tooltip="Actualiser les sauvegardes",
            on_click=on_refresh,
        )
        self.status_bar = StatusBar()
        self.backups_list = ft.Column(spacing=AppSpacing.SM, tight=True)

        super().__init__(
            title="Sauvegardes",
            icon=ft.Icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
            actions=[self.refresh_button],
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.MD,
                controls=[
                    self.file_picker,
                    ft.Row(
                        spacing=AppSpacing.SM,
                        controls=[self.create_button, self.restore_button],
                    ),
                    self.status_bar,
                    ft.Divider(height=1, color=AppColors.BORDER),
                    self.backups_list,
                ],
            ),
        )

    def render(self) -> None:
        self.backups_list.controls = AdminBuilder.build_backups(
            self.state,
            on_open_folder=self.on_open_folder,
            on_verify=self.on_verify,
            on_restore=self.on_restore,
            on_retry=self.on_refresh,
        )
        if self.state.backups_error:
            self.status_bar.counter.value = ""
            self.status_bar.clear_message()
        else:
            self.status_bar.clear_message()
            self.status_bar.set_count(
                len(self.state.backups),
                "sauvegarde",
                "sauvegardes",
            )
        self.create_button.disabled = self.state.backups_loading
        self.restore_button.disabled = self.state.backups_loading
        self.refresh_button.disabled = self.state.backups_loading
        self.file_picker.disabled = self.state.backups_loading
        self.status_bar.set_loading(
            self.state.backups_loading,
            "Traitement en cours...",
        )
