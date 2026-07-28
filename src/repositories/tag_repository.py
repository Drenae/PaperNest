import sqlite3
from typing import Any

from core.database.database import database
from core.errors.exceptions import DatabaseError, DocumentNotFoundError
from utils.text import normalize_search_text
from utils.time import local_now_iso


class TagRepository:
    def list_all(self) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        tags.id,
                        tags.name,
                        tags.normalized_name,
                        tags.created_at,
                        COUNT(document_tags.document_id) AS document_count
                    FROM tags
                    LEFT JOIN document_tags ON document_tags.tag_id = tags.id
                    GROUP BY tags.id
                    ORDER BY tags.name COLLATE NOCASE ASC
                    """
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les tags."
            ) from error

    def list_names(self) -> list[str]:
        return [str(tag["name"]) for tag in self.list_all()]

    def list_for_document(self, document_id: int) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        tags.id,
                        tags.name,
                        tags.normalized_name,
                        tags.created_at
                    FROM tags
                    JOIN document_tags ON document_tags.tag_id = tags.id
                    WHERE document_tags.document_id = ?
                    ORDER BY tags.name COLLATE NOCASE ASC
                    """,
                    (document_id,),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les tags du document."
            ) from error

    def replace_for_document(self, document_id: int, tags: list[str]) -> list[str]:
        normalized_tags = self.normalize_tags(tags)

        try:
            with database.connection() as connection:
                document = connection.execute(
                    """
                    SELECT 1
                    FROM documents
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (document_id,),
                ).fetchone()

                if document is None:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

                connection.execute(
                    """
                    DELETE FROM document_tags
                    WHERE document_id = ?
                    """,
                    (document_id,),
                )

                for tag_name in normalized_tags:
                    normalized_name = normalize_search_text(tag_name)

                    connection.execute(
                        """
                        INSERT INTO tags (
                            name,
                            normalized_name,
                            created_at
                        )
                        VALUES (?, ?, ?)
                        ON CONFLICT(normalized_name)
                        DO UPDATE SET name = excluded.name
                        """,
                        (
                            tag_name,
                            normalized_name,
                            local_now_iso(),
                        ),
                    )

                    tag_row = connection.execute(
                        """
                        SELECT id
                        FROM tags
                        WHERE normalized_name = ?
                        LIMIT 1
                        """,
                        (normalized_name,),
                    ).fetchone()

                    if tag_row is None:
                        raise DatabaseError(
                            "Impossible de créer le tag."
                        )

                    connection.execute(
                        """
                        INSERT OR IGNORE INTO document_tags (
                            document_id,
                            tag_id
                        )
                        VALUES (?, ?)
                        """,
                        (
                            document_id,
                            int(tag_row["id"]),
                        ),
                    )

                self._delete_unused_tags(connection)

            return normalized_tags

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’enregistrer les tags."
            ) from error

    def add_to_document(self, document_id: int, tag_name: str) -> str:
        normalized_tags = self.normalize_tags([tag_name])

        if not normalized_tags:
            raise ValueError("Le tag est vide.")

        clean_name = normalized_tags[0]
        normalized_name = normalize_search_text(clean_name)

        try:
            with database.connection() as connection:
                document = connection.execute(
                    """
                    SELECT 1
                    FROM documents
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (document_id,),
                ).fetchone()

                if document is None:
                    raise DocumentNotFoundError(
                        "Le document demandé n’existe pas."
                    )

                connection.execute(
                    """
                    INSERT INTO tags (
                        name,
                        normalized_name,
                        created_at
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT(normalized_name)
                    DO UPDATE SET name = excluded.name
                    """,
                    (
                        clean_name,
                        normalized_name,
                        local_now_iso(),
                    ),
                )

                tag_row = connection.execute(
                    """
                    SELECT id
                    FROM tags
                    WHERE normalized_name = ?
                    LIMIT 1
                    """,
                    (normalized_name,),
                ).fetchone()

                connection.execute(
                    """
                    INSERT OR IGNORE INTO document_tags (
                        document_id,
                        tag_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        document_id,
                        int(tag_row["id"]),
                    ),
                )

            return clean_name

        except DocumentNotFoundError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’ajouter le tag."
            ) from error

    def remove_from_document(self, document_id: int, tag_name: str) -> bool:
        normalized_name = normalize_search_text(tag_name)

        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    DELETE FROM document_tags
                    WHERE document_id = ?
                      AND tag_id = (
                          SELECT id
                          FROM tags
                          WHERE normalized_name = ?
                          LIMIT 1
                      )
                    """,
                    (
                        document_id,
                        normalized_name,
                    ),
                )

                self._delete_unused_tags(connection)

            return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de retirer le tag."
            ) from error

    def rename(self, old_name: str, new_name: str) -> str:
        old_normalized = normalize_search_text(old_name)
        normalized_tags = self.normalize_tags([new_name])

        if not normalized_tags:
            raise ValueError("Le nouveau nom du tag est vide.")

        clean_name = normalized_tags[0]
        new_normalized = normalize_search_text(clean_name)

        try:
            with database.connection() as connection:
                current = connection.execute(
                    """
                    SELECT id
                    FROM tags
                    WHERE normalized_name = ?
                    LIMIT 1
                    """,
                    (old_normalized,),
                ).fetchone()

                if current is None:
                    raise DatabaseError(
                        "Le tag demandé n’existe pas."
                    )

                existing = connection.execute(
                    """
                    SELECT id
                    FROM tags
                    WHERE normalized_name = ?
                    LIMIT 1
                    """,
                    (new_normalized,),
                ).fetchone()

                if existing and int(existing["id"]) != int(current["id"]):
                    connection.execute(
                        """
                        INSERT OR IGNORE INTO document_tags (
                            document_id,
                            tag_id
                        )
                        SELECT document_id, ?
                        FROM document_tags
                        WHERE tag_id = ?
                        """,
                        (
                            int(existing["id"]),
                            int(current["id"]),
                        ),
                    )

                    connection.execute(
                        """
                        DELETE FROM document_tags
                        WHERE tag_id = ?
                        """,
                        (int(current["id"]),),
                    )

                    connection.execute(
                        """
                        DELETE FROM tags
                        WHERE id = ?
                        """,
                        (int(current["id"]),),
                    )

                else:
                    connection.execute(
                        """
                        UPDATE tags
                        SET
                            name = ?,
                            normalized_name = ?
                        WHERE id = ?
                        """,
                        (
                            clean_name,
                            new_normalized,
                            int(current["id"]),
                        ),
                    )

            return clean_name

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de renommer le tag."
            ) from error

    def delete(self, tag_name: str) -> bool:
        normalized_name = normalize_search_text(tag_name)

        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT id
                    FROM tags
                    WHERE normalized_name = ?
                    LIMIT 1
                    """,
                    (normalized_name,),
                ).fetchone()

                if row is None:
                    return False

                connection.execute(
                    """
                    DELETE FROM document_tags
                    WHERE tag_id = ?
                    """,
                    (int(row["id"]),),
                )

                connection.execute(
                    """
                    DELETE FROM tags
                    WHERE id = ?
                    """,
                    (int(row["id"]),),
                )

            return True

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de supprimer le tag."
            ) from error

    @staticmethod
    def normalize_tags(tags: list[str]) -> list[str]:
        unique_tags: dict[str, str] = {}

        for raw_tag in tags:
            clean_tag = " ".join(raw_tag.strip().split())

            if not clean_tag:
                continue

            if len(clean_tag) > 50:
                raise ValueError(
                    "Un tag ne peut pas dépasser 50 caractères."
                )

            normalized_name = normalize_search_text(clean_tag)

            if normalized_name:
                unique_tags[normalized_name] = clean_tag

        if len(unique_tags) > 20:
            raise ValueError(
                "Un document ne peut pas contenir plus de 20 tags."
            )

        return sorted(
            unique_tags.values(),
            key=normalize_search_text,
        )

    @staticmethod
    def _delete_unused_tags(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            DELETE FROM tags
            WHERE id NOT IN (
                SELECT DISTINCT tag_id
                FROM document_tags
            )
            """
        )

    def list_names_for_document(self, document_id: int) -> list[str]:
        return [
            str(tag["name"])
            for tag in self.list_for_document(document_id)
        ]


tag_repository = TagRepository()