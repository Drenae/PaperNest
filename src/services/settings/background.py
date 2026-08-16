from __future__ import annotations

import json
import logging
import re
import shutil
import uuid
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageOps, UnidentifiedImageError

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
                alignment_x=current.alignment_x,
                alignment_y=current.alignment_y,
            )
        )

    def import_image(
        self,
        source: str | Path,
        *,
        alignment_x: float = 0.0,
        alignment_y: float = 0.0,
        zoom: float = 1.0,
        target_aspect_ratio: float = 16 / 9,
    ) -> BackgroundSettings:
        source_path = Path(source).expanduser()
        self._validate_image(source_path)
        self.background_root.mkdir(parents=True, exist_ok=True)
        destination = self.background_root / (
            f"custom_background_{uuid.uuid4().hex[:12]}{source_path.suffix.casefold()}"
        )
        temporary = destination.with_name(f".{destination.name}.part")
        temporary.unlink(missing_ok=True)
        normalized_zoom = self._normalize_zoom(zoom)
        if normalized_zoom != 1.0:
            cropped = self.load_preview_image(source_path, max_size=None)
            cropped = self._crop_image(
                cropped,
                alignment_x=alignment_x,
                alignment_y=alignment_y,
                zoom=normalized_zoom,
                target_aspect_ratio=target_aspect_ratio,
            )
            self._save_image(cropped, temporary, source_path.suffix.casefold())
            alignment_x = 0.0
            alignment_y = 0.0
        else:
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
                alignment_x=self._normalize_alignment(alignment_x),
                alignment_y=self._normalize_alignment(alignment_y),
            )
        )

    def load_preview_image(
        self,
        source: str | Path,
        *,
        max_size: int | None = 1600,
    ) -> Image.Image:
        with Image.open(Path(source)) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        if max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return image

    def render_crop_preview(
        self,
        image: Image.Image,
        *,
        alignment_x: float,
        alignment_y: float,
        zoom: float,
        target_aspect_ratio: float,
    ) -> bytes:
        cropped = self._crop_image(
            image,
            alignment_x=alignment_x,
            alignment_y=alignment_y,
            zoom=zoom,
            target_aspect_ratio=target_aspect_ratio,
        )
        cropped.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        output = BytesIO()
        cropped.save(output, format="JPEG", quality=88, optimize=True)
        return output.getvalue()

    def _crop_image(
        self,
        image: Image.Image,
        *,
        alignment_x: float,
        alignment_y: float,
        zoom: float,
        target_aspect_ratio: float,
    ) -> Image.Image:
        width, height = image.size
        ratio = max(0.2, min(5.0, float(target_aspect_ratio or 16 / 9)))
        image_ratio = width / height
        if image_ratio > ratio:
            base_height = float(height)
            base_width = base_height * ratio
        else:
            base_width = float(width)
            base_height = base_width / ratio
        normalized_zoom = self._normalize_zoom(zoom)
        crop_width = max(1.0, base_width / normalized_zoom)
        crop_height = max(1.0, base_height / normalized_zoom)
        x = (self._normalize_alignment(alignment_x) + 1.0) / 2.0
        y = (self._normalize_alignment(alignment_y) + 1.0) / 2.0
        left = (width - crop_width) * x
        top = (height - crop_height) * y
        if normalized_zoom >= 1.0:
            return image.crop((left, top, left + crop_width, top + crop_height))
        extended = self._crop_with_edge_extension(
            image,
            left=left,
            top=top,
            width=crop_width,
            height=crop_height,
        )
        extended.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
        return extended

    @staticmethod
    def _crop_with_edge_extension(
        image: Image.Image,
        *,
        left: float,
        top: float,
        width: float,
        height: float,
    ) -> Image.Image:
        crop_left = round(left)
        crop_top = round(top)
        target_width = max(1, round(width))
        target_height = max(1, round(height))
        crop_right = crop_left + target_width
        crop_bottom = crop_top + target_height

        source_left = max(0, crop_left)
        source_top = max(0, crop_top)
        source_right = min(image.width, crop_right)
        source_bottom = min(image.height, crop_bottom)
        source = image.crop((source_left, source_top, source_right, source_bottom))
        destination_left = source_left - crop_left
        destination_top = source_top - crop_top

        canvas = Image.new(image.mode, (target_width, target_height))
        canvas.paste(source, (destination_left, destination_top))
        destination_right = destination_left + source.width
        destination_bottom = destination_top + source.height

        if destination_left > 0:
            left_edge = source.crop((0, 0, 1, source.height)).resize(
                (destination_left, source.height)
            )
            canvas.paste(left_edge, (0, destination_top))
        if destination_right < target_width:
            right_width = target_width - destination_right
            right_edge = source.crop(
                (source.width - 1, 0, source.width, source.height)
            ).resize((right_width, source.height))
            canvas.paste(right_edge, (destination_right, destination_top))
        if destination_top > 0:
            top_edge = canvas.crop((0, destination_top, target_width, destination_top + 1))
            canvas.paste(top_edge.resize((target_width, destination_top)), (0, 0))
        if destination_bottom < target_height:
            bottom_height = target_height - destination_bottom
            bottom_edge = canvas.crop(
                (0, destination_bottom - 1, target_width, destination_bottom)
            )
            canvas.paste(
                bottom_edge.resize((target_width, bottom_height)),
                (0, destination_bottom),
            )
        return canvas

    @staticmethod
    def _save_image(image: Image.Image, path: Path, suffix: str) -> None:
        image_format = {
            ".png": "PNG",
            ".webp": "WEBP",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
        }.get(suffix, "JPEG")
        if image_format == "JPEG" and image.mode != "RGB":
            image = image.convert("RGB")
        image.save(path, format=image_format, quality=94)

    def use_image(self) -> BackgroundSettings:
        current = self.load()
        return self.save(
            BackgroundSettings(
                mode=BackgroundMode.IMAGE,
                color=current.color,
                image_path=current.image_path,
                alignment_x=current.alignment_x,
                alignment_y=current.alignment_y,
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

        page.bgcolor = ft.Colors.TRANSPARENT
        page.decoration = ft.BoxDecoration(
            image=ft.DecorationImage(
                src=self.resolve_image_source(resolved.image_path),
                fit=ft.BoxFit.COVER,
                alignment=ft.Alignment(
                    resolved.alignment_x,
                    resolved.alignment_y,
                ),
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
            alignment_x=self._normalize_alignment(settings.alignment_x),
            alignment_y=self._normalize_alignment(settings.alignment_y),
        )

    @staticmethod
    def _normalize_color(color: str) -> str:
        normalized = str(color or "").strip().upper()
        if not _HEX_COLOR_PATTERN.fullmatch(normalized):
            return DEFAULT_BACKGROUND_COLOR
        return normalized

    @staticmethod
    def _normalize_alignment(value: float) -> float:
        try:
            return max(-1.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _normalize_zoom(value: float) -> float:
        try:
            return max(0.5, min(4.0, float(value)))
        except (TypeError, ValueError):
            return 1.0

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
