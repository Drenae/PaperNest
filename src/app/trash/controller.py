import asyncio
import logging

from app.trash.state import TrashState
from core.errors.exceptions import PaperNestError
from services.files.archive import ArchiveFileService
from services.trash.service import TrashService, TrashedDocument

logger = logging.getLogger(__name__)


class TrashController:
    SEARCH_DELAY_SECONDS = 0.35

    def __init__(self, state: TrashState, on_state_changed=None):
        self.state = state
        self.on_state_changed = on_state_changed

    def dispose(self) -> None:
        self.state.search_generation += 1

    async def load_documents(self, search_query: str = "", generation: int | None = None) -> None:
        self.state.loading = True
        self.state.error_message = ""
        self._notify_state_changed()

        try:
            documents = await asyncio.to_thread(TrashService.list_documents, search_query)
            if generation is not None and generation != self.state.search_generation:
                return
            self.state.set_documents(documents, search_query)
        except PaperNestError as error:
            self.state.error_message = str(error)
        except Exception:
            logger.exception("Impossible de charger la corbeille.")
            self.state.error_message = "Impossible de charger la corbeille."
        finally:
            if generation is None or generation == self.state.search_generation:
                self.state.loading = False
                self._notify_state_changed()

    async def search_after_delay(self, search_query: str) -> None:
        self.state.search_generation += 1
        generation = self.state.search_generation
        await asyncio.sleep(self.SEARCH_DELAY_SECONDS)
        if generation == self.state.search_generation:
            await self.load_documents(search_query, generation)

    async def search_now(self, search_query: str) -> None:
        self.state.search_generation += 1
        await self.load_documents(search_query, self.state.search_generation)

    def set_document_selected(self, document: TrashedDocument, selected: bool) -> None:
        self.state.set_selected(document.trash_id, selected)
        self._notify_state_changed()

    def select_all(self, selected: bool) -> None:
        self.state.select_all(selected)
        self._notify_state_changed()

    def clear_selection(self) -> None:
        self.state.clear_selection()
        self._notify_state_changed()

    async def clean_invalid_entries(self) -> int:
        self.state.loading = True
        self._notify_state_changed()
        try:
            return await asyncio.to_thread(TrashService.clean_invalid_entries)
        finally:
            self.state.loading = False
            self._notify_state_changed()

    @staticmethod
    def open_trash_folder(document: TrashedDocument) -> None:
        ArchiveFileService.execute_native_file_open(str(document.trash_folder))

    def _notify_state_changed(self) -> None:
        if self.on_state_changed:
            self.on_state_changed()
