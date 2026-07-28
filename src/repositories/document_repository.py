import sqlite3
from typing import Any

from core.database.database import database
from core.errors.exceptions import DatabaseError
from core.models.search_filters import SearchFilters, build_fts_query
from utils.text import normalize_search_text


class DocumentRepository:
    IMAGE_EXTENSIONS = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".gif",
        ".tif",
        ".tiff",
    )

    def insert(
        self,
        *,
        category_key: str,
        stored_name: str,
        display_name: str,
        relative_path: str,
        extension: str,
        size_bytes: int,
        sha256: str,
        extracted_text: str,
        created_at: str,
        imported_at: str,
        modified_at: str,
        source_mtime_ns: int = 0,
        indexed_at: str | None = None,
    ) -> int:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO documents (
                        category_key,
                        stored_name,
                        display_name,
                        searchable_name,
                        relative_path,
                        extension,
                        size_bytes,
                        sha256,
                        extracted_text,
                        created_at,
                        imported_at,
                        modified_at,
                        source_mtime_ns,
                        indexed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        category_key,
                        stored_name,
                        display_name,
                        normalize_search_text(display_name),
                        relative_path,
                        extension,
                        size_bytes,
                        sha256,
                        normalize_search_text(extracted_text),
                        created_at,
                        imported_at,
                        modified_at,
                        source_mtime_ns,
                        indexed_at,
                    ),
                )

                return int(cursor.lastrowid)

        except sqlite3.IntegrityError as error:
            raise DatabaseError(
                "Ce document est déjà enregistré dans la base."
            ) from error

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’enregistrer le document."
            ) from error

    def upsert(
        self,
        *,
        category_key: str,
        stored_name: str,
        display_name: str,
        relative_path: str,
        extension: str,
        size_bytes: int,
        sha256: str,
        extracted_text: str,
        created_at: str,
        imported_at: str,
        modified_at: str,
        source_mtime_ns: int = 0,
        indexed_at: str | None = None,
    ) -> None:
        try:
            with database.connection() as connection:
                connection.execute(
                    """
                    INSERT INTO documents (
                        category_key,
                        stored_name,
                        display_name,
                        searchable_name,
                        relative_path,
                        extension,
                        size_bytes,
                        sha256,
                        extracted_text,
                        created_at,
                        imported_at,
                        modified_at,
                        source_mtime_ns,
                        indexed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(relative_path)
                    DO UPDATE SET
                        category_key = excluded.category_key,
                        stored_name = excluded.stored_name,
                        display_name = excluded.display_name,
                        searchable_name = excluded.searchable_name,
                        extension = excluded.extension,
                        size_bytes = excluded.size_bytes,
                        sha256 = excluded.sha256,
                        extracted_text = excluded.extracted_text,
                        modified_at = excluded.modified_at,
                        source_mtime_ns = excluded.source_mtime_ns,
                        indexed_at = excluded.indexed_at
                    """,
                    (
                        category_key,
                        stored_name,
                        display_name,
                        normalize_search_text(display_name),
                        relative_path,
                        extension,
                        size_bytes,
                        sha256,
                        normalize_search_text(extracted_text),
                        created_at,
                        imported_at,
                        modified_at,
                        source_mtime_ns,
                        indexed_at,
                    ),
                )

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’indexer le document."
            ) from error

    def get(self, document_id: int) -> dict[str, Any] | None:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT
                        documents.*,
                        categories.name AS category_name,
                        (
                            SELECT GROUP_CONCAT(tags.name, ', ')
                            FROM document_tags
                            JOIN tags ON tags.id = document_tags.tag_id
                            WHERE document_tags.document_id = documents.id
                        ) AS tags
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.id = ?
                    LIMIT 1
                    """,
                    (document_id,),
                ).fetchone()

            return dict(row) if row else None

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire le document."
            ) from error

    def find_by_hash(self, sha256: str) -> dict[str, Any] | None:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT
                        documents.*,
                        categories.name AS category_name
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.sha256 = ?
                    LIMIT 1
                    """,
                    (sha256,),
                ).fetchone()

            return dict(row) if row else None

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de vérifier les doublons."
            ) from error


    def find_duplicate_candidates(
        self,
        *,
        extension: str,
        minimum_size: int,
        maximum_size: int,
        limit: int = 120,
    ) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        documents.id,
                        documents.display_name,
                        documents.relative_path,
                        documents.extension,
                        documents.size_bytes,
                        categories.name AS category_name
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.extension = ?
                      AND documents.size_bytes BETWEEN ? AND ?
                    ORDER BY ABS(documents.size_bytes - ?) ASC
                    LIMIT ?
                    """,
                    (
                        extension,
                        minimum_size,
                        maximum_size,
                        (minimum_size + maximum_size) // 2,
                        max(1, limit),
                    ),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de rechercher les doublons probables."
            ) from error

    def get_by_relative_path(self, relative_path: str) -> dict[str, Any] | None:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT *
                    FROM documents
                    WHERE relative_path = ?
                    LIMIT 1
                    """,
                    (relative_path,),
                ).fetchone()

            return dict(row) if row else None

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire le document."
            ) from error

    def list_by_category(
        self,
        category_key: str,
        search_query: str = "",
    ) -> list[dict[str, Any]]:
        filters = SearchFilters(
            category_key=category_key,
            sort_order="name",
        )

        if search_query.strip():
            return self.search_advanced(
                search_query,
                filters,
            )

        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        documents.*,
                        categories.name AS category_name,
                        (
                            SELECT GROUP_CONCAT(tags.name, ', ')
                            FROM document_tags
                            JOIN tags ON tags.id = document_tags.tag_id
                            WHERE document_tags.document_id = documents.id
                        ) AS tags,
                        'Fichier du classeur' AS match_reason
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.category_key = ?
                    ORDER BY
                        documents.is_favorite DESC,
                        documents.display_name COLLATE NOCASE ASC
                    """,
                    (category_key,),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les documents du classeur."
            ) from error


    def list_by_category_tree(
        self,
        category_key: str,
        search_query: str = "",
    ) -> list[dict[str, Any]]:
        if search_query.strip():
            rows = self.list_by_category(category_key, search_query)
            child_keys = [str(item["key"]) for item in __import__("repositories.category_repository", fromlist=["category_repository"]).category_repository.list_children(category_key)]
            for child_key in child_keys:
                rows.extend(self.list_by_category(child_key, search_query))
            unique = {int(row["id"]): row for row in rows}
            return list(unique.values())
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT documents.*, categories.name AS category_name,
                        (SELECT GROUP_CONCAT(tags.name, ', ') FROM document_tags
                         JOIN tags ON tags.id = document_tags.tag_id
                         WHERE document_tags.document_id = documents.id) AS tags,
                        'Fichier du classeur' AS match_reason
                    FROM documents
                    JOIN categories ON categories.key = documents.category_key
                    WHERE documents.category_key = ? OR categories.parent_key = ?
                    ORDER BY documents.is_favorite DESC, documents.display_name COLLATE NOCASE ASC
                    """,
                    (category_key, category_key),
                ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            raise DatabaseError("Impossible de lire les documents du classeur.") from error

    def search(
        self,
        search_query: str,
    ) -> list[dict[str, Any]]:
        return self.search_advanced(
            search_query,
            SearchFilters(),
        )

    def search_advanced(
        self,
        search_query: str,
        filters: SearchFilters,
    ) -> list[dict[str, Any]]:
        normalized_query = normalize_search_text(search_query)
        fts_query = build_fts_query(search_query)

        if not normalized_query and not self._has_active_filters(filters):
            return []

        conditions: list[str] = []
        parameters: list[Any] = []
        cte = ""
        candidate_join = ""
        score_expression = "0.0"
        match_reason = "'Correspondance avec les filtres'"

        if fts_query:
            wildcard = f"%{normalized_query}%"
            cte = """
                WITH candidates AS (
                    SELECT
                        rowid AS document_id,
                        bm25(documents_fts, 8.0, 2.0, 4.0) AS score
                    FROM documents_fts
                    WHERE documents_fts MATCH ?

                    UNION ALL

                    SELECT
                        document_tags.document_id,
                        25.0 AS score
                    FROM document_tags
                    JOIN tags ON tags.id = document_tags.tag_id
                    WHERE tags.normalized_name LIKE ?
                )
            """
            parameters.extend((fts_query, wildcard))
            candidate_join = (
                "JOIN candidates ON candidates.document_id = documents.id"
            )
            score_expression = "MIN(candidates.score)"
            match_reason = """
                CASE
                    WHEN documents.searchable_name LIKE ?
                    THEN 'Correspondance dans le titre'
                    WHEN documents.metadata_search LIKE ?
                    THEN 'Correspondance dans les informations'
                    WHEN EXISTS (
                        SELECT 1
                        FROM document_tags
                        JOIN tags ON tags.id = document_tags.tag_id
                        WHERE document_tags.document_id = documents.id
                          AND tags.normalized_name LIKE ?
                    )
                    THEN 'Correspondance dans les tags'
                    ELSE 'Correspondance dans le contenu'
                END
            """
            parameters.extend((wildcard, wildcard, wildcard))

        if filters.category_key:
            conditions.append("documents.category_key = ?")
            parameters.append(filters.category_key)

        if filters.file_type:
            if filters.file_type == "image":
                placeholders = ", ".join("?" for _ in self.IMAGE_EXTENSIONS)
                conditions.append(
                    f"documents.extension IN ({placeholders})"
                )
                parameters.extend(self.IMAGE_EXTENSIONS)
            else:
                conditions.append("documents.extension = ?")
                parameters.append(filters.file_type)

        if filters.favorites_only:
            conditions.append("documents.is_favorite = 1")

        if filters.person_query:
            conditions.append("LOWER(COALESCE(documents.person_name, '')) LIKE ?")
            parameters.append(f"%{normalize_search_text(filters.person_query)}%")

        if filters.tag_query:
            conditions.append("""EXISTS (
                SELECT 1 FROM document_tags filter_document_tags
                JOIN tags filter_tags ON filter_tags.id = filter_document_tags.tag_id
                WHERE filter_document_tags.document_id = documents.id
                  AND filter_tags.normalized_name LIKE ?
            )""")
            parameters.append(f"%{normalize_search_text(filters.tag_query)}%")

        imported_after = filters.imported_after()
        if imported_after:
            conditions.append("date(documents.imported_at) >= date(?)")
            parameters.append(imported_after)

        where_clause = (
            "WHERE " + " AND ".join(conditions)
            if conditions
            else ""
        )
        order_by = self._search_order_by(
            filters.sort_order,
            has_query=bool(fts_query),
        )
        limit = max(1, min(int(filters.limit), 500))
        parameters.append(limit)

        try:
            with database.connection() as connection:
                rows = connection.execute(
                    f"""
                    {cte}
                    SELECT
                        documents.*,
                        categories.name AS category_name,
                        (
                            SELECT GROUP_CONCAT(tags.name, ', ')
                            FROM document_tags
                            JOIN tags ON tags.id = document_tags.tag_id
                            WHERE document_tags.document_id = documents.id
                        ) AS tags,
                        {match_reason} AS match_reason,
                        {score_expression} AS search_score
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    {candidate_join}
                    {where_clause}
                    GROUP BY documents.id
                    ORDER BY {order_by}
                    LIMIT ?
                    """,
                    tuple(parameters),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible d’effectuer la recherche."
            ) from error

    @staticmethod
    def _has_active_filters(filters: SearchFilters) -> bool:
        return any(
            (
                filters.category_key,
                filters.file_type,
                filters.favorites_only,
                filters.imported_period,
                filters.person_query,
                filters.tag_query,
            )
        )

    @staticmethod
    def _search_order_by(
        sort_order: str,
        *,
        has_query: bool,
    ) -> str:
        if sort_order == "newest":
            return "datetime(documents.imported_at) DESC"
        if sort_order == "oldest":
            return "datetime(documents.imported_at) ASC"
        if sort_order == "name":
            return "documents.display_name COLLATE NOCASE ASC"
        if sort_order == "size_desc":
            return "documents.size_bytes DESC"
        if sort_order == "size_asc":
            return "documents.size_bytes ASC"
        if sort_order == "name_desc":
            return "documents.display_name COLLATE NOCASE DESC"
        if sort_order == "favorite":
            return "documents.is_favorite DESC, documents.display_name COLLATE NOCASE ASC"
        if has_query:
            return (
                "search_score ASC, documents.is_favorite DESC, "
                "documents.display_name COLLATE NOCASE ASC"
            )
        return (
            "documents.is_favorite DESC, "
            "documents.display_name COLLATE NOCASE ASC"
        )

    def list_favorites(self) -> list[dict[str, Any]]:
        return self._list_with_condition(
            condition="documents.is_favorite = 1",
            match_reason="Document favori",
            order_by="documents.display_name COLLATE NOCASE ASC",
        )

    def list_upcoming(self, days: int = 30) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        documents.*,
                        categories.name AS category_name,
                        (
                            SELECT GROUP_CONCAT(tags.name, ', ')
                            FROM document_tags
                            JOIN tags ON tags.id = document_tags.tag_id
                            WHERE document_tags.document_id = documents.id
                        ) AS tags,
                        'Échéance prochaine' AS match_reason
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.due_date IS NOT NULL
                      AND date(documents.due_date)
                          BETWEEN date('now') AND date('now', ?)
                    ORDER BY
                        date(documents.due_date) ASC,
                        documents.display_name COLLATE NOCASE ASC
                    """,
                    (f"+{days} days",),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les prochaines échéances."
            ) from error

    def update_location(
        self,
        document_id: int,
        *,
        category_key: str,
        stored_name: str,
        display_name: str,
        relative_path: str,
        modified_at: str,
        source_mtime_ns: int,
    ) -> None:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE documents
                    SET
                        category_key = ?,
                        stored_name = ?,
                        display_name = ?,
                        searchable_name = ?,
                        relative_path = ?,
                        modified_at = ?,
                        source_mtime_ns = ?
                    WHERE id = ?
                    """,
                    (
                        category_key,
                        stored_name,
                        display_name,
                        normalize_search_text(display_name),
                        relative_path,
                        modified_at,
                        source_mtime_ns,
                        document_id,
                    ),
                )

                if cursor.rowcount == 0:
                    raise DatabaseError(
                        "Le document demandé n’existe pas."
                    )

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de modifier le document."
            ) from error

    def delete(self, document_id: int) -> bool:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    "DELETE FROM documents WHERE id = ?",
                    (document_id,),
                )

            return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de supprimer le document."
            ) from error

    def delete_by_relative_path(self, relative_path: str) -> bool:
        try:
            with database.connection() as connection:
                cursor = connection.execute(
                    "DELETE FROM documents WHERE relative_path = ?",
                    (relative_path,),
                )

            return cursor.rowcount > 0

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de retirer le document de l’index."
            ) from error

    def count_by_category(self, category_key: str) -> int:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    "SELECT COUNT(*) FROM documents WHERE category_key = ?",
                    (category_key,),
                ).fetchone()

            return int(row[0]) if row else 0

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de compter les documents."
            ) from error

    def list_relative_paths(self) -> set[str]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    "SELECT relative_path FROM documents"
                ).fetchall()

            return {str(row["relative_path"]) for row in rows}

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire l’index des documents."
            ) from error

    def remove_missing(self, existing_relative_paths: set[str]) -> int:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    "SELECT id, relative_path FROM documents"
                ).fetchall()

                missing_ids = [
                    int(row["id"])
                    for row in rows
                    if str(row["relative_path"]) not in existing_relative_paths
                ]

                if not missing_ids:
                    return 0

                placeholders = ",".join("?" for _ in missing_ids)

                connection.execute(
                    f"DELETE FROM documents WHERE id IN ({placeholders})",
                    missing_ids,
                )

            return len(missing_ids)

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de nettoyer l’index des documents."
            ) from error

    def _list_with_condition(
        self,
        *,
        condition: str,
        match_reason: str,
        order_by: str,
    ) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    f"""
                    SELECT
                        documents.*,
                        categories.name AS category_name,
                        (
                            SELECT GROUP_CONCAT(tags.name, ', ')
                            FROM document_tags
                            JOIN tags ON tags.id = document_tags.tag_id
                            WHERE document_tags.document_id = documents.id
                        ) AS tags,
                        ? AS match_reason
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE {condition}
                    ORDER BY {order_by}
                    """,
                    (match_reason,),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les documents."
            ) from error


document_repository = DocumentRepository()