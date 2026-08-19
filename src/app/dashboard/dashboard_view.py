from __future__ import annotations

from collections.abc import Callable

import flet as ft
from papernestextension import (
    PaperNestFilePickerFilesChangedEvent,
    PaperNestFilePickerValidationEvent,
)

from app.dashboard.builder import DashboardBuilder
from app.dashboard.controller import DashboardController
from app.dashboard.state import DashboardState
from app.detail.detail_view import DetailView
from app.notifications import notifications
from app.theme.tokens import AppSpacing


class DashboardView(ft.Column):
    """Relie l’état, le contrôleur et l’affichage du dashboard."""

    def __init__(
        self,
        page: ft.Page,
        on_detail_changed: Callable[[bool], None] | None = None,
    ):
        self.app_page = page
        self.on_detail_changed = on_detail_changed
        self.state = DashboardState()
        self.detail_view: DetailView | None = None
        self._mounted = False
        self._notified_detail_state = False

        self.builder = DashboardBuilder(
            on_category_click=self.show_cabinet_details,
            on_browse=self.browse_files,
            on_clear=self.clear_staged_files,
            on_commit=self.finalize_storage,
            on_default_category=self.apply_default_category,
            on_keep_duplicates=self.handle_keep_duplicates,
            on_files_changed=self.handle_files_changed,
            on_validation_error=self.handle_validation_error,
            on_duplicate_file=self.handle_duplicate_file,
        )
        self.cabinet_panel = self.builder.cabinet_panel
        self.upload_panel = self.builder.upload_panel
        self.controller = DashboardController(
            state=self.state,
            file_picker=self.upload_panel.file_picker,
            on_state_changed=self.render,
        )
        self.main_dashboard_controls = self.builder.build_main_controls()

        super().__init__(
            expand=True,
            spacing=AppSpacing.LG,
            scroll=ft.ScrollMode.AUTO,
            controls=list(self.main_dashboard_controls),
        )

        self.controller.subscribe()
        self.controller.load_categories()

    def did_mount(self) -> None:
        self._mounted = True
        self.controller.subscribe()
        self.controller.load_categories()

    def will_unmount(self) -> None:
        self._mounted = False
        self.controller.unsubscribe()
        self._dispose_detail_view()

    def dispose(self) -> None:
        self._mounted = False
        self._dispose_detail_view()
        self.controller.dispose()

    def show_cabinet_details(self, category: dict) -> None:
        self.controller.open_category(category)

    def show_main_dashboard(self, _event=None) -> None:
        self.controller.show_dashboard()

    async def browse_files(self, _event=None) -> None:
        await self.controller.browse_files(self.handle_picker_error)

    def handle_picker_error(self, _error: RuntimeError) -> None:
        notifications(self.app_page).error(
            "Impossible d’ouvrir le sélecteur de fichiers."
        )

    def handle_files_changed(
        self,
        event: PaperNestFilePickerFilesChangedEvent,
    ) -> None:
        default_category = (
            str(self.upload_panel.category_selector.value)
            if self.upload_panel.category_selector.value
            else None
        )
        invalid_paths = self.controller.set_selected_files(
            list(event.selected_files),
            default_category,
        )
        if invalid_paths:
            notifications(self.app_page).warning(
                "Certains fichiers sélectionnés ne fournissent pas "
                "de chemin local exploitable."
            )

    def handle_validation_error(
        self,
        event: PaperNestFilePickerValidationEvent,
    ) -> None:
        notifications(self.app_page).warning(
            event.message
            or "Ce fichier ne respecte pas les contraintes de sélection."
        )

    def handle_duplicate_file(self, _event) -> None:
        notifications(self.app_page).warning(
            "Ce fichier est déjà présent dans la sélection."
        )

    def apply_default_category(self, _event=None) -> None:
        category_key = (
            str(self.upload_panel.category_selector.value)
            if self.upload_panel.category_selector.value
            else None
        )
        self.controller.apply_default_category(category_key)

    def handle_row_category(self, event) -> None:
        self.controller.set_file_category(
            int(event.control.data),
            str(event.control.value) if event.control.value else None,
        )

    def handle_keep_duplicates(self, event) -> None:
        self.controller.set_keep_duplicates(bool(event.control.value))

    def remove_file(self, event) -> None:
        self.app_page.run_task(
            self.controller.remove_file,
            int(event.control.data),
        )

    def clear_staged_files(self, _event=None) -> None:
        self.app_page.run_task(self.controller.clear_files)

    def finalize_storage(self, _event=None) -> None:
        validation_error = self.controller.validate_import()
        if validation_error:
            notifications(self.app_page).warning(validation_error)
            return
        self.app_page.run_task(self.run_batch_storage)

    async def run_batch_storage(self) -> None:
        result = await self.controller.import_files()
        notifications(self.app_page).success(
            "Import terminé : "
            f"{result.imported} classé(s), "
            f"{result.duplicates} doublon(s) ignoré(s), "
            f"{result.errors} erreur(s)."
        )

    def render(self) -> None:
        category_options = self.builder.build_category_options(
            self.state.available_categories
        )
        file_rows = self.builder.build_file_rows(
            self.state,
            category_options,
            self.handle_row_category,
            self.remove_file,
        )
        self.cabinet_panel.render(self.state.categories)
        self.upload_panel.render(
            self.state,
            category_options,
            file_rows,
        )

        if self.state.showing_detail:
            self._show_detail()
        else:
            self._show_dashboard()

        self._safe_page_update()

    def _show_detail(self) -> None:
        if self.detail_view is None and self.state.selected_category is not None:
            self.scroll = None
            self.detail_view = self.builder.build_detail_view(
                page=self.app_page,
                category=self.state.selected_category,
                on_back=self.show_main_dashboard,
            )
            self.controls = [self.detail_view]
        self._notify_detail_changed(True)

    def _show_dashboard(self) -> None:
        self._dispose_detail_view()
        self.scroll = ft.ScrollMode.AUTO
        self.controls = list(self.main_dashboard_controls)
        self._notify_detail_changed(False)

    def _notify_detail_changed(self, showing_detail: bool) -> None:
        if self._notified_detail_state == showing_detail:
            return
        self._notified_detail_state = showing_detail
        if self.on_detail_changed is not None:
            self.on_detail_changed(showing_detail)

    def _dispose_detail_view(self) -> None:
        if self.detail_view is None:
            return
        for method_name in ("unsubscribe", "dispose"):
            method = getattr(self.detail_view, method_name, None)
            if callable(method):
                method()
        self.detail_view = None

    def _safe_page_update(self) -> None:
        if not self._mounted:
            return
        try:
            self.app_page.update()
        except RuntimeError:
            pass
