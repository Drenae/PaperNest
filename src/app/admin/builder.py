from __future__ import annotations

import flet as ft

from app.admin.state import AdminState
from app.theme.buttons import IconAction
from app.theme.cards import AppCard, CardDensity, CardOrientation, HeaderCard
from app.theme.state_view import StateView
from app.theme.tokens import AppColors, AppSpacing


class AdminBuilder:
    @staticmethod
    def build_layout(
        backup_panel: ft.Control,
        category_panel: ft.Control,
        appearance_panel: ft.Control,
    ) -> list[ft.Control]:
        return [
            HeaderCard(
                icon=ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED,
                title="Administration",
                subtitle="Protégez vos données et gérez les classeurs PaperNest.",
            ),
            ft.ResponsiveRow(
                spacing=AppSpacing.LG,
                run_spacing=AppSpacing.LG,
                controls=[
                    ft.Container(col={"sm": 12, "lg": 5}, content=backup_panel),
                    ft.Container(col={"sm": 12, "lg": 7}, content=category_panel),
                ],
            ),
            appearance_panel,
        ]

    @staticmethod
    def build_backups(
        state: AdminState,
        on_open_folder,
        on_verify,
        on_restore,
        on_retry,
    ) -> list[ft.Control]:
        if state.backups_error:
            return [
                StateView.error(
                    state.backups_error,
                    action_text="Réessayer",
                    on_action=on_retry,
                )
            ]
        if not state.backups:
            return [
                StateView.empty(
                    title="Aucune sauvegarde",
                    message="Créez une première sauvegarde pour protéger les données PaperNest.",
                    icon=ft.Icons.BACKUP_OUTLINED,
                )
            ]
        return [
            AdminBuilder.build_backup_card(
                backup,
                on_open_folder=on_open_folder,
                on_verify=on_verify,
                on_restore=on_restore,
            )
            for backup in state.backups
        ]

    @staticmethod
    def build_backup_card(backup: dict, on_open_folder, on_verify, on_restore) -> AppCard:
        backup_path = str(backup["path"])
        return AppCard(
            title=str(backup["name"]),
            subtitle=f"{backup['size']}   •   {backup['modified_at']}",
            icon=ft.Icons.ARCHIVE_OUTLINED,
            icon_color=AppColors.SECONDARY,
            icon_bgcolor=ft.Colors.BLUE_50,
            orientation=CardOrientation.HORIZONTAL,
            density=CardDensity.COMPACT,
            shadow=False,
            actions=[
                IconAction(
                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                    tooltip="Ouvrir le dossier",
                    icon_color=AppColors.SECONDARY,
                    on_click=lambda _event, path=backup_path: on_open_folder(path),
                ),
                IconAction(
                    icon=ft.Icons.VERIFIED_OUTLINED,
                    tooltip="Vérifier la sauvegarde",
                    icon_color=ft.Colors.GREEN_700,
                    on_click=lambda _event, path=backup_path: on_verify(path),
                ),
                IconAction(
                    icon=ft.Icons.SETTINGS_BACKUP_RESTORE_ROUNDED,
                    tooltip="Restaurer cette sauvegarde",
                    icon_color=ft.Colors.ORANGE_700,
                    on_click=lambda _event, path=backup_path: on_restore(path),
                ),
            ],
        )
