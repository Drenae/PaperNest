import hashlib
import json
import logging
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from core.config.constants import APP_NAME, BACKUP_ROOT, DB_PATH, STORAGE_ROOT
from core.events.event_bus import BackupCreated, BackupRestored, event_bus
from core.errors.exceptions import PaperNestError
from repositories.backup_repository import backup_repository
from services.indexing.service import DocumentIndexService


logger = logging.getLogger(__name__)


class BackupError(PaperNestError):
    pass


class InvalidBackupError(BackupError):
    pass


class BackupService:
    FORMAT_VERSION = 1
    MANIFEST_NAME = "manifest.json"
    DATABASE_ARCHIVE_PATH = "data/papernest.db"
    DOCUMENTS_ARCHIVE_ROOT = "archives"

    @staticmethod
    def create_backup(destination_directory: str | Path | None = None, *, safety_backup: bool = False) -> Path:
        destination_root = Path(destination_directory).expanduser() if destination_directory else BACKUP_ROOT
        destination_root.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        prefix = "PaperNest_securite" if safety_backup else "PaperNest_sauvegarde"
        backup_path = BackupService._build_unique_path(destination_root / f"{prefix}_{timestamp}.zip")
        temporary_path = backup_path.with_suffix(".zip.part")
        temporary_path.unlink(missing_ok=True)

        try:
            DocumentIndexService.synchronize()

            with tempfile.TemporaryDirectory(prefix="papernest_backup_") as temporary_directory:
                temporary_root = Path(temporary_directory)
                database_copy = temporary_root / "papernest.db"

                backup_repository.create_database_copy(database_copy)
                manifest = BackupService._build_manifest(database_copy)

                with zipfile.ZipFile(
                    temporary_path,
                    mode="w",
                    compression=zipfile.ZIP_DEFLATED,
                    compresslevel=6,
                ) as archive:
                    archive.write(database_copy, BackupService.DATABASE_ARCHIVE_PATH)

                    for document in manifest["documents"]:
                        relative_path = str(document["relative_path"])
                        source_path = STORAGE_ROOT / relative_path
                        archive.write(
                            source_path,
                            f"{BackupService.DOCUMENTS_ARCHIVE_ROOT}/{relative_path}",
                        )

                    archive.writestr(
                        BackupService.MANIFEST_NAME,
                        json.dumps(manifest, ensure_ascii=False, indent=2),
                    )

            BackupService.verify_backup(temporary_path)
            temporary_path.replace(backup_path)

            event_bus.publish(
                BackupCreated(backup_path=str(backup_path))
            )

            logger.info("Sauvegarde créée : %s", backup_path)
            return backup_path

        except BackupError:
            temporary_path.unlink(missing_ok=True)
            raise

        except Exception as error:
            temporary_path.unlink(missing_ok=True)
            logger.exception("Échec de la sauvegarde PaperNest.")

            raise BackupError(
                "Impossible de créer la sauvegarde."
            ) from error

    @staticmethod
    def verify_backup(backup_file: str | Path) -> dict[str, Any]:
        backup_path = Path(backup_file).expanduser()

        if not backup_path.exists() or not backup_path.is_file():
            raise InvalidBackupError(
                "Le fichier de sauvegarde est introuvable."
            )

        if not zipfile.is_zipfile(backup_path):
            raise InvalidBackupError(
                "Le fichier sélectionné n’est pas une archive ZIP valide."
            )

        try:
            with zipfile.ZipFile(backup_path, mode="r") as archive:
                corrupted_member = archive.testzip()

                if corrupted_member:
                    raise InvalidBackupError(
                        f"L’archive est endommagée : {corrupted_member}"
                    )

                archive_names = set(archive.namelist())

                if BackupService.MANIFEST_NAME not in archive_names:
                    raise InvalidBackupError(
                        "Le manifeste de sauvegarde est absent."
                    )

                if BackupService.DATABASE_ARCHIVE_PATH not in archive_names:
                    raise InvalidBackupError(
                        "La base PaperNest est absente."
                    )

                manifest = json.loads(
                    archive.read(BackupService.MANIFEST_NAME).decode("utf-8")
                )

                BackupService._validate_manifest(manifest)

                with tempfile.TemporaryDirectory(prefix="papernest_verify_") as temporary_directory:
                    database_path = Path(temporary_directory) / "papernest.db"

                    with archive.open(BackupService.DATABASE_ARCHIVE_PATH) as source:
                        with database_path.open("wb") as destination:
                            shutil.copyfileobj(source, destination)

                    backup_repository.verify_database(database_path)

                    expected_database_hash = str(manifest["database_sha256"])
                    actual_database_hash = BackupService._compute_sha256(database_path)

                    if actual_database_hash != expected_database_hash:
                        raise InvalidBackupError(
                            "La base de données sauvegardée est endommagée."
                        )

                for document in manifest["documents"]:
                    relative_path = str(document["relative_path"])
                    archive_name = f"{BackupService.DOCUMENTS_ARCHIVE_ROOT}/{relative_path}"

                    if archive_name not in archive_names:
                        raise InvalidBackupError(
                            f"Un document manque : {relative_path}"
                        )

                    actual_hash = BackupService._compute_zip_member_sha256(
                        archive,
                        archive_name,
                    )

                    if actual_hash != str(document["sha256"]):
                        raise InvalidBackupError(
                            f"Un document est endommagé : {relative_path}"
                        )

            return manifest

        except InvalidBackupError:
            raise

        except (zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise InvalidBackupError(
                "La sauvegarde est illisible ou endommagée."
            ) from error

    @staticmethod
    def restore_backup(backup_file: str | Path) -> dict[str, Any]:
        backup_path = Path(backup_file).expanduser()
        manifest = BackupService.verify_backup(backup_path)

        safety_backup = BackupService.create_backup(
            BACKUP_ROOT,
            safety_backup=True,
        )

        with tempfile.TemporaryDirectory(prefix="papernest_restore_") as temporary_directory:
            temporary_root = Path(temporary_directory)
            extracted_root = temporary_root / "extracted"
            rollback_storage = temporary_root / "rollback_archives"
            rollback_database = temporary_root / "rollback.db"

            extracted_root.mkdir(parents=True, exist_ok=True)

            try:
                with zipfile.ZipFile(backup_path, mode="r") as archive:
                    BackupService._safe_extract_all(archive, extracted_root)

                restored_storage = extracted_root / BackupService.DOCUMENTS_ARCHIVE_ROOT
                restored_database = extracted_root / BackupService.DATABASE_ARCHIVE_PATH

                backup_repository.verify_database(restored_database)
                BackupService._verify_extracted_documents(restored_storage, manifest)

                if STORAGE_ROOT.exists():
                    shutil.copytree(STORAGE_ROOT, rollback_storage)

                if DB_PATH.exists():
                    shutil.copy2(DB_PATH, rollback_database)

                BackupService._replace_storage(restored_storage)
                backup_repository.restore_database(restored_database, DB_PATH)

                DocumentIndexService.synchronize()

            except Exception as error:
                logger.exception("Échec de la restauration.")

                BackupService._restore_storage_rollback(
                    rollback_storage
                )

                if rollback_database.exists():
                    backup_repository.restore_database(
                        rollback_database,
                        DB_PATH,
                    )

                if isinstance(error, BackupError):
                    raise

                raise BackupError(
                    "La restauration a échoué. Les anciennes données ont été restaurées."
                ) from error

        event_bus.publish(
            BackupRestored(backup_path=str(backup_path))
        )

        return {
            "backup_path": str(backup_path),
            "safety_backup_path": str(safety_backup),
            "created_at": str(manifest["created_at"]),
            "document_count": int(manifest["document_count"]),
        }

    @staticmethod
    def list_local_backups() -> list[dict[str, Any]]:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        backups: list[dict[str, Any]] = []

        for backup_path in sorted(
            BACKUP_ROOT.glob("*.zip"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        ):
            stat = backup_path.stat()

            backups.append(
                {
                    "path": str(backup_path),
                    "name": backup_path.name,
                    "size_bytes": stat.st_size,
                    "size": BackupService.format_size(stat.st_size),
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime
                    ).astimezone().strftime("%d/%m/%Y à %H:%M"),
                }
            )

        return backups

    @staticmethod
    def format_size(size_bytes: int) -> str:
        size = float(size_bytes)
        units = ("o", "Ko", "Mo", "Go", "To")

        for unit in units:
            if size < 1024 or unit == units[-1]:
                return f"{int(size)} {unit}" if unit == "o" else f"{size:.1f} {unit}"

            size /= 1024

        return f"{size_bytes} o"

    @staticmethod
    def _build_manifest(database_path: Path) -> dict[str, Any]:
        documents = []

        for document_path in sorted(STORAGE_ROOT.rglob("*")):
            if not document_path.is_file() or document_path.name.endswith(".part"):
                continue

            relative_path = document_path.relative_to(STORAGE_ROOT).as_posix()
            stat = document_path.stat()

            documents.append(
                {
                    "relative_path": relative_path,
                    "size_bytes": stat.st_size,
                    "sha256": BackupService._compute_sha256(document_path),
                }
            )

        return {
            "application": APP_NAME,
            "format_version": BackupService.FORMAT_VERSION,
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "database_sha256": BackupService._compute_sha256(database_path),
            "document_count": len(documents),
            "documents": documents,
        }

    @staticmethod
    def _validate_manifest(manifest: Any) -> None:
        if not isinstance(manifest, dict):
            raise InvalidBackupError(
                "Le manifeste est invalide."
            )

        if manifest.get("application") != APP_NAME:
            raise InvalidBackupError(
                "Cette archive n’appartient pas à PaperNest."
            )

        if manifest.get("format_version") != BackupService.FORMAT_VERSION:
            raise InvalidBackupError(
                "Cette version de sauvegarde n’est pas prise en charge."
            )

        documents = manifest.get("documents")

        if not isinstance(documents, list):
            raise InvalidBackupError(
                "La liste des documents est invalide."
            )

        if int(manifest.get("document_count", -1)) != len(documents):
            raise InvalidBackupError(
                "Le nombre de documents est incohérent."
            )

        if not isinstance(manifest.get("database_sha256"), str):
            raise InvalidBackupError(
                "L’empreinte de la base est absente."
            )

        for document in documents:
            relative_path = str(document.get("relative_path", ""))
            sha256 = str(document.get("sha256", ""))

            BackupService._validate_relative_path(relative_path)

            if len(sha256) != 64:
                raise InvalidBackupError(
                    "Une empreinte de document est invalide."
                )

    @staticmethod
    def _verify_extracted_documents(storage_root: Path, manifest: dict[str, Any]) -> None:
        for document in manifest["documents"]:
            relative_path = str(document["relative_path"])
            document_path = storage_root / relative_path

            if not document_path.exists() or not document_path.is_file():
                raise InvalidBackupError(
                    f"Un document restauré est absent : {relative_path}"
                )

            if document_path.stat().st_size != int(document["size_bytes"]):
                raise InvalidBackupError(
                    f"La taille d’un document est incorrecte : {relative_path}"
                )

            if BackupService._compute_sha256(document_path) != str(document["sha256"]):
                raise InvalidBackupError(
                    f"Un document restauré est endommagé : {relative_path}"
                )

    @staticmethod
    def _replace_storage(restored_storage: Path) -> None:
        new_storage = STORAGE_ROOT.with_name(
            f"{STORAGE_ROOT.name}.restoring"
        )

        old_storage = STORAGE_ROOT.with_name(
            f"{STORAGE_ROOT.name}.previous"
        )

        shutil.rmtree(new_storage, ignore_errors=True)
        shutil.rmtree(old_storage, ignore_errors=True)

        shutil.copytree(restored_storage, new_storage)

        if STORAGE_ROOT.exists():
            STORAGE_ROOT.rename(old_storage)

        try:
            new_storage.rename(STORAGE_ROOT)

        except Exception:
            shutil.rmtree(STORAGE_ROOT, ignore_errors=True)

            if old_storage.exists():
                old_storage.rename(STORAGE_ROOT)

            raise

        shutil.rmtree(old_storage, ignore_errors=True)

    @staticmethod
    def _restore_storage_rollback(rollback_storage: Path) -> None:
        if not rollback_storage.exists():
            return

        shutil.rmtree(STORAGE_ROOT, ignore_errors=True)
        shutil.copytree(rollback_storage, STORAGE_ROOT)

    @staticmethod
    def _safe_extract_all(archive: zipfile.ZipFile, destination: Path) -> None:
        destination_root = destination.resolve()

        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()

            try:
                member_path.relative_to(destination_root)

            except ValueError as error:
                raise InvalidBackupError(
                    "L’archive contient un chemin dangereux."
                ) from error

        archive.extractall(destination)

    @staticmethod
    def _validate_relative_path(relative_path: str) -> None:
        path = Path(relative_path)

        if not relative_path or path.is_absolute() or ".." in path.parts:
            raise InvalidBackupError(
                "Le manifeste contient un chemin dangereux."
            )

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        digest = hashlib.sha256()

        with file_path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _compute_zip_member_sha256(archive: zipfile.ZipFile, member_name: str) -> str:
        digest = hashlib.sha256()

        with archive.open(member_name, mode="r") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

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