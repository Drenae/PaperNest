import base64
import logging
from pathlib import Path

import pymupdf

from core.errors.exceptions import PaperNestError


logger = logging.getLogger(__name__)


class PdfPreviewError(PaperNestError):
    pass


class PdfPreviewService:
    MIN_ZOOM = 0.5
    MAX_ZOOM = 3.0

    @staticmethod
    def get_page_count(file_path: str | Path) -> int:
        path = PdfPreviewService.validate_path(file_path)

        try:
            with pymupdf.open(path) as document:
                if document.needs_pass:
                    raise PdfPreviewError(
                        "Ce PDF est protégé par un mot de passe."
                    )

                return document.page_count

        except PdfPreviewError:
            raise

        except Exception as error:
            logger.exception(
                "Impossible de lire le PDF %s.",
                path,
            )

            raise PdfPreviewError(
                "Impossible de lire ce document PDF."
            ) from error

    @staticmethod
    def render_page_base64(
        file_path: str | Path,
        page_index: int = 0,
        zoom: float = 1.35,
        rotation: int = 0,
    ) -> str:
        path = PdfPreviewService.validate_path(file_path)
        zoom = max(
            PdfPreviewService.MIN_ZOOM,
            min(float(zoom), PdfPreviewService.MAX_ZOOM),
        )

        try:
            with pymupdf.open(path) as document:
                if document.needs_pass:
                    raise PdfPreviewError(
                        "Ce PDF est protégé par un mot de passe."
                    )

                if document.page_count == 0:
                    raise PdfPreviewError(
                        "Ce PDF ne contient aucune page."
                    )

                if page_index < 0 or page_index >= document.page_count:
                    raise PdfPreviewError(
                        "La page demandée n’existe pas."
                    )

                page = document.load_page(page_index)

                matrix = pymupdf.Matrix(
                    zoom,
                    zoom,
                ).prerotate(
                    rotation % 360
                )

                pixmap = page.get_pixmap(
                    matrix=matrix,
                    alpha=False,
                    colorspace=pymupdf.csRGB,
                )

                image_bytes = pixmap.tobytes(
                    "png"
                )

                return base64.b64encode(
                    image_bytes
                ).decode(
                    "ascii"
                )

        except PdfPreviewError:
            raise

        except Exception as error:
            logger.exception(
                "Impossible de rendre la page %s du PDF %s.",
                page_index + 1,
                path,
            )

            raise PdfPreviewError(
                "Impossible de générer l’aperçu du PDF."
            ) from error

    @staticmethod
    def validate_path(file_path: str | Path) -> Path:
        path = Path(
            file_path
        ).expanduser()

        if not path.exists() or not path.is_file():
            raise PdfPreviewError(
                "Le fichier PDF est introuvable."
            )

        if path.suffix.casefold() != ".pdf":
            raise PdfPreviewError(
                "Le fichier sélectionné n’est pas un PDF."
            )

        return path


pdf_preview_service = PdfPreviewService()