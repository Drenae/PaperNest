import logging
from pathlib import Path

from core.config.constants import STORAGE_ROOT
from core.events.event_bus import DocumentRenamed, event_bus
from core.errors.exceptions import DocumentNotFoundError, InvalidDocumentNameError, StorageError
from utils.time import local_now_iso
from repositories.document_repository import document_repository
from services.files.archive import ArchiveFileService


logger = logging.getLogger(__name__)


class DocumentRenameService:
    def rename(self, document_id: int, new_name: str) -> Path:
        document = document_repository.get(document_id)

        if document is None:
            raise DocumentNotFoundError(
                "Le document est introuvable."
            )

        current_path = STORAGE_ROOT / str(document["relative_path"])

        if not current_path.exists():
            raise StorageError(
                "Le fichier n’existe plus."
            )

        sanitized_name = ArchiveFileService.sanitize_document_name(new_name)
        suffix = current_path.suffix

        if sanitized_name.casefold().endswith(suffix.casefold()):
            sanitized_name = sanitized_name[:-len(suffix)]

        sanitized_name = sanitized_name.rstrip(" ._")

        if not sanitized_name:
            raise InvalidDocumentNameError(
                "Le nouveau nom est invalide."
            )

        destination_path = current_path.with_name(
            f"{sanitized_name}{suffix}"
        )

        if destination_path.resolve() == current_path.resolve():
            return current_path

        if destination_path.exists():
            raise StorageError(
                "Un document portant ce nom existe déjà dans ce classeur."
            )

        old_relative_path = str(document["relative_path"])
        new_relative_path = destination_path.relative_to(STORAGE_ROOT).as_posix()

        current_path.rename(destination_path)

        try:
            stat = destination_path.stat()

            document_repository.update_location(
                document_id,
                category_key=str(document["category_key"]),
                stored_name=destination_path.name,
                display_name=destination_path.name.replace("_", " "),
                relative_path=new_relative_path,
                modified_at=local_now_iso(),
                source_mtime_ns=stat.st_mtime_ns,
            )

        except Exception:
            destination_path.rename(current_path)
            raise

        event_bus.publish(
            DocumentRenamed(
                document_id=document_id,
                old_relative_path=old_relative_path,
                new_relative_path=new_relative_path,
            )
        )

        logger.info(
            "Document renommé : %s -> %s",
            current_path,
            destination_path,
        )

        return destination_path


document_rename_service = DocumentRenameService()