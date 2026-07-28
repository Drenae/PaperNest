from pathlib import Path

import flet as ft

from app.theme.tokens import AppColors, AppSpacing


class PreviewBuilder:
    @staticmethod
    def build_preview_image(
        image_base64: str,
        *,
        min_scale: float,
        max_scale: float,
    ) -> tuple[ft.Container, ft.InteractiveViewer]:
        image_source = f"data:image/png;base64,{image_base64}"
        image_viewer = ft.InteractiveViewer(
            min_scale=min_scale,
            max_scale=max_scale,
            boundary_margin=ft.Margin.all(1000),
            pan_enabled=True,
            scale_enabled=True,
            trackpad_scroll_causes_scale=True,
            scale_factor=150,
            content=ft.Image(
                src=image_source,
                fit=ft.BoxFit.SCALE_DOWN,
                expand=True,
            ),
        )

        container = ft.Container(
            expand=True,
            padding=5,
            bgcolor=ft.Colors.GREY_200,
            border_radius=10,
            alignment=ft.Alignment.CENTER,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=image_viewer,
        )
        return container, image_viewer

    @staticmethod
    def build_loading(
        message: str = "Génération de l’aperçu...",
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(
                        width=34,
                        height=34,
                        stroke_width=3,
                    ),
                    ft.Text(
                        message,
                        color=AppColors.TEXT_MUTED,
                    ),
                ],
            ),
        )

    @staticmethod
    def build_unsupported_preview(
        file_path: Path,
        extension: str,
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=30,
            content=ft.Column(
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.INSERT_DRIVE_FILE_ROUNDED,
                        size=64,
                        color=AppColors.SECONDARY,
                    ),
                    ft.Text(
                        file_path.name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        extension.upper().lstrip(".") or "FICHIER",
                        color=AppColors.TEXT_MUTED,
                    ),
                    ft.Text(
                        "L’aperçu de ce format n’est pas encore disponible.",
                        size=12,
                        color=AppColors.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    @staticmethod
    def build_error(message: str) -> ft.Container:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.SM,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.ERROR_OUTLINE_ROUNDED,
                        size=46,
                        color=ft.Colors.RED_600,
                    ),
                    ft.Text(
                        message,
                        color=AppColors.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
