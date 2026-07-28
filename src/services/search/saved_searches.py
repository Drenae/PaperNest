from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.config.constants import DATA_ROOT


class SavedSearchService:
    """Stockage local et lisible des recherches enregistrées."""

    def __init__(self, path: Path | None = None):
        self.path = path or (DATA_ROOT / "saved_searches.json")

    def list_all(self) -> list[dict[str, Any]]:
        try:
            if not self.path.exists():
                return []
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                return []
            return [item for item in payload if isinstance(item, dict) and item.get("name")]
        except (OSError, json.JSONDecodeError):
            return []

    def save(self, name: str, query: str, filters: dict[str, Any]) -> None:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Le nom de la recherche est obligatoire.")
        items = [item for item in self.list_all() if str(item.get("name", "")).casefold() != clean_name.casefold()]
        items.append({"name": clean_name, "query": query.strip(), "filters": filters})
        items.sort(key=lambda item: str(item["name"]).casefold())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    def delete(self, name: str) -> None:
        items = [item for item in self.list_all() if str(item.get("name")) != name]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


saved_search_service = SavedSearchService()
