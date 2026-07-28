import sqlite3
from typing import Any

from core.database.database import database
from core.errors.exceptions import DatabaseError


class StatisticsRepository:
    def get_dashboard_statistics(self) -> dict[str, int]:
        try:
            with database.connection() as connection:
                document_stats = connection.execute(
                    """
                    SELECT
                        COUNT(*) AS total_documents,
                        COALESCE(SUM(size_bytes), 0) AS total_size_bytes,
                        COALESCE(
                            SUM(
                                CASE
                                    WHEN is_favorite = 1 THEN 1
                                    ELSE 0
                                END
                            ),
                            0
                        ) AS favorite_documents,
                        COALESCE(
                            SUM(
                                CASE
                                    WHEN due_date IS NOT NULL
                                     AND date(due_date)
                                         BETWEEN date('now')
                                         AND date('now', '+30 days')
                                    THEN 1
                                    ELSE 0
                                END
                            ),
                            0
                        ) AS upcoming_documents,
                        COALESCE(
                            SUM(
                                CASE
                                    WHEN date(imported_at)
                                         >= date('now', '-30 days')
                                    THEN 1
                                    ELSE 0
                                END
                            ),
                            0
                        ) AS imported_last_30_days
                    FROM documents
                    """
                ).fetchone()

                category_count = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM categories
                    """
                ).fetchone()

                tag_count = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM tags
                    """
                ).fetchone()

            return {
                "total_documents": int(document_stats["total_documents"] or 0),
                "total_size_bytes": int(document_stats["total_size_bytes"] or 0),
                "favorite_documents": int(
                    document_stats["favorite_documents"] or 0
                ),
                "upcoming_documents": int(
                    document_stats["upcoming_documents"] or 0
                ),
                "imported_last_30_days": int(
                    document_stats["imported_last_30_days"] or 0
                ),
                "category_count": int(category_count[0] or 0),
                "tag_count": int(tag_count[0] or 0),
            }

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les statistiques."
            ) from error

    def get_category_distribution(self) -> list[dict[str, Any]]:
        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        categories.key AS category_key,
                        categories.name AS category_name,
                        categories.color,
                        COUNT(documents.id) AS document_count,
                        COALESCE(SUM(documents.size_bytes), 0) AS size_bytes
                    FROM categories
                    LEFT JOIN documents
                        ON documents.category_key = categories.key
                    GROUP BY categories.id
                    ORDER BY
                        document_count DESC,
                        categories.name COLLATE NOCASE ASC
                    """
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire la répartition des catégories."
            ) from error

    def get_recent_documents(self, limit: int = 10) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 100))

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
                        documents.imported_at,
                        documents.is_favorite,
                        categories.key AS category_key,
                        categories.name AS category_name
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    ORDER BY datetime(documents.imported_at) DESC
                    LIMIT ?
                    """,
                    (safe_limit,),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les documents récents."
            ) from error

    def get_upcoming_deadlines(
        self,
        days: int = 30,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        safe_days = max(1, min(days, 3650))
        safe_limit = max(1, min(limit, 100))

        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        documents.id,
                        documents.display_name,
                        documents.relative_path,
                        documents.due_date,
                        documents.person_name,
                        documents.amount,
                        categories.key AS category_key,
                        categories.name AS category_name,
                        CAST(
                            julianday(documents.due_date)
                            - julianday(date('now'))
                            AS INTEGER
                        ) AS days_remaining
                    FROM documents
                    JOIN categories
                        ON categories.key = documents.category_key
                    WHERE documents.due_date IS NOT NULL
                      AND date(documents.due_date)
                          BETWEEN date('now') AND date('now', ?)
                    ORDER BY
                        date(documents.due_date) ASC,
                        documents.display_name COLLATE NOCASE ASC
                    LIMIT ?
                    """,
                    (
                        f"+{safe_days} days",
                        safe_limit,
                    ),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire les prochaines échéances."
            ) from error

    def get_monthly_imports(self, months: int = 12) -> list[dict[str, Any]]:
        safe_months = max(1, min(months, 60))

        try:
            with database.connection() as connection:
                rows = connection.execute(
                    """
                    WITH RECURSIVE months(month_start, position) AS (
                        SELECT
                            date('now', 'start of month'),
                            0

                        UNION ALL

                        SELECT
                            date(month_start, '-1 month'),
                            position + 1
                        FROM months
                        WHERE position < ?
                    )
                    SELECT
                        strftime('%Y-%m', months.month_start) AS month,
                        COUNT(documents.id) AS document_count,
                        COALESCE(SUM(documents.size_bytes), 0) AS size_bytes
                    FROM months
                    LEFT JOIN documents
                        ON strftime('%Y-%m', documents.imported_at)
                           = strftime('%Y-%m', months.month_start)
                    GROUP BY months.month_start
                    ORDER BY months.month_start ASC
                    """,
                    (safe_months - 1,),
                ).fetchall()

            return [dict(row) for row in rows]

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de lire l’historique des imports."
            ) from error

    def count_overdue_documents(self) -> int:
        try:
            with database.connection() as connection:
                row = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM documents
                    WHERE due_date IS NOT NULL
                      AND date(due_date) < date('now')
                    """
                ).fetchone()

            return int(row[0]) if row else 0

        except sqlite3.Error as error:
            raise DatabaseError(
                "Impossible de compter les documents expirés."
            ) from error


statistics_repository = StatisticsRepository()