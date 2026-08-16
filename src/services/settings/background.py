from __future__ import annotations

import json
import logging
import re
import shutil
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, UnidentifiedImageError

from core.config.settings import APPEARANCE_SETTINGS_PATH, BACKGROUND_ROOT
from core.models.background_settings import (
    DEFAULT_BACKGROUND_COLOR,
    BackgroundMode,
    BackgroundSettings,
)

if TYPE_CHECKING:
    import flet as ft


logger = logging.getLogger(__name__)

DEFAULT_BACKGROUND_ASSET = "backgrounds/papernest_default.jpg"
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_BACKGROUND_SIZE_BYTES = 50 * 1024 * 1024
_HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-F]{6}$")


class BackgroundService:
    def __init__(
        self,
        *,
        settings_path: Path = APPEARANCE_SETTINGS_PATH,
        background_root: Path = BACKGROUND_ROOT,
        default_asset: str = DEFAULT_BACKGROUND_ASSET,
    ) -> None:
        self.settings_path = settings_path
        self.background_root = background_root
        self.default_asset = default_asset

    def load(self) -> BackgroundSettings:
        if not self.settings_path.exists():
            return BackgroundSettings()
        try:
            payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("La configuration d’apparence doit être un objet JSON.")
            settings = BackgroundSettings.from_dict(payload)
            return self._normalize(settings)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            logger.warning("Configuration d’apparence invalide, fond par défaut utilisé.")
            return BackgroundSettings()

    def save(self, settings: BackgroundSettings) -> BackgroundSettings:
        normalized = self._normalize(settings)
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.settings_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(normalized.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.settings_path)
        return normalized

    def use_color(self, color: str) -> BackgroundSettings:
        normalized_color = self._normalize_color(color)
        current = self.load()
        return self.save(
            BackgroundSettings(
                mode=BackgroundMode.COLOR,
                color=normalized_color,
                image_path=current.image_path,
            )
        )

    def import_image(self, source: str | Path) -> BackgroundSettings:
        source_path = Path(source).expanduser()
        self._validate_image(source_path)
        self.background_root.mkdir(parents=True, exist_ok=True)
        destination = self.background_root / (
            f"custom_background_{uuid.uuid4().hex[:12]}{source_path.suffix.casefold()}"
        )
        temporary = destination.with_name(f".{destination.name}.part")
        temporary.unlink(missing_ok=True)
        shutil.copy2(source_path, temporary)
        self._validate_image(temporary, check_extension=False)
        temporary.replace(destination)
        self._remove_previous_images(keep=destination)
        current = self.load()
        return self.save(
            BackgroundSettings(
                mode=BackgroundMode.IMAGE,
                color=current.color,
                image_path=str(destination),
            )
        )

    def use_image(self) -> BackgroundSettings:
        current = self.load()
        return self.save(
            BackgroundSettings(
                mode=BackgroundMode.IMAGE,
                color=current.color,
                image_path=current.image_path,
            )
        )

    def reset(self) -> BackgroundSettings:
        self._remove_previous_images()
        return self.save(BackgroundSettings())

    def apply(self, page: "ft.Page", settings: BackgroundSettings | None = None) -> None:
        import flet as ft

        resolved = self._normalize(settings or self.load())
        if resolved.mode is BackgroundMode.COLOR:
            page.decoration = None
            page.bgcolor = resolved.color
            return

        page.bgcolor = resolved.color
        page.decoration = ft.BoxDecoration(
            image=ft.DecorationImage(
                src=self.resolve_image_source(resolved.image_path),
                fit=ft.BoxFit.CONTAIN,
                alignment=ft.Alignment.CENTER,
            )
        )

    def resolve_image_source(self, image_path: str | None) -> str | bytes:
        if not image_path:
            return self.default_asset
        try:
            return Path(image_path).read_bytes()
        except OSError:
            logger.warning(
                "Image de fond impossible à lire, fond PaperNest utilisé."
            )
            return self.default_asset

    def _normalize(self, settings: BackgroundSettings) -> BackgroundSettings:
        color = self._normalize_color(settings.color)
        image_path = settings.image_path
        if image_path:
            try:
                self._validate_image(Path(image_path), check_extension=False)
            except ValueError:
                logger.warning(
                    "Image de fond absente ou invalide, fond PaperNest utilisé."
                )
                image_path = None
        return BackgroundSettings(
            mode=settings.mode,
            color=color,
            image_path=image_path,
        )

    @staticmethod
    def _normalize_color(color: str) -> str:
        normalized = str(color or "").strip().upper()
        if not _HEX_COLOR_PATTERN.fullmatch(normalized):
            return DEFAULT_BACKGROUND_COLOR
        return normalized

    @staticmethod
    def _validate_image(path: Path, *, check_extension: bool = True) -> None:
        if not path.exists() or not path.is_file():
            raise ValueError("L’image sélectionnée n’existe plus.")
        if check_extension and path.suffix.casefold() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise ValueError("Formats acceptés : PNG, JPG, JPEG et WebP.")
        if path.stat().st_size > MAX_BACKGROUND_SIZE_BYTES:
            raise ValueError("L’image dépasse la taille maximale de 50 Mo.")
        try:
            with Image.open(path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as error:
            raise ValueError("Le fichier sélectionné n’est pas une image valide.") from error

    def _remove_previous_images(self, *, keep: Path | None = None) -> None:
        if not self.background_root.exists():
            return
        for path in self.background_root.glob("custom_background*.*"):
            if keep is None or path != keep:
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    logger.warning("Ancienne image de fond impossible à supprimer : %s", path)


background_service = BackgroundService()
