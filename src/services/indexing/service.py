import hashlib
import logging
from datetime import datetime
from pathlib import Path

from core.config.constants import STORAGE_ROOT
from core.events.event_bus import IndexUpdated, event_bus
from utils.text import normalize_search_text
from utils.time import local_now_iso
from repositories.category_repository import category_repository
from repositories.document_repository import document_repository
from services.pdf.service import PdfExtractionService


logger = logging.getLogger(__name__)


class DocumentIndexService:
    @staticmethod
    def synchronize() -> dict[str, int]:
        statistics = {
            "new": 0,
            "updated": 0,
            "unchanged": 0,
            "missing": 0,
            "errors": 0,
        }

        physical_relative_paths: set[str] = set()

        for category in category_repository.list_all():
            category_key = str(category["key"])
            category_path = STORAGE_ROOT / category_key
            category_path.mkdir(parents=True, exist_ok=True)

            for file_path in category_path.iterdir():
                if not file_path.is_file():
                    continue

                if file_path.name.endswith(".part"):
                    logger.warning("Fichier temporaire ignoré : %s", file_path)
                    continue

                try:
                    relative_path = file_path.relative_to(STORAGE_ROOT).as_posix()
                    physical_relative_paths.add(relative_path)

                    result = DocumentIndexService.index_file_if_required(
                        category_key=category_key,
                        file_path=file_path,
                        relative_path=relative_path,
                    )

                    statistics[result] += 1

                except Exception:
                    statistics["errors"] += 1
                    logger.exception(
                        "Impossible d’indexer le document %s.",
                        file_path,
                    )

        statistics["missing"] = document_repository.remove_missing(
            physical_relative_paths
        )

        event_bus.publish(
            IndexUpdated(
                new_count=statistics["new"],
                updated_count=statistics["updated"],
                missing_count=statistics["missing"],
                error_count=statistics["errors"],
            )
        )

        logger.info(
            "Synchronisation terminée : %s",
            statistics,
        )

        return statistics

    @staticmethod
    def index_file_if_required(
        *,
        category_key: str,
        file_path: Path,
        relative_path: str,
    ) -> str:
        stat = file_path.stat()
        existing = document_repository.get_by_relative_path(relative_path)

        if existing:
            same_size = int(existing["size_bytes"]) == stat.st_size
            same_mtime = int(existing.get("source_mtime_ns") or 0) == stat.st_mtime_ns
            has_hash = bool(existing.get("sha256"))

            if same_size and same_mtime and has_hash:
                return "unchanged"

        file_hash = DocumentIndexService.compute_sha256(file_path)
        extracted_text = normalize_search_text(
            DocumentIndexService.extract_text(file_path)
        )

        display_name = DocumentIndexService.build_display_name(file_path)
        indexed_at = local_now_iso()

        document_repository.upsert(
            category_key=category_key,
            stored_name=file_path.name,
            display_name=display_name,
            relative_path=relative_path,
            extension=file_path.suffix.casefold(),
            size_bytes=stat.st_size,
            sha256=file_hash,
            extracted_text=extracted_text,
            created_at=datetime.fromtimestamp(
                stat.st_ctime
            ).astimezone().isoformat(timespec="seconds"),
            imported_at=(
                str(existing["imported_at"])
                if existing and existing.get("imported_at")
                else indexed_at
            ),
            modified_at=datetime.fromtimestamp(
                stat.st_mtime
            ).astimezone().isoformat(timespec="seconds"),
            source_mtime_ns=stat.st_mtime_ns,
            indexed_at=indexed_at,
        )

        if existing:
            logger.info("Index mis à jour : %s", file_path)
            return "updated"

        logger.info("Nouveau document indexé : %s", file_path)
        return "new"

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        digest = hashlib.sha256()

        with file_path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def extract_text(file_path: Path) -> str:
        if file_path.suffix.casefold() != ".pdf":
            return ""

        return PdfExtractionService.extract_lowercase_text(file_path)

    @staticmethod
    def build_display_name(file_path: Path) -> str:
        return file_path.name.replace("_", " ")