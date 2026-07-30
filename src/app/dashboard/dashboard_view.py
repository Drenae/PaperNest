from __future__ import annotations

import flet as ft

from app.theme.tokens import AppColors, AppSpacing
from app.theme.cards import PageHeader
from app.dashboard.components.cabinet_panel import CabinetPanel
from app.dashboard.components.upload_panel import UploadPanel
from app.detail.detail_view import DetailView


class DashboardView(ft.Column):
    """Accueil volontairement simple : import à gauche, classeurs à droite."""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=AppSpacing.LG, scroll=ft.ScrollMode.AUTO)
        self.app_page = page
        self.detail_view: DetailView | None = None

        self.processing_bar = ft.ProgressBar(
            value=0,
            visible=False,
            color=AppColors.PRIMARY_DARK,
            bgcolor=AppColors.PANEL,
            border_radius=4,
        )
        self.cabinet_panel = CabinetPanel(
            on_category_click=self.show_cabinet_details
        )
        self.upload_panel = UploadPanel(
            page=page,
            processing_bar=self.processing_bar,
            on_storage_done=self.handle_storage_done,
        )
        self.main_dashboard_controls = self._build_main_dashboard_controls()
        self.controls = list(self.main_dashboard_controls)

    def _build_main_dashboard_controls(self) -> list[ft.Control]:
        return [
            PageHeader(
                icon=ft.Icons.DASHBOARD_ROUNDED,
                title="Accueil",
                subtitle="Classez vos fichiers puis ouvrez directement le classeur souhaité.",
            ),
            ft.ResponsiveRow(
                spacing=AppSpacing.LG,
                run_spacing=AppSpacing.LG,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 5, "lg": 5},
                        content=self.upload_panel,
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 7, "lg": 7},
                        content=self.cabinet_panel,
                    ),
                ],
            ),
        ]

    def handle_storage_done(self, _event=None) -> None:
        self.cabinet_panel.refresh_grid_ui()
        self._safe_page_update()

    def show_cabinet_details(self, category_cat: dict) -> None:
        self._dispose_detail_view()
        self.scroll = None
        self.detail_view = DetailView(
            page=self.app_page,
            category_cat=category_cat,
            on_back=self.show_main_dashboard,
        )
        self.controls = [self.detail_view]
        self._safe_page_update()

    def show_main_dashboard(self, _event=None) -> None:
        self._dispose_detail_view()
        self.scroll = ft.ScrollMode.AUTO
        self.cabinet_panel.refresh_grid_ui()
        self.controls = list(self.main_dashboard_controls)
        self._safe_page_update()

    def _dispose_detail_view(self) -> None:
        if self.detail_view is None:
            return
        for method_name in ("unsubscribe", "dispose"):
            method = getattr(self.detail_view, method_name, None)
            if callable(method):
                method()
        self.detail_view = None

    def dispose(self) -> None:
        self._dispose_detail_view()
        for component in (self.cabinet_panel, self.upload_panel):
            for method_name in ("unsubscribe", "dispose"):
                method = getattr(component, method_name, None)
                if callable(method):
                    method()

    def _safe_page_update(self) -> None:
        try:
            self.app_page.update()
        except RuntimeError:
            pass
