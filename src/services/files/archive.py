import hashlib
import logging
import os
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

from core.config.appearance import BACKGROUND_ROOT
from core.config.constants import (
    APP_ROOT,
    COPY_BUFFER_SIZE,
    DATA_ROOT,
    DB_PATH,
    LEGACY_DATABASE_PATH,
    LEGACY_STORAGE_ROOT,
    LOG_ROOT,
    STORAGE_ROOT,
    TRASH_ROOT,
    UNSORTED_ROOT,
)
from core.events.event_bus import DocumentImported, event_bus
from core.errors.exceptions import (
    CategoryNotFoundError,
    DocumentImportError,
    DuplicateDocumentError,
    InvalidCategoryNameError,
    InvalidDocumentNameError,
    StorageError,
)
from utils.time import local_now_iso
from repositories.category_repository import category_repository
from repositories.document_repository import document_repository
from services.categories.service import category_service
from services.documents.query import document_query_service
from services.indexing.service import DocumentIndexService
from services.pdf.service import PdfExtractionService


logger = logging.getLogger(__name__)


class ArchiveFileService:
    @staticmethod
    def initialize_storage_tree() -> None:
        ArchiveFileService._create_application_directories()
        ArchiveFileService._migrate_legacy_layout_if_needed()

        for category in category_repository.list_all():
            (STORAGE_ROOT / str(category["key"])).mkdir(
                parents=True,
                exist_ok=True,
            )

        DocumentIndexService.synchronize()

    @staticmethod
    def get_category_path(category_key: str) -> str:
        ArchiveFileService._get_category(category_key)
        return str(STORAGE_ROOT / category_key)

    @staticmethod
    def sanitize_document_name(name: str) -> str:
        sanitized = ArchiveFileService._sanitize_component(name)

        if not sanitized:
            raise InvalidDocumentNameError(
                "Le nom du document est vide ou invalide."
            )

        return sanitized

    @staticmethod
    def sanitize_category_name(name: str) -> str:
        sanitized = ArchiveFileService._sanitize_component(name)

        if not sanitized:
            raise InvalidCategoryNameError(
                "Le nom du classeur est vide ou invalide."
            )

        return sanitized

    @staticmethod
    def store_document(
        source_file_path: str,
        user_given_name: str,
        chosen_category_key: str,
        *,
        allow_duplicate: bool = False,
        source_sha256: str | None = None,
    ) -> Path:
        ArchiveFileService._create_application_directories()

        category = ArchiveFileService._get_category(
            chosen_category_key
        )

        source_path = Path(source_file_path).expanduser()

        if not source_path.exists():
            raise DocumentImportError(
                "Le fichier sélectionné n’existe plus."
            )

        if not source_path.is_file():
            raise DocumentImportError(
                "L’élément sélectionné n’est pas un fichier."
            )

        clean_name = ArchiveFileService.sanitize_document_name(
            user_given_name
        )

        extension = source_path.suffix.casefold()

        destination_path = ArchiveFileService._build_unique_path(
            STORAGE_ROOT
            / str(category["key"])
            / f"{clean_name}{extension}"
        )

        temporary_path = destination_path.with_name(
            f".{destination_path.name}.part"
        )

        source_hash = (
            source_sha256
            or ArchiveFileService._compute_sha256(source_path)
        )

        duplicate = (
            None
            if allow_duplicate
            else document_repository.find_by_hash(source_hash)
        )

        if duplicate:
            raise DuplicateDocumentError(
                "Ce fichier existe déjà dans PaperNest : "
                f"« {duplicate['display_name']} » dans le classeur "
                f"« {duplicate['category_name']} »."
            )

        try:
            temporary_path.unlink(missing_ok=True)
            shutil.copy2(source_path, temporary_path)

            copied_hash = ArchiveFileService._compute_sha256(
                temporary_path
            )

            if copied_hash != source_hash:
                raise DocumentImportError(
                    "La copie du fichier n’a pas pu être vérifiée."
                )

            temporary_path.replace(destination_path)

            stat = destination_path.stat()
            extracted_text = ArchiveFileService._extract_document_text(
                destination_path
            )

            relative_path = destination_path.relative_to(
                STORAGE_ROOT
            ).as_posix()

            imported_at = local_now_iso()

            try:
                document_id = document_repository.insert(
                    category_key=str(category["key"]),
                    stored_name=destination_path.name,
                    display_name=destination_path.name.replace("_", " "),
                    relative_path=relative_path,
                    extension=extension,
                    size_bytes=stat.st_size,
                    sha256=source_hash,
                    extracted_text=extracted_text,
                    created_at=datetime.fromtimestamp(
                        stat.st_ctime
                    ).astimezone().isoformat(timespec="seconds"),
                    imported_at=imported_at,
                    modified_at=datetime.fromtimestamp(
                        stat.st_mtime
                    ).astimezone().isoformat(timespec="seconds"),
                    source_mtime_ns=stat.st_mtime_ns,
                    indexed_at=imported_at,
                )

            except Exception:
                destination_path.unlink(missing_ok=True)
                raise

            event_bus.publish(
                DocumentImported(
                    document_id=document_id,
                    category_key=str(category["key"]),
                    relative_path=relative_path,
                )
            )

            logger.info(
                "Document importé : %s.",
                destination_path,
            )

            return destination_path

        except DuplicateDocumentError:
            raise

        except Exception as error:
            temporary_path.unlink(missing_ok=True)

            logger.exception(
                "Échec de l’import de %s.",
                source_path,
            )

            if isinstance(error, DocumentImportError):
                raise

            raise DocumentImportError(
                f"Impossible d’importer « {source_path.name} »."
            ) from error

    @staticmethod
    def get_files_in_category(category_key: str, search_query: str = ""):
        ArchiveFileService._get_category(category_key)

        return document_query_service.list_by_category(
            category_key,
            search_query,
        )

    @staticmethod
    def query_archive_vault(search_keyword: str):
        return document_query_service.search(
            search_keyword
        )

    @staticmethod
    def get_favorite_documents():
        return document_query_service.list_favorites()

    @staticmethod
    def get_upcoming_documents(days: int = 30):
        return document_query_service.list_upcoming(days)

    @staticmethod
    def count_files_in_category(category_key: str) -> int:
        ArchiveFileService._get_category(category_key)

        return document_query_service.count_by_category(
            category_key
        )

    @staticmethod
    def execute_native_file_open(target_path: str) -> None:
        path = Path(target_path)

        if not path.exists():
            raise StorageError(
                f"Le fichier ou dossier est introuvable : {path}"
            )

        try:
            if os.name == "nt":
                os.startfile(str(path))
                return

            import subprocess
            import sys

            command = (
                ["open", str(path)]
                if sys.platform == "darwin"
                else ["xdg-open", str(path)]
            )

            subprocess.Popen(command)

        except Exception as error:
            logger.exception(
                "Impossible d’ouvrir %s.",
                path,
            )

            raise StorageError(
                f"Impossible d’ouvrir « {path.name} »."
            ) from error

    @staticmethod
    def execute_rename_logic(category: dict, new_name: str) -> bool:
        try:
            category_service.rename_category(
                str(category["key"]),
                new_name,
            )

            return True

        except Exception:
            logger.exception(
                "Impossible de renommer la catégorie %s.",
                category.get("key"),
            )

            return False

    @staticmethod
    def execute_delete_logic(category_key: str, action: str) -> bool:
        try:
            if action == "move":
                category_service.delete_and_move_documents(
                    category_key
                )

            elif action == "keep":
                category_service.delete_and_trash_documents(
                    category_key
                )

            elif action == "none":
                category_service.delete_empty_category(
                    category_key
                )

            else:
                raise StorageError(
                    f"Action de suppression inconnue : {action}"
                )

            return True

        except Exception:
            logger.exception(
                "Impossible de supprimer la catégorie %s.",
                category_key,
            )

            return False

    @staticmethod
    def _create_application_directories() -> None:
        for directory in (
            APP_ROOT,
            STORAGE_ROOT,
            DATA_ROOT,
            BACKGROUND_ROOT,
            LOG_ROOT,
            TRASH_ROOT,
            UNSORTED_ROOT,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    @staticmethod
    def _migrate_legacy_layout_if_needed() -> None:
        migration_marker = (
            DATA_ROOT
            / ".legacy_migration_completed"
        )

        if migration_marker.exists():
            return

        try:
            if (
                LEGACY_DATABASE_PATH.exists()
                and LEGACY_DATABASE_PATH.resolve()
                != DB_PATH.resolve()
                and not DB_PATH.exists()
            ):
                shutil.copy2(
                    LEGACY_DATABASE_PATH,
                    DB_PATH,
                )

            for category in category_repository.list_all():
                category_key = str(category["key"])
                legacy_path = (
                    LEGACY_STORAGE_ROOT
                    / category_key
                )
                new_path = (
                    STORAGE_ROOT
                    / category_key
                )

                if (
                    legacy_path.exists()
                    and legacy_path.is_dir()
                    and not new_path.exists()
                ):
                    shutil.copytree(
                        legacy_path,
                        new_path,
                    )

            migration_marker.write_text(
                datetime.now()
                .astimezone()
                .isoformat(timespec="seconds"),
                encoding="utf-8",
            )

        except Exception:
            logger.exception(
                "La migration de l’ancienne organisation a échoué."
            )

    @staticmethod
    def _get_category(category_key: str) -> dict:
        category = category_repository.get(
            category_key
        )

        if category is None:
            raise CategoryNotFoundError(
                f"Le classeur « {category_key} » n’existe pas."
            )

        return category

    @staticmethod
    def _sanitize_component(value: str, replacement: str = "_") -> str:
        normalized = unicodedata.normalize(
            "NFKC",
            value,
        ).strip()

        normalized = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            replacement,
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            replacement,
            normalized,
        )

        normalized = re.sub(
            rf"{re.escape(replacement)}+",
            replacement,
            normalized,
        )

        normalized = normalized.strip(
            f" .{replacement}"
        )

        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *{
                f"COM{index}"
                for index in range(1, 10)
            },
            *{
                f"LPT{index}"
                for index in range(1, 10)
            },
        }

        if normalized.upper() in reserved_names:
            normalized = f"_{normalized}"

        return normalized[:180]

    @staticmethod
    def _build_unique_path(path: Path) -> Path:
        if not path.exists():
            return path

        counter = 2

        while True:
            candidate = path.with_name(
                f"{path.stem}_{counter}{path.suffix}"
            )

            if not candidate.exists():
                return candidate

            counter += 1

    @staticmethod
    def _compute_sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as source:
            for chunk in iter(
                lambda: source.read(
                    COPY_BUFFER_SIZE
                ),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _extract_document_text(path: Path) -> str:
        if path.suffix.casefold() != ".pdf":
            return ""

        return PdfExtractionService.extract_lowercase_text(
            path
        )
