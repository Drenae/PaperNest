from __future__ import annotations

import flet as ft

from app.settings.components import AppearancePanel, TrashSettingsPanel
from app.theme.cards import HeaderCard
from app.theme.tokens import AppSpacing


class SettingsView(ft.Column):
    """Réglages personnalisables de l’application PaperNest."""

    def __init__(self, page: ft.Page) -> None:
        super().__init__(
            expand=True,
            spacing=AppSpacing.LG,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                HeaderCard(
                    title="Paramètres",
                    subtitle="Personnalisez le fonctionnement et l’apparence de PaperNest.",
                    icon=ft.Icons.SETTINGS_ROUNDED,
                ),
                ft.ResponsiveRow(
                    spacing=AppSpacing.LG,
                    run_spacing=AppSpacing.LG,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            col={"sm": 12, "xl": 8},
                            content=AppearancePanel(page),
                        ),
                        ft.Container(
                            col={"sm": 12, "xl": 4},
                            content=TrashSettingsPanel(page),
                        ),
                    ],
                ),
            ],
        )
