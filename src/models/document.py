from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    # Affichage
    name: str
    absolute_path: str
    category: str
    file_size: str
    match_reason: str

    # Identifiants
    document_id: int | None = None
    category_key: str | None = None

    # Stockage
    relative_path: str | None = None
    extension: str | None = None
    size_bytes: int = 0
    sha256: str | None = None
    imported_at: str | None = None

    # Métadonnées
    is_favorite: bool = False

    document_date: str | None = None
    due_date: str | None = None

    amount: str | None = None

    person_name: str = ""

    notes: str = ""

    tags: tuple[str, ...] = ()

    @property
    def path(self) -> Path:
        return Path(self.absolute_path)

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def stem(self) -> str:
        return self.path.stem

    @property
    def suffix(self) -> str:
        return self.path.suffix

    @property
    def has_metadata(self) -> bool:
        return any(
            (
                self.tags,
                self.person_name,
                self.notes,
                self.document_date,
                self.due_date,
                self.amount,
            )
        )

    @property
    def has_due_date(self) -> bool:
        return self.due_date is not None

    @property
    def has_amount(self) -> bool:
        return self.amount is not None

    @property
    def is_pdf(self) -> bool:
        return self.extension == ".pdf"

    @property
    def is_image(self) -> bool:
        return self.extension in (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".bmp",
        )