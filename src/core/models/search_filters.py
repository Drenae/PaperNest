from dataclasses import asdict, dataclass
from datetime import date, timedelta
import re
from typing import Any

from utils.text import normalize_search_text


@dataclass(frozen=True, slots=True)
class SearchFilters:
    category_key: str | None = None
    file_type: str | None = None
    favorites_only: bool = False
    imported_period: str | None = None
    person_query: str | None = None
    tag_query: str | None = None
    sort_order: str = "relevance"
    limit: int = 200

    def imported_after(self) -> str | None:
        days_by_period = {"7_days": 7, "30_days": 30, "90_days": 90, "1_year": 365}
        days = days_by_period.get(self.imported_period or "")
        return None if days is None else (date.today() - timedelta(days=days)).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchFilters":
        allowed = {field.name for field in __import__("dataclasses").fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in allowed})


def build_fts_query(value: str) -> str:
    normalized = normalize_search_text(value)
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return " AND ".join(f'"{token}"*' for token in tokens[:12]) if tokens else ""
