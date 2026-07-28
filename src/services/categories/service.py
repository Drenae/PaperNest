import logging
import re
import shutil
import unicodedata
from pathlib import Path

from core.config.constants import STORAGE_ROOT, TRASH_ROOT, UNSORTED_ROOT
from core.events.event_bus import (
    CategoryCreated,
    CategoryDeleted,
    CategoryRenamed,
    event_bus,
)
from core.errors.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    InvalidCategoryNameError,
    StorageError,
)
from repositories.category_repository import category_repository


logger = logging.getLogger(__name__)


class CategoryService:
    def list_categories(self) -> list[dict]:
        return category_repository.list_all()

    def get_category(self, category_key: str) -> dict:
        category = category_repository.get(category_key)

        if category is None:
            raise CategoryNotFoundError(
                f"Le classeur « {category_key} » n’existe pas."
            )

        return category

    def create_category(
        self,
        name: str,
        icon: str,
        color: str,
        background: str,
    ) -> dict:
        clean_name = self._clean_display_name(name)
        category_key = self._build_next_category_key(clean_name)
        category_path = STORAGE_ROOT / category_key

        if category_path.exists():
            raise CategoryAlreadyExistsError(
                f"Le classeur « {clean_name} » existe déjà."
            )

        category_path.mkdir(parents=True, exist_ok=False)

        try:
            category = category_repository.create(
                category_key=category_key,
                name=clean_name,
                icon=icon,
                color=color,
                background=background,
            )

        except Exception:
            shutil.rmtree(category_path, ignore_errors=True)
            raise

        event_bus.publish(
            CategoryCreated(category_key=category_key)
        )

        logger.info(
            "Catégorie créée : %s.",
            category_key,
        )

        return category

    def rename_category(self, category_key: str, new_name: str) -> dict:
        category = self.get_category(category_key)
        clean_name = self._clean_display_name(new_name)
        parent_key = category.get("parent_key")

        if parent_key:
            new_key = f"{parent_key}/{self._sanitize_folder_name(clean_name)}"
        else:
            prefix = category_key.partition("_")[0]
            new_key = f"{prefix}_{self._sanitize_folder_name(clean_name)}"

        if new_key != category_key and category_repository.exists(new_key):
            raise CategoryAlreadyExistsError(
                f"Le classeur « {clean_name} » existe déjà."
            )

        old_path = STORAGE_ROOT / category_key
        new_path = STORAGE_ROOT / new_key

        if new_key != category_key:
            if new_path.exists():
                raise CategoryAlreadyExistsError(
                    f"Le dossier « {new_path.name} » existe déjà."
                )
            new_path.parent.mkdir(parents=True, exist_ok=True)
            if old_path.exists():
                old_path.rename(new_path)
            else:
                new_path.mkdir(parents=True, exist_ok=False)

        try:
            updated_category = category_repository.update(
                category_key,
                new_key=new_key,
                name=clean_name,
                icon=str(category["icon"]),
                color=str(category["color"]),
                background=str(category["bg"]),
            )
        except Exception:
            if new_key != category_key and new_path.exists() and not old_path.exists():
                old_path.parent.mkdir(parents=True, exist_ok=True)
                new_path.rename(old_path)
            raise

        event_bus.publish(
            CategoryRenamed(
                old_category_key=category_key,
                new_category_key=new_key,
            )
        )
        return updated_category

    def create_subcategory(
        self,
        parent_key: str,
        name: str,
        icon: str,
        color: str,
        background: str,
    ) -> dict:
        parent = self.get_category(parent_key)
        if parent.get("parent_key"):
            raise InvalidCategoryNameError(
                "Une sous-catégorie ne peut pas contenir d’autre niveau."
            )
        clean_name = self._clean_display_name(name)
        category_key = f"{parent_key}/{self._sanitize_folder_name(clean_name)}"
        category_path = STORAGE_ROOT / category_key
        if category_repository.exists(category_key) or category_path.exists():
            raise CategoryAlreadyExistsError(
                f"La sous-catégorie « {clean_name} » existe déjà."
            )
        category_path.mkdir(parents=True, exist_ok=False)
        try:
            category = category_repository.create(
                category_key=category_key,
                name=clean_name,
                icon=icon,
                color=color,
                background=background,
                parent_key=parent_key,
            )
        except Exception:
            shutil.rmtree(category_path, ignore_errors=True)
            raise
        event_bus.publish(CategoryCreated(category_key=category_key))
        return category

    def update_appearance(
        self,
        category_key: str,
        *,
        name: str,
        icon: str,
        color: str,
        background: str,
    ) -> dict:
        category = self.get_category(category_key)

        return category_repository.update(
            category_key,
            new_key=category_key,
            name=self._clean_display_name(name),
            icon=icon or str(category["icon"]),
            color=color or str(category["color"]),
            background=background or str(category["bg"]),
        )

    def delete_empty_category(self, category_key: str) -> None:
        category = self.get_category(category_key)

        if int(category.get("document_count", 0)) > 0:
            raise StorageError(
                "Le classeur contient encore des documents."
            )

        category_path = STORAGE_ROOT / category_key

        if category_path.exists():
            if any(category_path.iterdir()):
                raise StorageError(
                    "Le dossier du classeur n’est pas vide."
                )

            category_path.rmdir()

        try:
            category_repository.delete(category_key)

        except Exception:
            category_path.mkdir(parents=True, exist_ok=True)
            raise

        self._publish_deleted(category_key)

    def delete_and_trash_documents(self, category_key: str) -> Path | None:
        self.get_category(category_key)

        category_path = STORAGE_ROOT / category_key
        trash_destination: Path | None = None

        if category_path.exists():
            TRASH_ROOT.mkdir(parents=True, exist_ok=True)

            trash_destination = self._build_unique_path(
                TRASH_ROOT / f"classeur_{category_path.name}"
            )

            shutil.move(
                str(category_path),
                str(trash_destination),
            )

        try:
            category_repository.delete(category_key)

        except Exception:
            if (
                trash_destination is not None
                and trash_destination.exists()
                and not category_path.exists()
            ):
                shutil.move(
                    str(trash_destination),
                    str(category_path),
                )

            raise

        self._publish_deleted(category_key)

        return trash_destination

    def delete_and_move_documents(self, category_key: str) -> int:
        self.get_category(category_key)

        category_path = STORAGE_ROOT / category_key
        moved_files: list[tuple[Path, Path]] = []

        UNSORTED_ROOT.mkdir(parents=True, exist_ok=True)

        try:
            if category_path.exists():
                for source_path in category_path.iterdir():
                    destination_path = self._build_unique_path(
                        UNSORTED_ROOT / source_path.name
                    )

                    shutil.move(
                        str(source_path),
                        str(destination_path),
                    )

                    moved_files.append(
                        (
                            source_path,
                            destination_path,
                        )
                    )

                category_path.rmdir()

            category_repository.delete(category_key)

        except Exception:
            category_path.mkdir(parents=True, exist_ok=True)

            for source_path, destination_path in reversed(moved_files):
                if destination_path.exists():
                    shutil.move(
                        str(destination_path),
                        str(source_path),
                    )

            raise

        self._publish_deleted(category_key)

        return len(moved_files)

    def count_categories(self) -> int:
        return category_repository.count()

    def _build_next_category_key(self, name: str) -> str:
        categories = category_repository.list_all()
        highest_prefix = 0

        for category in categories:
            raw_prefix = str(category["key"]).partition("_")[0]

            try:
                highest_prefix = max(
                    highest_prefix,
                    int(raw_prefix),
                )

            except ValueError:
                continue

        folder_name = self._sanitize_folder_name(name)

        return f"{highest_prefix + 1:02d}_{folder_name}"

    @staticmethod
    def _clean_display_name(name: str) -> str:
        clean_name = " ".join(
            unicodedata.normalize("NFKC", name).strip().split()
        )

        if not clean_name:
            raise InvalidCategoryNameError(
                "Le nom du classeur est vide."
            )

        if len(clean_name) > 80:
            raise InvalidCategoryNameError(
                "Le nom du classeur ne peut pas dépasser 80 caractères."
            )

        return clean_name

    @staticmethod
    def _sanitize_folder_name(name: str) -> str:
        clean_name = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            "_",
            name,
        )

        clean_name = re.sub(
            r"\s+",
            "_",
            clean_name,
        )

        clean_name = re.sub(
            r"_+",
            "_",
            clean_name,
        )

        clean_name = clean_name.strip(" ._")

        if not clean_name:
            raise InvalidCategoryNameError(
                "Le nom du dossier est invalide."
            )

        return clean_name[:100]

    @staticmethod
    def _build_unique_path(desired_path: Path) -> Path:
        if not desired_path.exists():
            return desired_path

        counter = 2

        while True:
            candidate = desired_path.with_name(
                f"{desired_path.name}_{counter}"
            )

            if not candidate.exists():
                return candidate

            counter += 1

    @staticmethod
    def _publish_deleted(category_key: str) -> None:
        event_bus.publish(
            CategoryDeleted(category_key=category_key)
        )

        logger.info(
            "Catégorie supprimée : %s.",
            category_key,
        )


category_service = CategoryService()