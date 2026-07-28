import flet as ft

from app.theme.tokens import AppColors


class PreviewPlaceholder(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            border_radius=12,
            bgcolor=AppColors.CARD_BG,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.DESCRIPTION_OUTLINED,
                        size=80,
                        color=AppColors.TEXT_MUTED,
                    ),
                    ft.Text(
                        "Sélectionnez un document",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "L'aperçu apparaîtra ici.",
                        color=AppColors.TEXT_MUTED,
                    ),
                ],
            ),
        )
