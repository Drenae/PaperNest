import logging
import sqlite3
from collections.abc import Callable

from core.config.constants import DEFAULT_CATEGORIES
from core.database.database import database
from core.errors.exceptions import DatabaseError
from utils.time import local_now_iso

logger = logging.getLogger(__name__)


Migration = Callable[[sqlite3.Connection], None]


class MigrationManager:
    CURRENT_VERSION = 6

    def __init__(self):
        self.migrations: dict[int, Migration] = {
            1: self._migration_1_initial_schema,
            2: self._migration_2_document_index,
            3: self._migration_3_trash_and_backup_support,
            4: self._migration_4_document_metadata,
            5: self._migration_5_full_text_search,
            6: self._migration_6_subcategories,
        }

    def migrate(self) -> None:
        try:
            with database.connection() as connection:
                self._ensure_metadata_table(connection)

                current_version = self._get_current_version(
                    connection
                )

                for version in range(
                    current_version + 1,
                    self.CURRENT_VERSION + 1,
                ):
                    migration = self.migrations.get(version)

                    if migration is None:
                        raise DatabaseError(
                            f"La migration {version} est introuvable."
                        )

                    logger.info(
                        "Application de la migration SQLite %s.",
                        version,
                    )

                    migration(connection)
                    self._set_current_version(
                        connection,
                        version,
                    )

                self._ensure_default_categories(
                    connection
                )

        except sqlite3.Error as error:
            logger.exception(
                "Impossible de migrer la base SQLite."
            )

            raise DatabaseError(
                "Impossible de mettre à jour la base de données."
            ) from error

    @staticmethod
    def _ensure_metadata_table(
        connection: sqlite3.Connection,
    ) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS application_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _get_current_version(
        connection: sqlite3.Connection,
    ) -> int:
        row = connection.execute(
            """
            SELECT value
            FROM application_metadata
            WHERE key = 'schema_version'
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            return 0

        try:
            return int(row["value"])

        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _set_current_version(
        connection: sqlite3.Connection,
        version: int,
    ) -> None:
        connection.execute(
            """
            INSERT INTO application_metadata (
                key,
                value
            )
            VALUES (
                'schema_version',
                ?
            )

            ON CONFLICT(key)
            DO UPDATE SET
                value = excluded.value
            """,
            (str(version),),
        )

    @staticmethod
    def _migration_1_initial_schema(
        connection: sqlite3.Connection,
    ) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                icon TEXT NOT NULL,
                color TEXT NOT NULL,
                bg TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_key TEXT NOT NULL,
                stored_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                relative_path TEXT UNIQUE NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL DEFAULT 0,
                sha256 TEXT,
                extracted_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,

                FOREIGN KEY (category_key)
                    REFERENCES categories(key)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );
            """
        )

    @staticmethod
    def _migration_2_document_index(
        connection: sqlite3.Connection,
    ) -> None:
        MigrationManager._add_column_if_missing(
            connection,
            "documents",
            "searchable_name",
            "TEXT NOT NULL DEFAULT ''",
        )

        MigrationManager._add_column_if_missing(
            connection,
            "documents",
            "source_mtime_ns",
            "INTEGER NOT NULL DEFAULT 0",
        )

        MigrationManager._add_column_if_missing(
            connection,
            "documents",
            "indexed_at",
            "TEXT",
        )

        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_documents_category
            ON documents(category_key);

            CREATE INDEX IF NOT EXISTS idx_documents_hash
            ON documents(sha256);

            CREATE INDEX IF NOT EXISTS idx_documents_name
            ON documents(searchable_name);

            CREATE INDEX IF NOT EXISTS idx_documents_modified
            ON documents(source_mtime_ns);
            """
        )

        connection.execute(
            """
            UPDATE documents
            SET searchable_name = lower(display_name)
            WHERE searchable_name = ''
            """
        )

    @staticmethod
    def _migration_3_trash_and_backup_support(
        connection: sqlite3.Connection,
    ) -> None:
        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_documents_relative_path
            ON documents(relative_path);

            CREATE INDEX IF NOT EXISTS idx_documents_imported_at
            ON documents(imported_at);
            """
        )

    @staticmethod
    def _migration_4_document_metadata(
        connection: sqlite3.Connection,
    ) -> None:
        columns = {
            "is_favorite": "INTEGER NOT NULL DEFAULT 0",
            "document_date": "TEXT",
            "due_date": "TEXT",
            "amount": "TEXT",
            "person_name": "TEXT NOT NULL DEFAULT ''",
            "notes": "TEXT NOT NULL DEFAULT ''",
            "metadata_search": "TEXT NOT NULL DEFAULT ''",
        }

        for column_name, definition in columns.items():
            MigrationManager._add_column_if_missing(
                connection,
                "documents",
                column_name,
                definition,
            )

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS document_tags (
                document_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,

                PRIMARY KEY (
                    document_id,
                    tag_id
                ),

                FOREIGN KEY (document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (tag_id)
                    REFERENCES tags(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_documents_favorite
            ON documents(is_favorite);

            CREATE INDEX IF NOT EXISTS idx_documents_document_date
            ON documents(document_date);

            CREATE INDEX IF NOT EXISTS idx_documents_due_date
            ON documents(due_date);

            CREATE INDEX IF NOT EXISTS idx_tags_normalized_name
            ON tags(normalized_name);
            """
        )

    @staticmethod
    def _migration_5_full_text_search(
        connection: sqlite3.Connection,
    ) -> None:
        connection.executescript(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(
                searchable_name,
                extracted_text,
                metadata_search,
                content='documents',
                content_rowid='id',
                tokenize='unicode61 remove_diacritics 2'
            );

            CREATE TRIGGER IF NOT EXISTS documents_fts_insert
            AFTER INSERT ON documents
            BEGIN
                INSERT INTO documents_fts(
                    rowid,
                    searchable_name,
                    extracted_text,
                    metadata_search
                )
                VALUES (
                    new.id,
                    new.searchable_name,
                    new.extracted_text,
                    new.metadata_search
                );
            END;

            CREATE TRIGGER IF NOT EXISTS documents_fts_delete
            AFTER DELETE ON documents
            BEGIN
                INSERT INTO documents_fts(
                    documents_fts,
                    rowid,
                    searchable_name,
                    extracted_text,
                    metadata_search
                )
                VALUES (
                    'delete',
                    old.id,
                    old.searchable_name,
                    old.extracted_text,
                    old.metadata_search
                );
            END;

            CREATE TRIGGER IF NOT EXISTS documents_fts_update
            AFTER UPDATE OF searchable_name, extracted_text, metadata_search
            ON documents
            BEGIN
                INSERT INTO documents_fts(
                    documents_fts,
                    rowid,
                    searchable_name,
                    extracted_text,
                    metadata_search
                )
                VALUES (
                    'delete',
                    old.id,
                    old.searchable_name,
                    old.extracted_text,
                    old.metadata_search
                );

                INSERT INTO documents_fts(
                    rowid,
                    searchable_name,
                    extracted_text,
                    metadata_search
                )
                VALUES (
                    new.id,
                    new.searchable_name,
                    new.extracted_text,
                    new.metadata_search
                );
            END;

            INSERT INTO documents_fts(documents_fts)
            VALUES ('rebuild');
            """
        )

    @staticmethod
    def _add_column_if_missing(
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        definition: str,
    ) -> None:
        columns = connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        column_names = {
            str(column["name"])
            for column in columns
        }

        if column_name in column_names:
            return

        connection.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {definition}
            """
        )


    @staticmethod
    def _migration_6_subcategories(
        connection: sqlite3.Connection,
    ) -> None:
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(categories)").fetchall()}
        if "parent_key" not in columns:
            connection.execute("ALTER TABLE categories ADD COLUMN parent_key TEXT")
        if "position" not in columns:
            connection.execute("ALTER TABLE categories ADD COLUMN position INTEGER NOT NULL DEFAULT 0")
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_categories_parent_position "
            "ON categories(parent_key, position, name)"
        )

    @staticmethod
    def _ensure_default_categories(
        connection: sqlite3.Connection,
    ) -> None:
        row = connection.execute(
            """
            SELECT COUNT(*)
            FROM categories
            """
        ).fetchone()

        if row and int(row[0]) > 0:
            return

        now = local_now_iso()

        connection.executemany(
            """
            INSERT INTO categories (
                key,
                name,
                icon,
                color,
                bg,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    key,
                    name,
                    icon,
                    color,
                    bg,
                    now,
                    now,
                )
                for key, name, icon, color, bg
                in DEFAULT_CATEGORIES
            ],
        )


migration_manager = MigrationManager()