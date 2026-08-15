from __future__ import annotations

import flet as ft
from papernestextension.controls.material.papernest_textfield import PaperNestTextFieldState

from app.detail.builder import DetailBuilder
from app.detail.controller import DetailController
from app.detail.state import DetailState
from app.preview import PreviewController, PreviewPanel
from app.theme.cards import PageHeader
from app.theme.forms import SearchTextField
from app.theme.status_bar import StatusBar
from core.events.event_bus import (
    DocumentDeleted,
    DocumentFavoriteChanged,
    DocumentMetadataUpdated,
    DocumentMoved,
    DocumentRenamed,
    DocumentRestored,
)
from core.events.subscription import EventSubscription
from app.theme.tokens import AppColors, AppRadius, AppSpacing
from repositories.category_repository import category_repository


class DetailView(ft.Column):
    """Exploration et gestion des documents d’un classeur."""

    COMPACT_PREVIEW_WIDTH = 1180
    DOCUMENT_EVENTS = (
        DocumentRenamed,
        DocumentMoved,
        DocumentDeleted,
        DocumentRestored,
        DocumentMetadataUpdated,
        DocumentFavoriteChanged,
    )

    def __init__(self, page: ft.Page, category_cat: dict, on_back):
        self.app_page = page
        self.on_back_callback = on_back
        self._mounted = False
        self.subscriptions = EventSubscription()

        self.state = DetailState(
            category_key=str(category_cat["key"]),
            category_name=str(category_cat["name"]),
            subcategories=category_repository.list_children(str(category_cat["key"])),
        )
        self.controller = DetailController(self.state, self.render)
        self.preview_controller = PreviewController()
        self.preview_panel = PreviewPanel(
            page=self.app_page,
            controller=self.preview_controller,
            on_close=self.close_preview,
            on_toggle_layout=self.toggle_preview_layout,
            on_previous_document=self.show_previous_document,
            on_next_document=self.show_next_document,
        )

        category_icon = getattr(ft.Icons, str(category_cat.get("icon") or ""), ft.Icons.FOLDER_ROUNDED)
        self.search_input = SearchTextField(
            hint_text=f"Rechercher dans {self.state.category_name}...",
            expand=True,
            on_search=self.handle_search,
            show_refresh_action=True,
            refresh_action_tooltip="Actualiser le classeur",
            on_refresh_action=self.handle_refresh,
        )
        self.status_bar = StatusBar()
        self.documents_list = ft.ListView(expand=True, spacing=AppSpacing.SM, padding=2)
        self.documents_panel = ft.Container(expand=5, visible=True, padding=ft.Padding.only(right=AppSpacing.XS), content=self.documents_list)
        self.content_row = ft.Row(expand=True, spacing=AppSpacing.MD, vertical_alignment=ft.CrossAxisAlignment.STRETCH, controls=[self.documents_panel, self.preview_panel])
        self.category_filters = ft.Row(spacing=AppSpacing.XS, scroll=ft.ScrollMode.AUTO, controls=DetailBuilder.build_category_filters(self.state, self.select_category_filter))
        self.search_section = ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.SM, vertical=AppSpacing.XS),
            bgcolor=AppColors.CARD_BG,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=AppRadius.MD,
            content=ft.Row(
                spacing=AppSpacing.XS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.search_input],
            ),
        )
        header_section = ft.Column(
            tight=True,
            spacing=AppSpacing.SM,
            controls=[
                PageHeader(
                    title=self.state.category_name,
                    subtitle="Visualisation et gestion locale de vos documents.",
                    icon=category_icon,
                    on_back=self.on_back_callback,
                ),
                ft.Container(content=self.category_filters) if self.state.subcategories else ft.Container(visible=False),
                self.search_section,
                self.status_bar,
            ],
        )
        super().__init__(expand=True, spacing=AppSpacing.MD, controls=[header_section, self.content_row])
        self.subscribe()
        self.app_page.run_task(self.controller.load_documents)

    def did_mount(self) -> None:
        self._mounted = True
        self.subscribe()

    def will_unmount(self) -> None:
        self._mounted = False
        self.unsubscribe()
        self.controller.dispose()

    def dispose(self) -> None:
        self._mounted = False
        self.unsubscribe()
        self.controller.dispose()
        self.preview_controller.clear()

    def subscribe(self) -> None:
        self.subscriptions.add_many(self.DOCUMENT_EVENTS, self.handle_document_event)

    def unsubscribe(self) -> None:
        self.subscriptions.clear()

    def handle_document_event(self, _event) -> None:
        if self._mounted:
            self.app_page.run_task(self.controller.search_now, self.get_search_query())

    def select_category_filter(self, category_key: str) -> None:
        generation = self.controller.select_category(category_key)
        self.category_filters.controls = DetailBuilder.build_category_filters(
            self.state, self.select_category_filter
        )
        self.app_page.run_task(self.controller.load_documents, self.get_search_query(), generation)
        self.safe_update()

    async def handle_search(self, _event) -> None:
        await self.controller.search_now(self.get_search_query())

    def handle_refresh(self, _event=None) -> None:
        if not self.state.loading:
            self.app_page.run_task(self.controller.search_now, self.get_search_query())

    async def refresh_after_change(self) -> None:
        await self.controller.search_now(self.get_search_query())

    def show_preview(self, document) -> None:
        self.select_document(document, adapt_layout=True)

    def select_document(self, document, *, adapt_layout: bool = False) -> None:
        compact = self.get_available_width() < self.COMPACT_PREVIEW_WIDTH if adapt_layout else None
        self.controller.select_document(document.document_id, preview_full_width=compact)
        self.preview_controller.select_file(
            document.absolute_path,
            document.name,
            category_name=self.state.category_name,
            file_size=document.file_size,
        )
        self.preview_panel.show_document()
        self.update_document_navigation()
        self.apply_preview_layout()
        self.render_document_cards()
        self.safe_page_update()

    def show_previous_document(self) -> None:
        document = self.controller.previous_document()
        if document is not None:
            self.select_document(document)

    def show_next_document(self) -> None:
        document = self.controller.next_document()
        if document is not None:
            self.select_document(document)

    def update_document_navigation(self) -> None:
        index = self.state.selected_document_index
        if index is None:
            self.preview_panel.set_document_navigation(has_previous=False, has_next=False)
            return
        self.preview_panel.set_document_navigation(
            has_previous=index > 0,
            has_next=index < len(self.state.documents) - 1,
        )

    def toggle_preview_layout(self) -> None:
        if self.preview_panel.visible:
            self.controller.toggle_preview_layout()
            self.apply_preview_layout()
            self.safe_page_update()

    def apply_preview_layout(self) -> None:
        if not self.preview_panel.visible:
            self.documents_panel.visible = True
            self.documents_panel.expand = 5
            self.preview_panel.expand = 6
            self.preview_panel.set_full_width(False)
        elif self.state.preview_full_width:
            self.documents_panel.visible = False
            self.preview_panel.expand = 1
            self.preview_panel.set_full_width(True)
        else:
            self.documents_panel.visible = True
            self.documents_panel.expand = 5
            self.preview_panel.expand = 6
            self.preview_panel.set_full_width(False)

    def close_preview(self, _event=None, *, update_page: bool = True) -> None:
        self.controller.close_preview()
        self.preview_panel.clear()
        self.preview_panel.set_document_navigation(has_previous=False, has_next=False)
        self.apply_preview_layout()
        self.render_document_cards()
        if update_page:
            self.safe_page_update()

    def refresh_selected_preview(self) -> None:
        document = self.state.selected_document
        if document is None:
            if self.preview_panel.visible:
                self.close_preview(update_page=False)
            return
        self.preview_controller.select_file(
            document.absolute_path,
            document.name,
            category_name=self.state.category_name,
            file_size=document.file_size,
        )
        self.preview_panel.show_document()
        self.update_document_navigation()
        self.apply_preview_layout()

    def render_document_cards(self) -> None:
        self.documents_list.controls = DetailBuilder.build_documents(
            self.state,
            self.app_page,
            self.show_preview,
            self.refresh_after_change,
            self.handle_refresh,
        )

    def render(self) -> None:
        self.render_document_cards()
        self.category_filters.controls = DetailBuilder.build_category_filters(
            self.state, self.select_category_filter
        )
        self.search_input.searching = self.state.loading
        self.search_input.refresh_action_disabled = self.state.loading
        self.search_input.state = (
            PaperNestTextFieldState.ERROR
            if self.state.error_message
            else PaperNestTextFieldState.NORMAL
        )
        self.search_input.state_message = self.state.error_message or None

        if self.state.error_message:
            self.status_bar.counter.value = ""
            self.status_bar.clear_message()
        else:
            singular, plural = ("résultat", "résultats") if self.state.search_query else ("document", "documents")
            self.status_bar.clear_message()
            self.status_bar.set_count(len(self.state.documents), singular, plural)

        self.status_bar.set_loading(self.state.loading, "Chargement...")
        self.refresh_selected_preview()
        self.update_document_navigation()
        self.safe_page_update()

    def get_available_width(self) -> float:
        return float(getattr(self.app_page, "width", 0) or 0)

    def get_search_query(self) -> str:
        return self.search_input.value.strip() if self.search_input.value else ""

    def safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass

    def safe_page_update(self) -> None:
        try:
            self.app_page.update()
        except RuntimeError:
            pass

    @staticmethod
    def safe_update_control(control: ft.Control) -> None:
        try:
            control.update()
        except RuntimeError:
            pass
