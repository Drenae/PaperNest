import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from core.config.constants import TRASH_ROOT
from core.errors.exceptions import DocumentNotFoundError, PaperNestError
from core.models.trash_settings import DEFAULT_TRASH_RETENTION_DAYS
from repositories.category_repository import category_repository
from services.documents.delete import document_delete_service
from services.documents.restore import document_restore_service
from services.settings import trash_settings_service


class TrashError(PaperNestError):
    pass


class InvalidTrashEntryError(TrashError):
    pass


@dataclass(frozen=True, slots=True)
class TrashedDocument:
    trash_id: str
    trash_folder: Path
    file_path: Path
    file_name: str
    display_name: str
    original_category_key: str
    original_category_name: str
    original_relative_path: str
    deleted_at: str
    deleted_at_display: str
    size_bytes: int
    formatted_size: str
    extension: str
    sha256: str
    tags: tuple[str, ...]
    notes: str
    person_name: str
    age_days: int
    retention_days: int
    remaining_days: int
    expiration_label: str
    expiration_progress: float
    expiration_level: str


class TrashService:
    TRASH_DOCUMENTS_ROOT = TRASH_ROOT / "documents"
    MANIFEST_FILENAME = "document.json"
    DEFAULT_RETENTION_DAYS = DEFAULT_TRASH_RETENTION_DAYS

    @staticmethod
    def initialize() -> None:
        TrashService.TRASH_DOCUMENTS_ROOT.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_documents(search_query: str = "") -> list[TrashedDocument]:
        TrashService.initialize()
        query_terms = [term for term in search_query.strip().casefold().split() if term]
        documents: list[TrashedDocument] = []
        retention_days = trash_settings_service.get_retention_days()

        for trash_folder in TrashService.TRASH_DOCUMENTS_ROOT.iterdir():
            if not trash_folder.is_dir():
                continue
            try:
                document = TrashService._read_entry(trash_folder, retention_days)
            except InvalidTrashEntryError:
                continue

            searchable_text = " ".join(
                [
                    document.display_name,
                    document.file_name,
                    document.original_category_name,
                    document.original_category_key,
                    document.original_relative_path,
                    document.deleted_at_display,
                    document.person_name,
                    document.notes,
                    " ".join(document.tags),
                ]
            ).casefold()

            if query_terms and not all(term in searchable_text for term in query_terms):
                continue
            documents.append(document)

        documents.sort(key=lambda item: item.deleted_at, reverse=True)
        return documents

    @staticmethod
    def count_documents() -> int:
        return document_delete_service.count_documents()

    @staticmethod
    def restore_document(trash_id: str, destination_category_key: str | None = None) -> Path:
        try:
            return document_restore_service.restore(trash_id, destination_category_key)
        except PaperNestError:
            raise
        except Exception as error:
            raise TrashError("Impossible de restaurer le document.") from error

    @staticmethod
    def restore_many(trash_ids: list[str], destination_category_key: str | None = None) -> tuple[int, list[str]]:
        restored_count = 0
        errors: list[str] = []
        for trash_id in dict.fromkeys(trash_ids):
            try:
                TrashService.restore_document(trash_id, destination_category_key)
                restored_count += 1
            except PaperNestError as error:
                errors.append(str(error))
        return restored_count, errors

    @staticmethod
    def permanently_delete(trash_id: str) -> None:
        try:
            entry = TrashService.get_document(trash_id)
            document_delete_service.permanently_delete(entry.trash_folder)
        except PaperNestError:
            raise
        except Exception as error:
            raise TrashError("Impossible de supprimer définitivement le document.") from error

    @staticmethod
    def permanently_delete_many(trash_ids: list[str]) -> tuple[int, list[str]]:
        deleted_count = 0
        errors: list[str] = []
        for trash_id in dict.fromkeys(trash_ids):
            try:
                TrashService.permanently_delete(trash_id)
                deleted_count += 1
            except PaperNestError as error:
                errors.append(str(error))
        return deleted_count, errors

    @staticmethod
    def empty_trash() -> int:
        try:
            return document_delete_service.empty_trash()
        except PaperNestError:
            raise
        except Exception as error:
            raise TrashError("Impossible de vider la corbeille.") from error

    @staticmethod
    def purge_expired(retention_days: int | None = None) -> int:
        days = (
            trash_settings_service.get_retention_days()
            if retention_days is None
            else retention_days
        )
        deleted_count = 0
        for document in TrashService.list_documents():
            if document.age_days < days:
                continue
            try:
                TrashService.permanently_delete(document.trash_id)
                deleted_count += 1
            except PaperNestError:
                continue
        return deleted_count

    @staticmethod
    def get_summary() -> tuple[int, int]:
        documents = TrashService.list_documents()
        return len(documents), sum(document.size_bytes for document in documents)

    @staticmethod
    def get_document(trash_id: str) -> TrashedDocument:
        TrashService.initialize()
        if not trash_id or "/" in trash_id or "\\" in trash_id or trash_id in {".", ".."}:
            raise InvalidTrashEntryError("Identifiant de corbeille invalide.")
        trash_folder = TrashService.TRASH_DOCUMENTS_ROOT / trash_id
        if not trash_folder.exists():
            raise DocumentNotFoundError("Ce document n’existe plus dans la corbeille.")
        return TrashService._read_entry(
            trash_folder,
            trash_settings_service.get_retention_days(),
        )

    @staticmethod
    def original_category_exists(trash_id: str) -> bool:
        entry = TrashService.get_document(trash_id)
        return category_repository.get(entry.original_category_key) is not None

    @staticmethod
    def get_available_categories() -> list[dict]:
        return category_repository.list_all()

    @staticmethod
    def clean_invalid_entries() -> int:
        TrashService.initialize()
        invalid_root = TRASH_ROOT / "entrees_endommagees"
        invalid_root.mkdir(parents=True, exist_ok=True)
        moved_count = 0
        retention_days = trash_settings_service.get_retention_days()
        for trash_folder in TrashService.TRASH_DOCUMENTS_ROOT.iterdir():
            if not trash_folder.is_dir():
                continue
            try:
                TrashService._read_entry(trash_folder, retention_days)
            except InvalidTrashEntryError:
                destination = TrashService._build_unique_path(invalid_root / trash_folder.name)
                trash_folder.rename(destination)
                moved_count += 1
        return moved_count

    @staticmethod
    def _read_entry(
        trash_folder: Path,
        retention_days: int | None = None,
    ) -> TrashedDocument:
        manifest = TrashService._read_manifest(trash_folder)
        document_data = manifest["document"]
        files = [path for path in trash_folder.iterdir() if path.is_file() and path.name != TrashService.MANIFEST_FILENAME]
        if len(files) != 1:
            raise InvalidTrashEntryError("L’entrée de corbeille est invalide.")
        file_path = files[0]
        category_key = str(document_data.get("category_key", ""))
        category = category_repository.get(category_key)
        category_name = str(category["name"]) if category else category_key or "Classeur supprimé"
        deleted_at = str(manifest.get("deleted_at", ""))
        deleted_datetime = TrashService._parse_datetime(deleted_at)
        now = datetime.now().astimezone()
        age_days = max(0, (now.date() - deleted_datetime.date()).days) if deleted_datetime else 0
        retention_days = retention_days or trash_settings_service.get_retention_days()
        remaining_days = max(0, retention_days - age_days)
        progress = min(1.0, max(0.0, age_days / retention_days))
        size_bytes = int(document_data.get("size_bytes", file_path.stat().st_size))
        tags = tuple(str(tag).strip() for tag in document_data.get("tags", []) if str(tag).strip())
        return TrashedDocument(
            trash_id=trash_folder.name,
            trash_folder=trash_folder,
            file_path=file_path,
            file_name=file_path.name,
            display_name=str(document_data.get("display_name", file_path.stem.replace("_", " "))),
            original_category_key=category_key,
            original_category_name=category_name,
            original_relative_path=str(document_data.get("relative_path", "")),
            deleted_at=deleted_at,
            deleted_at_display=TrashService._format_datetime(deleted_at),
            size_bytes=size_bytes,
            formatted_size=TrashService._format_size(size_bytes),
            extension=file_path.suffix.casefold(),
            sha256=str(document_data.get("sha256", "")),
            tags=tags,
            notes=str(document_data.get("notes") or ""),
            person_name=str(document_data.get("person_name") or ""),
            age_days=age_days,
            retention_days=retention_days,
            remaining_days=remaining_days,
            expiration_label=TrashService._expiration_label(remaining_days),
            expiration_progress=progress,
            expiration_level=TrashService._expiration_level(remaining_days),
        )

    @staticmethod
    def _read_manifest(trash_folder: Path) -> dict:
        manifest_path = trash_folder / TrashService.MANIFEST_FILENAME
        if not manifest_path.exists():
            raise InvalidTrashEntryError("Le manifeste de suppression est absent.")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as error:
            raise InvalidTrashEntryError("Le manifeste de suppression est illisible.") from error
        if not isinstance(manifest, dict) or not isinstance(manifest.get("document"), dict):
            raise InvalidTrashEntryError("Le manifeste de suppression est invalide.")
        return manifest

    @staticmethod
    def _parse_datetime(value: str) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
            return parsed if parsed.tzinfo else parsed.astimezone()
        except ValueError:
            return None

    @staticmethod
    def _format_datetime(value: str) -> str:
        parsed = TrashService._parse_datetime(value)
        return parsed.strftime("%d/%m/%Y à %H:%M") if parsed else value or "Date inconnue"

    @staticmethod
    def _expiration_label(remaining_days: int) -> str:
        if remaining_days <= 0:
            return "Expire aujourd’hui"
        if remaining_days == 1:
            return "Expire demain"
        return f"Suppression définitive dans {remaining_days} jours"

    @staticmethod
    def _expiration_level(remaining_days: int) -> str:
        if remaining_days <= 3:
            return "danger"
        if remaining_days <= 10:
            return "warning"
        return "safe"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        size = float(size_bytes)
        for unit in ("o", "Ko", "Mo", "Go"):
            if size < 1024 or unit == "Go":
                return f"{size:.0f} {unit}" if unit == "o" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size_bytes} o"

    @staticmethod
    def _build_unique_path(path: Path) -> Path:
        if not path.exists():
            return path
        counter = 2
        while True:
            candidate = path.with_name(f"{path.name}_{counter}")
            if not candidate.exists():
                return candidate
            counter += 1
