import flet as ft

from app.important.builder import ImportantBuilder
from app.important.controller import ImportantController
from app.important.state import ImportantState
from app.notifications import notifications
from app.preview import PreviewController, PreviewPanel
from app.theme.buttons import PrimaryButton
from app.theme.cards import HeaderCard
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
from app.theme.tokens import AppColors


class ImportantView(ft.Column):
    COMPACT_PREVIEW_WIDTH = 1180

    DOCUMENT_EVENTS = (
        DocumentFavoriteChanged,
        DocumentMetadataUpdated,
        DocumentDeleted,
        DocumentMoved,
        DocumentRenamed,
        DocumentRestored,
    )

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, spacing=15)

        self.app_page = page
        self.subscriptions = EventSubscription()
        self.state = ImportantState()
        self.controller = ImportantController(self.state, self.render)
        self.preview_controller = PreviewController()

        self.preview_panel = PreviewPanel(
            page=self.app_page,
            controller=self.preview_controller,
            on_close=self.close_preview,
            on_toggle_layout=self.toggle_preview_layout,
            on_previous_document=self.show_previous_document,
            on_next_document=self.show_next_document,
        )

        self.favorites_button = PrimaryButton("Favoris", icon=ft.Icons.STAR_ROUNDED, on_click=lambda event: self.change_tab("favorites"))
        self.upcoming_button = PrimaryButton("Échéances", icon=ft.Icons.EVENT_BUSY_ROUNDED, on_click=lambda event: self.change_tab("upcoming"))
        self.status_bar = StatusBar()
        self.documents_list = ft.ListView(expand=True, spacing=12, padding=2)
        self.documents_panel = ft.Container(expand=5, visible=True, content=self.documents_list)
        self.content_row = ft.Row(expand=True, spacing=15, vertical_alignment=ft.CrossAxisAlignment.STRETCH, controls=[self.documents_panel, self.preview_panel])

        self.controls = [
            ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    HeaderCard(title="Documents importants", subtitle=("Retrouvez vos favoris et les prochaines échéances."), icon=ft.Icons.STAR_ROUNDED),
                    ft.Row(controls=[self.favorites_button, self.upcoming_button], spacing=10),
                    self.status_bar,
                    ft.Divider(height=1, color=AppColors.BORDER),
                ],
            ),
            self.content_row,
        ]

        self.subscribe()
        self.app_page.run_task(self.controller.load_documents)

    def did_mount(self) -> None:
        self.subscribe()

    def will_unmount(self) -> None:
        self.unsubscribe()

    def subscribe(self) -> None:
        self.subscriptions.add_many(self.DOCUMENT_EVENTS, self.handle_document_event)

    def unsubscribe(self) -> None:
        self.subscriptions.clear()

    def dispose(self) -> None:
        self.unsubscribe()
        self.preview_controller.clear()

    def handle_document_event(self, event) -> None:
        self.app_page.run_task(self.controller.load_documents)

    def change_tab(self, tab_name: str) -> None:
        if not self.controller.change_tab(tab_name):
            return

        self.preview_panel.clear()
        self.apply_preview_layout()
        self.app_page.run_task(self.controller.load_documents)

    def show_preview(self, document) -> None:
        self.controller.select_document(document)
        self.state.preview_full_width = (self.get_available_width() < self.COMPACT_PREVIEW_WIDTH)
        self.show_selected_preview()
        self.render()

    def close_preview(self, event=None, *, update_page: bool = True) -> None:
        self.controller.clear_selection()
        self.preview_panel.clear()
        self.apply_preview_layout()
        self.render(update_page=update_page)

    def toggle_preview_layout(self) -> None:
        if not self.preview_panel.visible:
            return
        self.controller.toggle_preview_layout()
        self.apply_preview_layout()
        self.safe_page_update()

    def show_previous_document(self) -> None:
        if self.controller.select_previous_document() is None:
            return
        self.show_selected_preview()
        self.render()

    def show_next_document(self) -> None:
        if self.controller.select_next_document() is None:
            return
        self.show_selected_preview()
        self.render()

    def show_selected_preview(self) -> None:
        document = self.state.selected_document()
        if document is None:
            self.preview_panel.clear()
            return

        self.preview_controller.select_file(document.absolute_path, document.name, category_name=document.category, file_size=document.file_size)
        self.preview_panel.show_document()
        self.update_document_navigation()
        self.apply_preview_layout()

    def update_document_navigation(self) -> None:
        selected_index = self.state.selected_document_index()
        if selected_index is None:
            self.preview_panel.set_document_navigation(has_previous=False, has_next=False)
            return

        self.preview_panel.set_document_navigation(has_previous=selected_index > 0, has_next=selected_index < len(self.state.documents) - 1)

    def apply_preview_layout(self) -> None:
        if not self.preview_panel.visible:
            self.documents_panel.visible = True
            self.documents_panel.expand = 5
            self.preview_panel.expand = 6
            self.preview_panel.set_full_width(False)
            return

        if self.state.preview_full_width:
            self.documents_panel.visible = False
            self.preview_panel.expand = 1
            self.preview_panel.set_full_width(True)
        else:
            self.documents_panel.visible = True
            self.documents_panel.expand = 5
            self.preview_panel.expand = 6
            self.preview_panel.set_full_width(False)

    def render(self, update_page: bool = True) -> None:
        selected_document = self.state.selected_document()
        if self.state.selected_document_id is not None and selected_document is None:
            self.preview_panel.clear()

        self.documents_list.controls = ImportantBuilder.build_documents(
            page=self.app_page,
            state=self.state,
            on_preview=self.show_preview,
            on_changed=self.controller.load_documents,
            on_retry=lambda event: self.app_page.run_task(self.controller.load_documents),
        )

        favorites_selected = self.state.selected_tab == "favorites"
        self.favorites_button.bgcolor = (AppColors.PRIMARY if favorites_selected else AppColors.PANEL)
        self.upcoming_button.bgcolor = (AppColors.PANEL if favorites_selected else AppColors.PRIMARY)
        self.favorites_button.disabled = self.state.loading
        self.upcoming_button.disabled = self.state.loading

        if self.state.error_message:
            self.status_bar.counter.value = ""
            self.status_bar.clear_message()
            notifications(self.app_page).error(self.state.error_message)
        else:
            singular, plural = ImportantBuilder.count_labels(self.state.selected_tab)
            self.status_bar.clear_message()
            self.status_bar.set_count(len(self.state.documents), singular, plural)

        self.status_bar.set_loading(self.state.loading, "Chargement...")

        if selected_document is not None:
            self.show_selected_preview()
        else:
            self.apply_preview_layout()

        if update_page:
            self.safe_page_update()

    def get_available_width(self) -> float:
        return float(getattr(self.app_page, "width", 0) or 0)

    def safe_page_update(self) -> None:
        try:
            self.app_page.update()
        except RuntimeError:
            pass
