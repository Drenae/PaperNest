from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.dashboard.components.cabinet_panel import CabinetPanel
from app.dashboard.components.upload_panel import UploadPanel
from app.detail.detail_view import DetailView
from app.theme.cards import PageHeader
from app.theme.tokens import AppSpacing


class DashboardBuilder:
    @staticmethod
    def build_main_controls(*, upload_panel: UploadPanel, cabinet_panel: CabinetPanel) -> list[ft.Control]:
        return [
            PageHeader(icon=ft.Icons.DASHBOARD_ROUNDED, title="Accueil", subtitle="Classez vos fichiers puis ouvrez directement " "le classeur souhaité."),
            ft.ResponsiveRow(
                spacing=AppSpacing.LG,
                run_spacing=AppSpacing.LG,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(col={"xs": 12, "md": 5, "lg": 5}, content=upload_panel),
                    ft.Container(col={"xs": 12, "md": 7, "lg": 7}, content=cabinet_panel),
                ],
            ),
        ]

    @staticmethod
    def build_detail_view(*, page: ft.Page, category: dict, on_back: Callable) -> DetailView:
        return DetailView(page=page, category_cat=category, on_back=on_back)