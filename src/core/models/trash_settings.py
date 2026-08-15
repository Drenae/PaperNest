from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_TRASH_RETENTION_DAYS = 30
MIN_TRASH_RETENTION_DAYS = 1
MAX_TRASH_RETENTION_DAYS = 3650


@dataclass(frozen=True, slots=True)
class TrashSettings:
    retention_days: int = DEFAULT_TRASH_RETENTION_DAYS

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TrashSettings":
        try:
            retention_days = int(payload.get("retention_days"))
        except (TypeError, ValueError):
            retention_days = DEFAULT_TRASH_RETENTION_DAYS
        if not MIN_TRASH_RETENTION_DAYS <= retention_days <= MAX_TRASH_RETENTION_DAYS:
            retention_days = DEFAULT_TRASH_RETENTION_DAYS
        return cls(retention_days=retention_days)

    def to_dict(self) -> dict[str, int]:
        return {"retention_days": self.retention_days}
