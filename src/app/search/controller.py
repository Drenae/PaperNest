from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from app.search.state import SearchState
from core.errors.exceptions import PaperNestError
from core.models.search_filters import SearchFilters
from services.documents.query import document_query_service
from services.files.archive import ArchiveFileService
from services.search.saved_searches import saved_search_service

logger = logging.getLogger(__name__)


class SearchController:
    def __init__(self, state: SearchState, on_state_changed=None):
        self.state = state
        self.on_state_changed = on_state_changed

    async def search(self, query: str, filters: SearchFilters, generation: int) -> None:
        if generation != self.state.generation:
            return

        if not query and not self.has_active_filters(filters):
            self.state.set_initial()
            self.state.loading = False
            self._notify_state_changed()
            return

        self.state.loading = True
        self.state.error_message = ""
        self._notify_state_changed()

        try:
            documents = await asyncio.to_thread(
                document_query_service.search_advanced,
                query,
                filters,
            )
            if generation == self.state.generation:
                self.state.set_results(list(documents))
        except PaperNestError as error:
            if generation == self.state.generation:
                self.state.set_error(str(error))
        except Exception:
            logger.exception("Impossible d'effectuer la recherche avancée.")
            if generation == self.state.generation:
                self.state.set_error("Impossible d'effectuer la recherche.")
        finally:
            if generation == self.state.generation:
                self.state.loading = False
                self._notify_state_changed()

    def begin_search(self, query: str, filters: SearchFilters) -> int:
        return self.state.begin_search(query, filters)

    def invalidate_search(self) -> None:
        self.state.invalidate_search()

    def select_document(self, index: int):
        document = self.state.select_index(index)
        self._notify_state_changed()
        return document

    def clear_selection(self) -> None:
        self.state.clear_selection()
        self._notify_state_changed()

    def previous_document(self):
        return self.select_document(self.state.selected_index - 1)

    def next_document(self):
        return self.select_document(self.state.selected_index + 1)

    def list_saved_searches(self) -> list[dict[str, Any]]:
        return list(saved_search_service.list_all())

    def save_search(self, name: str, query: str, filters: SearchFilters) -> str:
        saved_search_service.save(name, query, filters.to_dict())
        return name.strip()

    def load_saved_search(self, name: str) -> tuple[str, SearchFilters] | None:
        item = next(
            (item for item in self.list_saved_searches() if item.get("name") == name),
            None,
        )
        if not item:
            return None
        return (
            str(item.get("query") or ""),
            SearchFilters.from_dict(item.get("filters") or {}),
        )

    def delete_saved_search(self, name: str) -> None:
        saved_search_service.delete(name)

    @staticmethod
    def open_document(target_path: str) -> None:
        ArchiveFileService.execute_native_file_open(target_path)

    @staticmethod
    def open_parent_folder(target_path: str) -> None:
        ArchiveFileService.execute_native_file_open(str(Path(target_path).parent))

    @staticmethod
    def has_active_filters(filters: SearchFilters) -> bool:
        return any(
            (
                filters.category_key,
                filters.file_type,
                filters.favorites_only,
                filters.imported_period,
                filters.person_query,
                filters.tag_query,
            )
        )

    def _notify_state_changed(self) -> None:
        if self.on_state_changed:
            self.on_state_changed()
