from __future__ import annotations

import flet as ft

from app.notifications import notifications
from app.theme.buttons import PrimaryButton
from app.theme.cards import Section
from app.theme.forms import BaseNumberField
from app.theme.tokens import AppColors, AppSpacing
from core.models.trash_settings import (
    MAX_TRASH_RETENTION_DAYS,
    MIN_TRASH_RETENTION_DAYS,
)
from services.settings import trash_settings_service


class TrashSettingsPanel(Section):
    def __init__(self, page: ft.Page) -> None:
        self.app_page = page
        retention_days = trash_settings_service.get_retention_days()
        self.retention_field = BaseNumberField(
            label="Durée de conservation (jours)",
            value=str(retention_days),
            icon=ft.Icons.SCHEDULE_ROUNDED,
        )
        self.save_button = PrimaryButton(
            "Enregistrer",
            icon=ft.Icons.SAVE_ROUNDED,
            on_click=self._save,
        )

        super().__init__(
            title="Corbeille",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            content=ft.Column(
                spacing=AppSpacing.MD,
                controls=[
                    ft.Text(
                        "Choisissez combien de jours les documents supprimés "
                        "restent récupérables.",
                        size=12,
                        color=AppColors.TEXT_MUTED,
                    ),
                    self.retention_field,
                    ft.Text(
                        f"Valeur autorisée : {MIN_TRASH_RETENTION_DAYS} à "
                        f"{MAX_TRASH_RETENTION_DAYS} jours. La nouvelle durée "
                        "sera utilisée lors du prochain nettoyage automatique.",
                        size=11,
                        color=AppColors.TEXT_MUTED,
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[self.save_button],
                    ),
                ],
            ),
        )

    def _save(self, _event=None) -> None:
        try:
            settings = trash_settings_service.save_retention_days(
                str(self.retention_field.value or "")
            )
            self.retention_field.value = str(settings.retention_days)
            notifications(self.app_page).success(
                "La durée de conservation de la corbeille a été enregistrée."
            )
            self.app_page.update()
        except ValueError as error:
            notifications(self.app_page).error(str(error))
        except OSError:
            notifications(self.app_page).error(
                "Impossible d’enregistrer les paramètres de la corbeille."
            )
