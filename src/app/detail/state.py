from __future__ import annotations

from dataclasses import dataclass, field

from models.document import DocumentMetadata


@dataclass
class DetailState:
    category_key: str
    category_name: str
    subcategories: list[dict] = field(default_factory=list)
    documents: list[DocumentMetadata] = field(default_factory=list)
    selected_category_key: str = "__all__"
    selected_document_id: int | None = None
    search_query: str = ""
    preview_full_width: bool = False
    loading: bool = False
    error_message: str = ""
    search_generation: int = 0

    FILTER_ALL = "__all__"
    FILTER_DIRECT = "__direct__"

    def set_documents(self, documents: list[DocumentMetadata], search_query: str) -> None:
        self.documents = list(documents)
        self.search_query = search_query
        self.error_message = ""
        available_ids = {document.document_id for document in self.documents}
        if self.selected_document_id not in available_ids:
            self.selected_document_id = None
            self.preview_full_width = False

    @property
    def subcategory_by_key(self) -> dict[str, dict]:
        return {str(item["key"]): item for item in self.subcategories}

    @property
    def selected_document_index(self) -> int | None:
        if self.selected_document_id is None:
            return None
        for index, document in enumerate(self.documents):
            if document.document_id == self.selected_document_id:
                return index
        return None

    @property
    def selected_document(self) -> DocumentMetadata | None:
        index = self.selected_document_index
        return self.documents[index] if index is not None else None
