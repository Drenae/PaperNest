from __future__ import annotations

import json
import logging
from pathlib import Path

from core.config.settings import TRASH_SETTINGS_PATH
from core.models.trash_settings import (
    MAX_TRASH_RETENTION_DAYS,
    MIN_TRASH_RETENTION_DAYS,
    TrashSettings,
)


logger = logging.getLogger(__name__)


class TrashSettingsService:
    def __init__(self, settings_path: Path = TRASH_SETTINGS_PATH) -> None:
        self.settings_path = settings_path

    def load(self) -> TrashSettings:
        if not self.settings_path.exists():
            return TrashSettings()
        try:
            payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError
            return TrashSettings.from_dict(payload)
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            logger.warning(
                "Configuration de corbeille invalide, durée par défaut utilisée."
            )
            return TrashSettings()

    def get_retention_days(self) -> int:
        return self.load().retention_days

    def save_retention_days(self, value: int | str) -> TrashSettings:
        try:
            retention_days = int(str(value).strip())
        except (TypeError, ValueError) as error:
            raise ValueError("Saisissez un nombre entier de jours.") from error
        if not MIN_TRASH_RETENTION_DAYS <= retention_days <= MAX_TRASH_RETENTION_DAYS:
            raise ValueError(
                f"La durée doit être comprise entre {MIN_TRASH_RETENTION_DAYS} "
                f"et {MAX_TRASH_RETENTION_DAYS} jours."
            )
        settings = TrashSettings(retention_days=retention_days)
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.settings_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.settings_path)
        return settings


trash_settings_service = TrashSettingsService()
