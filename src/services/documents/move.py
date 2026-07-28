import logging
import shutil
from pathlib import Path

from core.config.constants import STORAGE_ROOT
from core.events.event_bus import DocumentMoved, event_bus
from core.errors.exceptions import (
    CategoryNotFoundError,
    DocumentNotFoundError,
    StorageError,
)
from utils.time import local_now_iso
from repositories.category_repository import category_repository
from repositories.document_repository import document_repository


logger = logging.getLogger(__name__)


class DocumentMoveService:
    def move(
        self,
        document_id: int,
        destination_category_key: str,
    ) -> Path:
        document = document_repository.get(document_id)

        if document is None:
            raise DocumentNotFoundError(
                "Le document est introuvable."
            )

        category = category_repository.get(
            destination_category_key
        )

        if category is None:
            raise CategoryNotFoundError(
                "Le classeur de destination n'existe pas."
            )

        source_path = (
            STORAGE_ROOT
            / str(document["relative_path"])
        )

        if not source_path.exists():
            raise StorageError(
                "Le fichier n'existe plus."
            )

        destination_directory = (
            STORAGE_ROOT
            / destination_category_key
        )

        destination_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_path = (
            destination_directory
            / source_path.name
        )

        counter = 2

        while destination_path.exists():
            destination_path = (
                destination_directory
                / f"{source_path.stem}_{counter}{source_path.suffix}"
            )

            counter += 1

        shutil.move(
            str(source_path),
            str(destination_path),
        )

        relative_path = destination_path.relative_to(
            STORAGE_ROOT
        ).as_posix()

        stat = destination_path.stat()

        document_repository.update_location(
            document_id,
            category_key=destination_category_key,
            stored_name=destination_path.name,
            display_name=destination_path.name.replace(
                "_",
                " ",
            ),
            relative_path=relative_path,
            modified_at=local_now_iso(),
            source_mtime_ns=stat.st_mtime_ns,
        )

        event_bus.publish(
            DocumentMoved(
                document_id=document_id,
                old_category_key=str(
                    document["category_key"]
                ),
                new_category_key=destination_category_key,
            )
        )

        logger.info(
            "Document déplacé : %s -> %s",
            source_path,
            destination_path,
        )

        return destination_path


document_move_service = DocumentMoveService()