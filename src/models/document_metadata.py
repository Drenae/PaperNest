from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DocumentDetails:
    document_id: int
    is_favorite: bool = False
    tags: tuple[str, ...] = ()
    document_date: date | None = None
    due_date: date | None = None
    amount: Decimal | None = None
    person_name: str = ""
    notes: str = ""