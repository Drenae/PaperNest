from __future__ import annotations

from dataclasses import dataclass, field

from core.models.search_filters import SearchFilters
from models.document import DocumentMetadata


@dataclass
class SearchState:
    query: str = ""
    filters: SearchFilters = field(default_factory=SearchFilters)
    documents: list[DocumentMetadata] = field(default_factory=list)
    selected_index: int = -1
    loading: bool = False
    error_message: str = ""
    has_searched: bool = False
    generation: int = 0

    def begin_search(self, query: str, filters: SearchFilters) -> int:
        self.query = query
        self.filters = filters
        self.generation += 1
        return self.generation

    def invalidate_search(self) -> None:
        self.generation += 1

    def set_results(self, documents: list[DocumentMetadata]) -> None:
        self.documents = list(documents)
        self.selected_index = -1
        self.error_message = ""
        self.has_searched = True

    def set_initial(self) -> None:
        self.documents = []
        self.selected_index = -1
        self.error_message = ""
        self.has_searched = False

    def set_error(self, message: str) -> None:
        self.documents = []
        self.selected_index = -1
        self.error_message = message
        self.has_searched = True

    def select_index(self, index: int) -> DocumentMetadata | None:
        if not 0 <= index < len(self.documents):
            return None
        self.selected_index = index
        return self.documents[index]

    def clear_selection(self) -> None:
        self.selected_index = -1

    def selected_document(self) -> DocumentMetadata | None:
        if not 0 <= self.selected_index < len(self.documents):
            return None
        return self.documents[self.selected_index]
