import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from core.config.constants import DATA_ROOT, DB_PATH
from core.errors.exceptions import DatabaseError


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, database_path: Path = DB_PATH):
        self.database_path = database_path

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(
            str(self.database_path),
            timeout=15,
        )

        connection.row_factory = sqlite3.Row

        try:
            self._configure_connection(connection)
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def execute_script(self, script: str) -> None:
        try:
            with self.connection() as connection:
                connection.executescript(script)

        except sqlite3.Error as error:
            logger.exception(
                "Impossible d’exécuter le script SQLite."
            )

            raise DatabaseError(
                "Impossible de mettre à jour la base de données."
            ) from error

    def integrity_check(self) -> bool:
        try:
            with self.connection() as connection:
                result = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

            return bool(
                result
                and str(result[0]).casefold() == "ok"
            )

        except sqlite3.Error:
            logger.exception(
                "Impossible de vérifier l’intégrité de la base."
            )

            return False

    def table_exists(self, table_name: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = ?
                LIMIT 1
                """,
                (table_name,),
            ).fetchone()

        return row is not None

    def index_exists(self, index_name: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'index'
                  AND name = ?
                LIMIT 1
                """,
                (index_name,),
            ).fetchone()

        return row is not None

    def get_table_columns(self, table_name: str) -> set[str]:
        if not self._is_safe_identifier(table_name):
            raise ValueError(
                "Nom de table SQLite invalide."
            )

        with self.connection() as connection:
            rows = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

        return {
            str(row["name"])
            for row in rows
        }

    def add_column_if_missing(
        self,
        table_name: str,
        column_name: str,
        definition: str,
    ) -> bool:
        if not self._is_safe_identifier(table_name):
            raise ValueError(
                "Nom de table SQLite invalide."
            )

        if not self._is_safe_identifier(column_name):
            raise ValueError(
                "Nom de colonne SQLite invalide."
            )

        existing_columns = self.get_table_columns(
            table_name
        )

        if column_name in existing_columns:
            return False

        try:
            with self.connection() as connection:
                connection.execute(
                    f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} {definition}
                    """
                )

            logger.info(
                "Colonne ajoutée : %s.%s",
                table_name,
                column_name,
            )

            return True

        except sqlite3.Error as error:
            logger.exception(
                "Impossible d’ajouter la colonne %s.%s.",
                table_name,
                column_name,
            )

            raise DatabaseError(
                "Impossible de mettre à jour la structure "
                "de la base de données."
            ) from error

    @staticmethod
    def _configure_connection(connection: sqlite3.Connection) -> None:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA busy_timeout = 15000")

    @staticmethod
    def _is_safe_identifier(value: str) -> bool:
        if not value:
            return False

        return value.replace("_", "").isalnum()


database = Database()