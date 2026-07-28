import json
import logging
import shutil
from pathlib import Path

from core.config.constants import STORAGE_ROOT, TRASH_ROOT
from core.events.event_bus import DocumentRestored, TrashChanged, event_bus
from core.errors.exceptions import (
    CategoryNotFoundError,
    DocumentNotFoundError,
    StorageError,
)
from utils.time import local_now_iso
from repositories.category_repository import category_repository
from repositories.document_repository import document_repository
from repositories.metadata_repository import metadata_repository


logger = logging.getLogger(__name__)


class DocumentRestoreService:
    TRASH_ROOT = TRASH_ROOT / "documents"

    def restore(
        self,
        trash_id: str,
        destination_category_key: str | None = None,
    ) -> Path:
        trash_folder = self._get_trash_folder(trash_id)
        manifest = self._read_manifest(trash_folder)
        document_data = manifest["document"]

        original_category_key = str(
            document_data["category_key"]
        )

        category_key = (
            destination_category_key
            or original_category_key
        )

        category = category_repository.get(
            category_key
        )

        if category is None:
            if destination_category_key is None:
                raise CategoryNotFoundError(
                    "Le classeur d’origine n’existe plus. "
                    "Choisissez un autre classeur."
                )

            raise CategoryNotFoundError(
                "Le classeur de destination n’existe pas."
            )

        source_file = self._find_document_file(
            trash_folder
        )

        destination_folder = (
            STORAGE_ROOT / category_key
        )

        destination_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_path = self._build_unique_path(
            destination_folder / source_file.name
        )

        relative_path = (
            destination_path
            .relative_to(STORAGE_ROOT)
            .as_posix()
        )

        shutil.move(
            str(source_file),
            str(destination_path),
        )

        try:
            stat = destination_path.stat()

            document_id = document_repository.insert(
                category_key=category_key,
                stored_name=destination_path.name,
                display_name=destination_path.name.replace(
                    "_",
                    " ",
                ),
                relative_path=relative_path,
                extension=destination_path.suffix.casefold(),
                size_bytes=stat.st_size,
                sha256=str(
                    document_data.get("sha256") or ""
                ),
                extracted_text=str(
                    document_data.get("extracted_text") or ""
                ),
                created_at=str(
                    document_data.get("created_at")
                    or local_now_iso()
                ),
                imported_at=str(
                    document_data.get("imported_at")
                    or local_now_iso()
                ),
                modified_at=local_now_iso(),
                source_mtime_ns=stat.st_mtime_ns,
                indexed_at=local_now_iso(),
            )

            metadata_repository.update(
                document_id,
                is_favorite=bool(
                    document_data.get(
                        "is_favorite",
                        False,
                    )
                ),
                document_date=document_data.get(
                    "document_date"
                ),
                due_date=document_data.get(
                    "due_date"
                ),
                amount=document_data.get(
                    "amount"
                ),
                person_name=str(
                    document_data.get(
                        "person_name",
                        "",
                    )
                ),
                notes=str(
                    document_data.get(
                        "notes",
                        "",
                    )
                ),
                tags=list(
                    document_data.get(
                        "tags",
                        [],
                    )
                ),
            )

        except Exception:
            if destination_path.exists():
                shutil.move(
                    str(destination_path),
                    str(source_file),
                )

            raise

        shutil.rmtree(
            trash_folder
        )

        event_bus.publish(
            DocumentRestored(
                document_id=document_id,
                category_key=category_key,
                relative_path=relative_path,
            )
        )

        event_bus.publish(
            TrashChanged(
                document_count=self.count_documents()
            )
        )

        logger.info(
            "Document restauré : %s",
            destination_path,
        )

        return destination_path

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

    def _get_trash_folder(self, trash_id: str) -> Path:
        if (
            not trash_id
            or "/" in trash_id
            or "\\" in trash_id
            or trash_id in {".", ".."}
        ):
            raise StorageError(
                "Identifiant de corbeille invalide."
            )

        folder = (
            self.TRASH_ROOT / trash_id
        )

        if not folder.exists():
            raise DocumentNotFoundError(
                "Le document n’existe plus "
                "dans la corbeille."
            )

        return folder

    @staticmethod
    def _read_manifest(trash_folder: Path) -> dict:
        manifest_path = (
            trash_folder / "document.json"
        )

        if not manifest_path.exists():
            raise StorageError(
                "Le manifeste de suppression est absent."
            )

        try:
            manifest = json.loads(
                manifest_path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception as error:
            raise StorageError(
                "Le manifeste de suppression "
                "est illisible."
            ) from error

        if not isinstance(
            manifest.get("document"),
            dict,
        ):
            raise StorageError(
                "Le manifeste de suppression "
                "est invalide."
            )

        return manifest

    @staticmethod
    def _find_document_file(
        trash_folder: Path,
    ) -> Path:
        files = [
            path
            for path in trash_folder.iterdir()
            if path.is_file()
            and path.name != "document.json"
        ]

        if len(files) != 1:
            raise StorageError(
                "L’entrée de corbeille est invalide."
            )

        return files[0]

    @staticmethod
    def _build_unique_path(path: Path) -> Path:
        if not path.exists():
            return path

        counter = 2

        while True:
            candidate = path.with_name(
                f"{path.stem}_{counter}"
                f"{path.suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1


document_restore_service = DocumentRestoreService()