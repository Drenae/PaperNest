import base64
import io
import logging
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from core.errors.exceptions import PaperNestError


logger = logging.getLogger(__name__)


class ImagePreviewError(PaperNestError):
    pass


class ImagePreviewService:
    SUPPORTED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".gif",
        ".tif",
        ".tiff",
    }

    MAX_PREVIEW_WIDTH = 2200
    MAX_PREVIEW_HEIGHT = 2200

    @classmethod
    def is_supported(cls, file_path: str | Path) -> bool:
        return Path(file_path).suffix.casefold() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def render_base64(
        cls,
        file_path: str | Path,
        rotation: int = 0,
    ) -> str:
        path = cls.validate_path(file_path)

        try:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source)
                image.seek(0)

                if rotation % 360:
                    image = image.rotate(
                        -(rotation % 360),
                        expand=True,
                    )

                image.thumbnail(
                    (
                        cls.MAX_PREVIEW_WIDTH,
                        cls.MAX_PREVIEW_HEIGHT,
                    ),
                    Image.Resampling.LANCZOS,
                )

                image = cls.prepare_image(image)

                buffer = io.BytesIO()

                image.save(
                    buffer,
                    format="PNG",
                    optimize=True,
                )

                return base64.b64encode(
                    buffer.getvalue()
                ).decode("ascii")

        except ImagePreviewError:
            raise

        except UnidentifiedImageError as error:
            raise ImagePreviewError(
                "Le fichier sélectionné n’est pas une image valide."
            ) from error

        except Exception as error:
            logger.exception(
                "Impossible de générer l’aperçu de l’image %s.",
                path,
            )

            raise ImagePreviewError(
                "Impossible de générer l’aperçu de cette image."
            ) from error

    @staticmethod
    def prepare_image(image: Image.Image) -> Image.Image:
        if image.mode in {"RGBA", "LA"}:
            background = Image.new(
                "RGB",
                image.size,
                "white",
            )

            alpha = image.getchannel("A")

            background.paste(
                image.convert("RGBA"),
                mask=alpha,
            )

            return background

        if image.mode == "P" and "transparency" in image.info:
            return ImagePreviewService.prepare_image(
                image.convert("RGBA")
            )

        return image.convert("RGB")

    @classmethod
    def validate_path(cls, file_path: str | Path) -> Path:
        path = Path(file_path).expanduser()

        if not path.exists() or not path.is_file():
            raise ImagePreviewError(
                "Le fichier image est introuvable."
            )

        if path.suffix.casefold() not in cls.SUPPORTED_EXTENSIONS:
            raise ImagePreviewError(
                "Ce format d’image n’est pas pris en charge."
            )

        return path


image_preview_service = ImagePreviewService()