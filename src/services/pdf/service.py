import logging
from pathlib import Path

from pypdf import PdfReader

from core.errors.exceptions import PdfExtractionError


logger = logging.getLogger(__name__)


class PdfExtractionService:
    @staticmethod
    def extract_text(pdf_path: Path) -> str:
        """
        Extrait le texte d'un PDF contenant déjà une couche texte.

        Cette méthode ne fait pas encore d'OCR.
        Un PDF provenant d'un scanner peut donc ne retourner aucun texte.
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PdfExtractionError(
                f"Le fichier PDF est introuvable : {pdf_path}"
            )

        extracted_pages: list[str] = []

        try:
            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    page_content = page.extract_text()

                    if page_content:
                        extracted_pages.append(page_content)

                except Exception:
                    logger.warning(
                        "Impossible d'extraire la page %s du PDF %s.",
                        page_number,
                        pdf_path,
                        exc_info=True,
                    )

        except Exception as error:
            logger.exception(
                "Échec de lecture du PDF %s.",
                pdf_path,
            )

            raise PdfExtractionError(
                f"Impossible de lire le PDF « {pdf_path.name} »."
            ) from error

        return "\n".join(extracted_pages).strip()

    @staticmethod
    def extract_lowercase_text(pdf_path: Path) -> str:
        """
        Méthode conservée pour rester compatible avec l'ancien code.
        """
        try:
            return PdfExtractionService.extract_text(pdf_path).casefold()
        except PdfExtractionError:
            return ""