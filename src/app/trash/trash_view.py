import logging

import flet as ft
from papernestextension.controls.material.papernest_textfield import PaperNestTextFieldState

from app.notifications import notifications
from app.theme.buttons import DangerButton, OutlineButton, PrimaryButton
from app.theme.cards import HeaderCard
from app.theme.forms import BaseCheckbox, SearchTextField
from app.theme.status_bar import StatusBar
from app.trash.builder import TrashBuilder
from app.trash.controller import TrashController
from app.trash.dialogs.batch_trash_dialog import BatchTrashDialog
from app.trash.dialogs.empty_trash_dialog import EmptyTrashDialog
from app.trash.dialogs.permanent_delete_dialog import PermanentDeleteDialog
from app.trash.dialogs.restore_dialog import RestoreDialog
from app.trash.state import TrashState
from core.events.event_bus import TrashChanged
from core.events.subscription import EventSubscription
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors
from services.trash.service import TrashedDocument

logger = logging.getLogger(__name__)


class TrashView(ft.Column):
    def __init__(self, page: ft.Page, on_content_changed=None):
        super().__init__(expand=True, spacing=15)
        self.app_page = page
        self.on_content_changed = on_content_changed
        self.subscriptions = EventSubscription()
        self.state = TrashState()
        self.controller = TrashController(self.state, self.render)

        self.search_field = SearchTextField(hint_text="Rechercher par nom, tag, note, personne ou classeur...", expand=True, on_search=self.handle_search)
        self.select_all_checkbox = BaseCheckbox(label="Tout sélectionner", value=False, on_change=self.toggle_select_all)
        self.selection_text = ft.Text("Aucune sélection", size=12, color=AppColors.TEXT_MUTED)
        self.restore_selected_button = PrimaryButton("Restaurer", icon=ft.Icons.RESTORE_FROM_TRASH_ROUNDED, on_click=self.show_restore_selected_dialog)
        self.delete_selected_button = DangerButton("Supprimer", icon=ft.Icons.DELETE_FOREVER_ROUNDED, on_click=self.show_delete_selected_dialog)
        self.clean_button = OutlineButton("Nettoyer", icon=ft.Icons.CLEANING_SERVICES_ROUNDED, on_click=self.clean_invalid_entries)
        self.empty_button = DangerButton("Vider la corbeille", icon=ft.Icons.DELETE_FOREVER_ROUNDED, on_click=self.show_empty_trash_dialog)
        self.status_bar = StatusBar()
        self.documents_list = ft.ListView(expand=True, spacing=12, padding=2)

        self.controls = [
            HeaderCard(title="Corbeille", subtitle="Les documents sont supprimés automatiquement après 30 jours.", icon=ft.Icons.DELETE_OUTLINE_ROUNDED),
            ft.Row(controls=[self.search_field, self.clean_button, self.empty_button], spacing=10),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=10,
                bgcolor=ft.Colors.GREY_100,
                content=ft.Row(spacing=10, controls=[self.select_all_checkbox, self.selection_text, self.restore_selected_button, self.delete_selected_button]),
            ),
            self.status_bar,
            ft.Divider(height=1, color=AppColors.BORDER),
            self.documents_list,
        ]
        self.subscribe()
        self.app_page.run_task(self.controller.load_documents)

    def did_mount(self) -> None:
        self.subscribe()

    def will_unmount(self) -> None:
        self.unsubscribe()

    def subscribe(self) -> None:
        self.subscriptions.add(TrashChanged, self.handle_trash_changed)

    def unsubscribe(self) -> None:
        self.subscriptions.clear()

    def dispose(self) -> None:
        self.unsubscribe()
        self.controller.dispose()

    def handle_trash_changed(self, event) -> None:
        self.app_page.run_task(self.controller.load_documents, self.get_search_query())

    async def handle_search(self, _event) -> None:
        await self.controller.search_now(self.get_search_query())

    def handle_selection(self, document: TrashedDocument, selected: bool) -> None:
        self.controller.set_document_selected(document, selected)

    def toggle_select_all(self, event) -> None:
        self.controller.select_all(bool(event.control.value))

    def show_restore_selected_dialog(self, event) -> None:
        BatchTrashDialog(self.app_page, list(self.state.selected_ids), "restore", self.handle_batch_completed).show()

    def show_delete_selected_dialog(self, event) -> None:
        BatchTrashDialog(self.app_page, list(self.state.selected_ids), "delete", self.handle_batch_completed).show()

    async def handle_batch_completed(self, count: int, errors: list[str], mode: str) -> None:
        self.controller.clear_selection()
        action = "restauré" if mode == "restore" else "supprimé définitivement"
        notifications(self.app_page).success(f"{count} document(s) {action}(s).")
        if errors:
            notifications(self.app_page).warning(f"{len(errors)} document(s) n’ont pas pu être traités.")
        self.notify_content_changed()
        await self.controller.load_documents(self.get_search_query())

    def show_restore_dialog(self, document: TrashedDocument) -> None:
        RestoreDialog(page=self.app_page, document=document, on_restored=self.handle_document_restored).show()

    async def handle_document_restored(self, destination) -> None:
        notifications(self.app_page).success(f"Document restauré : {destination.name}")
        self.controller.clear_selection()
        self.notify_content_changed()

    def show_permanent_delete_dialog(self, document: TrashedDocument) -> None:
        PermanentDeleteDialog(page=self.app_page, document=document, on_deleted=self.handle_document_permanently_deleted).show()

    async def handle_document_permanently_deleted(self, document: TrashedDocument) -> None:
        notifications(self.app_page).success(f"« {document.display_name} » a été supprimé définitivement.")
        self.state.selected_ids.discard(document.trash_id)
        self.render()
        self.notify_content_changed()

    def show_empty_trash_dialog(self, event) -> None:
        EmptyTrashDialog(page=self.app_page, on_emptied=self.handle_trash_emptied).show()

    async def handle_trash_emptied(self, deleted_count: int) -> None:
        self.controller.clear_selection()
        message = (f"{deleted_count} document supprimé." if deleted_count == 1 else f"{deleted_count} documents supprimés.")
        notifications(self.app_page).success(message)
        self.notify_content_changed()

    def clean_invalid_entries(self, event) -> None:
        self.app_page.run_task(self.run_clean_invalid_entries)

    async def run_clean_invalid_entries(self) -> None:
        try:
            moved_count = await self.controller.clean_invalid_entries()
            message = ("Aucune entrée endommagée." if moved_count == 0 else f"{moved_count} entrée(s) endommagée(s) déplacée(s).")
            notifications(self.app_page).info(message)
            await self.controller.load_documents(self.get_search_query())
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))
        except Exception:
            logger.exception("Impossible de nettoyer la corbeille.")
            notifications(self.app_page).error("Impossible de nettoyer la corbeille.")

    def open_trash_folder(self, document: TrashedDocument) -> None:
        try:
            self.controller.open_trash_folder(document)
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))

    def render(self) -> None:
        self.documents_list.controls = TrashBuilder.build_documents(
            state=self.state,
            on_selected=self.handle_selection,
            on_open_folder=self.open_trash_folder,
            on_restore=self.show_restore_dialog,
            on_delete=self.show_permanent_delete_dialog,
            on_retry=lambda event: self.app_page.run_task(self.controller.load_documents, self.get_search_query()),
        )

        if self.state.error_message:
            self.status_bar.counter.value = ""
            self.status_bar.clear_message()
        else:
            singular, plural = TrashBuilder.count_labels(self.state.search_query)
            self.status_bar.clear_message()
            self.status_bar.set_count(len(self.state.documents), singular, plural)

        count = self.state.selection_count
        self.selection_text.value = TrashBuilder.selection_label(count)
        self.select_all_checkbox.value = self.state.all_selected
        self.select_all_checkbox.disabled = not self.state.documents
        self.clean_button.disabled = self.state.loading
        self.empty_button.disabled = self.state.loading or (not self.state.documents and not self.state.search_query)
        self.restore_selected_button.disabled = self.state.loading or count == 0
        self.delete_selected_button.disabled = self.state.loading or count == 0
        self.search_field.searching = self.state.loading
        self.search_field.state = (
            PaperNestTextFieldState.ERROR
            if self.state.error_message
            else PaperNestTextFieldState.NORMAL
        )
        self.search_field.state_message = self.state.error_message or None
        self.status_bar.set_loading(self.state.loading, "Chargement...")

        if self.state.error_message:
            notifications(self.app_page).error(self.state.error_message)

        self.safe_update()

    def notify_content_changed(self) -> None:
        if self.on_content_changed:
            self.on_content_changed()

    def get_search_query(self) -> str:
        return self.search_field.value.strip() if self.search_field.value else ""

    def safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
