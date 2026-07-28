from pathlib import Path

from core.config.constants import STORAGE_ROOT
from core.models.search_filters import SearchFilters
from models.document import DocumentMetadata
from repositories.document_repository import document_repository


class DocumentQueryService:
    def list_by_category(self, category_key: str, search_query: str = "") -> list[DocumentMetadata]:
        rows = document_repository.list_by_category(category_key, search_query)
        return self._map_existing_documents(rows)

    def list_by_category_tree(self, category_key: str, search_query: str = "") -> list[DocumentMetadata]:
        rows = document_repository.list_by_category_tree(category_key, search_query)
        return self._map_existing_documents(rows)

    def search(self, search_query: str) -> list[DocumentMetadata]:
        return self.search_advanced(
            search_query,
            SearchFilters(),
        )

    def search_advanced(
        self,
        search_query: str,
        filters: SearchFilters,
    ) -> list[DocumentMetadata]:
        rows = document_repository.search_advanced(
            search_query,
            filters,
        )
        return self._map_existing_documents(rows)

    def list_favorites(self) -> list[DocumentMetadata]:
        rows = document_repository.list_favorites()
        return self._map_existing_documents(rows)

    def list_upcoming(self, days: int = 30) -> list[DocumentMetadata]:
        rows = document_repository.list_upcoming(days)
        return self._map_existing_documents(rows)

    def count_by_category(self, category_key: str) -> int:
        return document_repository.count_by_category(category_key)

    def get(self, document_id: int) -> DocumentMetadata | None:
        row = document_repository.get(document_id)

        if row is None:
            return None

        document = self._map_document(row)

        if not document.path.exists():
            return None

        return document

    def _map_existing_documents(self, rows: list[dict]) -> list[DocumentMetadata]:
        documents: list[DocumentMetadata] = []

        for row in rows:
            document = self._map_document(row)

            if document.path.exists():
                documents.append(document)

        return documents

    def _map_document(self, row: dict) -> DocumentMetadata:
        absolute_path = STORAGE_ROOT / str(row["relative_path"])

        return DocumentMetadata(
            name=str(row["display_name"]),
            absolute_path=str(absolute_path),
            category=str(row.get("category_name") or ""),
            file_size=self._format_file_size(int(row["size_bytes"])),
            match_reason=str(row.get("match_reason") or ""),
            document_id=int(row["id"]),
            category_key=str(row["category_key"]),
            relative_path=str(row["relative_path"]),
            extension=str(row["extension"]),
            size_bytes=int(row["size_bytes"]),
            sha256=str(row["sha256"]) if row.get("sha256") else None,
            imported_at=str(row["imported_at"]) if row.get("imported_at") else None,
            is_favorite=bool(row.get("is_favorite", False)),
            document_date=str(row["document_date"]) if row.get("document_date") else None,
            due_date=str(row["due_date"]) if row.get("due_date") else None,
            amount=str(row["amount"]) if row.get("amount") else None,
            person_name=str(row.get("person_name") or ""),
            notes=str(row.get("notes") or ""),
            tags=self._parse_tags(row.get("tags")),
        )

    @staticmethod
    def _parse_tags(raw_tags) -> tuple[str, ...]:
        if not raw_tags:
            return ()

        return tuple(
            tag.strip()
            for tag in str(raw_tags).split(",")
            if tag.strip()
        )

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        size = float(size_bytes)
        units = ("o", "Ko", "Mo", "Go", "To")

        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{int(size)} {unit}" if unit == "o" else f"{size:.1f} {unit}"

            size /= 1024

        return f"{size_bytes} o"


document_query_service = DocumentQueryService()