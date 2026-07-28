from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable

from app.detail.state import DetailState
from core.errors.exceptions import PaperNestError
from services.documents.query import document_query_service

logger = logging.getLogger(__name__)


class DetailController:
    SEARCH_DELAY_SECONDS = 0.35

    def __init__(self, state: DetailState, on_state_changed: Callable[[], None] | None = None):
        self.state = state
        self.on_state_changed = on_state_changed

    def dispose(self) -> None:
        self.state.search_generation += 1

    def select_category(self, category_key: str) -> int:
        self.state.selected_category_key = category_key
        return self.next_generation()

    def next_generation(self) -> int:
        self.state.search_generation += 1
        return self.state.search_generation

    async def load_documents(self, search_query: str = "", generation: int | None = None) -> None:
        self.state.loading = True
        self.state.error_message = ""
        self._notify()
        try:
            method, category_key = self._resolve_query()
            documents = await asyncio.to_thread(method, category_key, search_query)
            if self._is_obsolete(generation):
                return
            self.state.set_documents(documents, search_query)
        except PaperNestError as error:
            if not self._is_obsolete(generation):
                self.state.error_message = str(error)
        except Exception:
            logger.exception("Impossible de charger le classeur %s.", self.state.category_key)
            if not self._is_obsolete(generation):
                self.state.error_message = "Impossible de charger les documents de ce classeur."
        finally:
            if not self._is_obsolete(generation):
                self.state.loading = False
                self._notify()

    async def search_after_delay(self, search_query: str) -> None:
        generation = self.next_generation()
        await asyncio.sleep(self.SEARCH_DELAY_SECONDS)
        if generation == self.state.search_generation:
            await self.load_documents(search_query, generation)

    async def search_now(self, search_query: str) -> None:
        generation = self.next_generation()
        await self.load_documents(search_query, generation)

    def select_document(self, document_id: int | None, *, preview_full_width: bool | None = None) -> None:
        self.state.selected_document_id = document_id
        if preview_full_width is not None:
            self.state.preview_full_width = preview_full_width

    def close_preview(self) -> None:
        self.state.selected_document_id = None
        self.state.preview_full_width = False

    def toggle_preview_layout(self) -> None:
        self.state.preview_full_width = not self.state.preview_full_width

    def previous_document(self):
        index = self.state.selected_document_index
        if index is None or index <= 0:
            return None
        return self.state.documents[index - 1]

    def next_document(self):
        index = self.state.selected_document_index
        if index is None or index >= len(self.state.documents) - 1:
            return None
        return self.state.documents[index + 1]

    def _resolve_query(self):
        selected = self.state.selected_category_key
        if selected == DetailState.FILTER_ALL:
            return document_query_service.list_by_category_tree, self.state.category_key
        if selected == DetailState.FILTER_DIRECT:
            return document_query_service.list_by_category, self.state.category_key
        return document_query_service.list_by_category, selected

    def _is_obsolete(self, generation: int | None) -> bool:
        return generation is not None and generation != self.state.search_generation

    def _notify(self) -> None:
        if self.on_state_changed:
            self.on_state_changed()
