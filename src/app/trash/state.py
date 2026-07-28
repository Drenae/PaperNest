from dataclasses import dataclass, field

from services.trash.service import TrashedDocument


@dataclass
class TrashState:
    documents: list[TrashedDocument] = field(default_factory=list)
    selected_ids: set[str] = field(default_factory=set)
    search_query: str = ""
    loading: bool = False
    error_message: str = ""
    search_generation: int = 0

    def set_documents(self, documents: list[TrashedDocument], search_query: str) -> None:
        self.documents = documents
        self.search_query = search_query
        available_ids = {document.trash_id for document in documents}
        self.selected_ids.intersection_update(available_ids)
        self.error_message = ""

    def set_selected(self, trash_id: str, selected: bool) -> None:
        if selected:
            self.selected_ids.add(trash_id)
        else:
            self.selected_ids.discard(trash_id)

    def select_all(self, selected: bool) -> None:
        self.selected_ids = (
            {document.trash_id for document in self.documents}
            if selected
            else set()
        )

    def clear_selection(self) -> None:
        self.selected_ids.clear()

    @property
    def selection_count(self) -> int:
        return len(self.selected_ids)

    @property
    def all_selected(self) -> bool:
        return bool(self.documents) and self.selection_count == len(self.documents)
