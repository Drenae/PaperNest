import sqlite3
from typing import Any

from core.database.database import database
from core.errors.exceptions import DatabaseError, DocumentNotFoundError
from utils.text import normalize_search_text
from utils.time import local_now_iso
from repositories.tag_repository import tag_repository


class MetadataRepository:
    def get(self, document_id: int) -> dict[str, Any]:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        is_favorite,
                        document_date,
                        due_date,
                        amount,
                        person_name,
                        notes,
                        metadata_search
                    FROM documents
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (document_id,),
                ).fetchone()

            if row is None:
                raise DocumentNotFoundError(
                    "Le document demandé n’existe pas."
                )

            result = dict(row)
            result["tags"] = tag_repository.list_names_for_document(
                document_id
            )

            return result

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les informations du document."
            ) from error

    def update(
        self,
        document_id: int,
        *,
        is_favorite: bool,
        document_date: str | None,
        due_date: str | None,
        amount: str | None,
        person_name: str,
        notes: str,
        tags: list[str],
    ) -> dict[str, Any]:
        clean_person_name = " ".join(person_name.strip().split())
        clean_notes = notes.strip()
        normalized_tags = tag_repository.normalize_tags(tags)

        metadata_search = normalize_search_text(
            " ".join(
                [
                    clean_person_name,
                    clean_notes,
                    amount or "",
                    " ".join(normalized_tags),
                ]
            )
        )

        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE documents
                    SET
                        is_favorite = ?,
                        document_date = ?,
                        due_date = ?,
                        amount = ?,
                        person_name = ?,
                        notes = ?,
                        metadata_search = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (
                        int(is_favorite),
                        document_date,
                        due_date,
                        amount,
                        clean_person_name,
                        clean_notes,
                        metadata_search,
                        local_now_iso(),
                        document_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

            tag_repository.replace_for_document(
                document_id,
                normalized_tags,
            )

            return self.get(document_id)

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’enregistrer les informations du document."
            ) from error

    def toggle_favorite(self, document_id: int) -> bool:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT is_favorite
                    FROM documents
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (document_id,),
                ).fetchone()

                if row is None:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

                new_value = not bool(row["is_favorite"])

                connection.execute(
                    """
                    UPDATE documents
                    SET
                        is_favorite = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (
                        int(new_value),
                        local_now_iso(),
                        document_id,
                    ),
                )

            return new_value

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de modifier le favori."
            ) from error

    def set_favorite(self, document_id: int, value: bool) -> None:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE documents
                    SET
                        is_favorite = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (
                        int(value),
                        local_now_iso(),
                        document_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de modifier le favori."
            ) from error

    def clear(self, document_id: int) -> None:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE documents
                    SET
                        is_favorite = 0,
                        document_date = NULL,
                        due_date = NULL,
                        amount = NULL,
                        person_name = '',
                        notes = '',
                        metadata_search = '',
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (
                        local_now_iso(),
                        document_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

            tag_repository.replace_for_document(
                document_id,
                [],
            )

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’effacer les informations du document."
            ) from error


metadata_repository = MetadataRepository()