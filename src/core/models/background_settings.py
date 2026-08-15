from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

DEFAULT_BACKGROUND_COLOR = "#F4F2ED"


class BackgroundMode(str, Enum):
    IMAGE = "image"
    COLOR = "color"


@dataclass(frozen=True, slots=True)
class BackgroundSettings:
    mode: BackgroundMode = BackgroundMode.IMAGE
    color: str = DEFAULT_BACKGROUND_COLOR
    image_path: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BackgroundSettings":
        try:
            mode = BackgroundMode(str(payload.get("mode", BackgroundMode.IMAGE.value)))
        except ValueError:
            mode = BackgroundMode.IMAGE
        color = str(payload.get("color") or DEFAULT_BACKGROUND_COLOR).upper()
        image_path = payload.get("image_path")
        return cls(
            mode=mode,
            color=color,
            image_path=str(image_path) if image_path else None,
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "mode": self.mode.value,
            "color": self.color,
            "image_path": self.image_path,
        }
