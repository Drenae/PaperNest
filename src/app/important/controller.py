import asyncio
import logging

from app.important.state import ImportantState
from core.errors.exceptions import PaperNestError
from models.document import DocumentMetadata
from services.documents.query import document_query_service


logger = logging.getLogger(__name__)


class ImportantController:
    UPCOMING_DAYS = 30

    def __init__(self, state: ImportantState, on_state_changed=None):
        self.state = state
        self.on_state_changed = on_state_changed

    async def load_documents(self) -> None:
        self.state.loading = True
        self.state.error_message = ""
        self._notify_state_changed()

        try:
            if self.state.selected_tab == "favorites":
                documents = await asyncio.to_thread(document_query_service.list_favorites)
            else:
                documents = await asyncio.to_thread(document_query_service.list_upcoming, self.UPCOMING_DAYS)

            self.state.set_documents(documents)
        except PaperNestError as error:
            self.state.error_message = str(error)
        except Exception:
            logger.exception("Impossible de charger les documents importants.")
            self.state.error_message = ("Impossible de charger les documents importants.")
        finally:
            self.state.loading = False
            self._notify_state_changed()

    def change_tab(self, tab_name: str) -> bool:
        changed = self.state.change_tab(tab_name)
        if changed:
            self._notify_state_changed()
        return changed

    def select_document(self, document: DocumentMetadata) -> None:
        self.state.select_document(document.document_id)
        self._notify_state_changed()

    def clear_selection(self) -> None:
        self.state.clear_selection()
        self._notify_state_changed()

    def toggle_preview_layout(self) -> bool:
        if self.state.selected_document_id is None:
            return False

        self.state.preview_full_width = not self.state.preview_full_width
        self._notify_state_changed()
        return True

    def select_previous_document(self) -> DocumentMetadata | None:
        selected_index = self.state.selected_document_index()
        if selected_index is None or selected_index <= 0:
            return None

        document = self.state.documents[selected_index - 1]
        self.state.select_document(document.document_id)
        self._notify_state_changed()
        return document

    def select_next_document(self) -> DocumentMetadata | None:
        selected_index = self.state.selected_document_index()
        if (selected_index is None or selected_index >= len(self.state.documents) - 1):
            return None

        document = self.state.documents[selected_index + 1]
        self.state.select_document(document.document_id)
        self._notify_state_changed()
        return document

    def _notify_state_changed(self) -> None:
        if self.on_state_changed:
            self.on_state_changed()
