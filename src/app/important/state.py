from dataclasses import dataclass, field

from models.document import DocumentMetadata


@dataclass
class ImportantState:
    selected_tab: str = "favorites"
    documents: list[DocumentMetadata] = field(default_factory=list)
    selected_document_id: int | None = None
    preview_full_width: bool = False
    loading: bool = False
    error_message: str = ""

    def set_documents(self, documents: list[DocumentMetadata]) -> None:
        self.documents = documents
        self.error_message = ""

        if self.selected_document_id is None:
            return

        available_ids = {document.document_id for document in documents}
        if self.selected_document_id not in available_ids:
            self.clear_selection()

    def change_tab(self, tab_name: str) -> bool:
        if tab_name == self.selected_tab:
            return False

        self.selected_tab = tab_name
        self.clear_selection()
        return True

    def select_document(self, document_id: int) -> None:
        self.selected_document_id = document_id

    def clear_selection(self) -> None:
        self.selected_document_id = None
        self.preview_full_width = False

    def selected_document(self) -> DocumentMetadata | None:
        if self.selected_document_id is None:
            return None
        return next((document for document in self.documents if document.document_id == self.selected_document_id), None )

    def selected_document_index(self) -> int | None:
        if self.selected_document_id is None:
            return None

        for index, document in enumerate(self.documents):
            if document.document_id == self.selected_document_id:
                return index

        return None
