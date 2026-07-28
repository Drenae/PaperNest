import shutil
import sqlite3
from pathlib import Path

from core.database.database import database
from core.errors.exceptions import DatabaseError


class BackupRepository:
    REQUIRED_TABLES = {
        "categories",
        "documents",
        "application_metadata",
    }

    def create_database_copy(self, destination_path: str | Path) -> Path:
        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.unlink(missing_ok=True)

        try:
            with database.connection() as source:
                with sqlite3.connect(str(destination)) as target:
                    source.backup(target)

            self.verify_database(destination)
            return destination

        except sqlite3.Error as error:
            destination.unlink(missing_ok=True)

            raise DatabaseError(
                "Impossible de copier la base de données."
            ) from error

    def verify_database(self, database_path: str | Path) -> None:
        path = Path(database_path)

        if not path.exists() or not path.is_file():
            raise DatabaseError(
                "La base de données est introuvable."
            )

        try:
            with sqlite3.connect(str(path)) as connection:
                integrity_result = connection.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

                if not integrity_result or str(integrity_result[0]).casefold() != "ok":
                    raise DatabaseError(
                        "La base de données est endommagée."
                    )

                rows = connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    """
                ).fetchall()

                existing_tables = {
                    str(row[0])
                    for row in rows
                }

                missing_tables = self.REQUIRED_TABLES - existing_tables

                if missing_tables:
                    raise DatabaseError(
                        "La base de données est incomplète."
                    )

        except DatabaseError:
            raise

        except sqlite3.Error as error:
            raise DatabaseError(
                "La base de données est illisible."
            ) from error

    def restore_database(self, source_path: str | Path, destination_path: str | Path) -> Path:
        source = Path(source_path)
        destination = Path(destination_path)

        self.verify_database(source)

        destination.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = destination.with_name(
            f"{destination.name}.restoring"
        )

        previous_path = destination.with_name(
            f"{destination.name}.previous"
        )

        temporary_path.unlink(missing_ok=True)
        previous_path.unlink(missing_ok=True)

        shutil.copy2(source, temporary_path)
        self.verify_database(temporary_path)

        try:
            if destination.exists():
                destination.replace(previous_path)

            temporary_path.replace(destination)
            self.verify_database(destination)

        except Exception:
            destination.unlink(missing_ok=True)

            if previous_path.exists():
                previous_path.replace(destination)

            temporary_path.unlink(missing_ok=True)
            raise

        previous_path.unlink(missing_ok=True)
        return destination

    def get_schema_version(self, database_path: str | Path | None = None) -> int:
        path = Path(database_path) if database_path else database.database_path

        try:
            with sqlite3.connect(str(path)) as connection:
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

            return int(row[0])

        except (sqlite3.Error, TypeError, ValueError) as error:
            raise DatabaseError(
                "Impossible de lire la version de la base."
            ) from error


backup_repository = BackupRepository()