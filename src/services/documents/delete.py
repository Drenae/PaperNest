import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

from core.config.constants import STORAGE_ROOT, TRASH_ROOT
from core.events.event_bus import DocumentDeleted, TrashChanged, event_bus
from core.errors.exceptions import DocumentNotFoundError, StorageError
from utils.time import local_now_iso
from repositories.document_repository import document_repository


logger = logging.getLogger(__name__)


class DocumentDeleteService:
    TRASH_ROOT = TRASH_ROOT / "documents"

    def move_to_trash(self, document_id: int) -> Path:
        document = document_repository.get(document_id)

        if document is None:
            raise DocumentNotFoundError(
                "Le document est introuvable."
            )

        source_path = STORAGE_ROOT / str(document["relative_path"])

        if not source_path.exists():
            raise StorageError(
                "Le fichier n’existe plus."
            )

        self.TRASH_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        trash_folder = self._build_unique_directory(
            self.TRASH_ROOT
            / f"{timestamp}_{document_id}"
        )

        trash_folder.mkdir(
            parents=True,
            exist_ok=False,
        )

        trash_file = trash_folder / source_path.name
        manifest_path = trash_folder / "document.json"

        manifest = {
            "trash_version": 2,
            "deleted_at": local_now_iso(),
            "document": {
                "id": int(document["id"]),
                "category_key": str(
                    document["category_key"]
                ),
                "stored_name": str(
                    document["stored_name"]
                ),
                "display_name": str(
                    document["display_name"]
                ),
                "searchable_name": str(
                    document.get("searchable_name") or ""
                ),
                "relative_path": str(
                    document["relative_path"]
                ),
                "extension": str(
                    document["extension"]
                ),
                "size_bytes": int(
                    document["size_bytes"]
                ),
                "sha256": str(
                    document.get("sha256") or ""
                ),
                "extracted_text": str(
                    document.get("extracted_text") or ""
                ),
                "created_at": str(
                    document["created_at"]
                ),
                "imported_at": str(
                    document["imported_at"]
                ),
                "modified_at": str(
                    document["modified_at"]
                ),
                "source_mtime_ns": int(
                    document.get("source_mtime_ns") or 0
                ),
                "indexed_at": str(
                    document.get("indexed_at") or ""
                ),
                "is_favorite": bool(
                    document.get("is_favorite", False)
                ),
                "document_date": document.get(
                    "document_date"
                ),
                "due_date": document.get(
                    "due_date"
                ),
                "amount": document.get(
                    "amount"
                ),
                "person_name": str(
                    document.get("person_name") or ""
                ),
                "notes": str(
                    document.get("notes") or ""
                ),
                "metadata_search": str(
                    document.get("metadata_search") or ""
                ),
                "tags": self._parse_tags(
                    document.get("tags")
                ),
            },
        }

        try:
            shutil.move(
                str(source_path),
                str(trash_file),
            )

            manifest_path.write_text(
                json.dumps(
                    manifest,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            if not document_repository.delete(document_id):
                raise DocumentNotFoundError(
                    "Le document n’existe plus dans l’index."
                )

        except Exception:
            manifest_path.unlink(
                missing_ok=True
            )

            source_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if trash_file.exists():
                shutil.move(
                    str(trash_file),
                    str(source_path),
                )

            shutil.rmtree(
                trash_folder,
                ignore_errors=True,
            )

            raise

        event_bus.publish(
            DocumentDeleted(
                document_id=document_id,
                relative_path=str(
                    document["relative_path"]
                ),
            )
        )

        event_bus.publish(
            TrashChanged(
                document_count=self.count_documents()
            )
        )

        logger.info(
            "Document déplacé dans la corbeille : %s",
            source_path,
        )

        return trash_folder

    def permanently_delete(self, trash_folder: str | Path) -> None:
        folder = Path(trash_folder).resolve()
        trash_root = self.TRASH_ROOT.resolve()

        try:
            folder.relative_to(trash_root)

        except ValueError as error:
            raise StorageError(
                "Chemin de corbeille invalide."
            ) from error

        if not folder.exists():
            raise DocumentNotFoundError(
                "Le document n’existe plus dans la corbeille."
            )

        shutil.rmtree(folder)

        event_bus.publish(
            TrashChanged(
                document_count=self.count_documents()
            )
        )

    def empty_trash(self) -> int:
        self.TRASH_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        deleted_count = 0

        for entry in self.TRASH_ROOT.iterdir():
            if not entry.is_dir():
                continue

            shutil.rmtree(entry)
            deleted_count += 1

        event_bus.publish(
            TrashChanged(document_count=0)
        )

        return deleted_count

    def count_documents(self) -> int:
        self.TRASH_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        return sum(
            1
            for entry in self.TRASH_ROOT.iterdir()
            if entry.is_dir()
        )

    @staticmethod
    def _parse_tags(raw_tags) -> list[str]:
        if not raw_tags:
            return []

        return [
            tag.strip()
            for tag in str(raw_tags).split(",")
            if tag.strip()
        ]

    @staticmethod
    def _build_unique_directory(path: Path) -> Path:
        if not path.exists():
            return path

        counter = 2

        while True:
            candidate = path.with_name(
                f"{path.name}_{counter}"
            )

            if not candidate.exists():
                return candidate

            counter += 1


document_delete_service = DocumentDeleteService()