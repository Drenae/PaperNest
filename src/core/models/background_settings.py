from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

DEFAULT_BACKGROUND_COLOR = "#F4F2ED"
DEFAULT_BACKGROUND_ALIGNMENT = 0.0


class BackgroundMode(str, Enum):
    IMAGE = "image"
    COLOR = "color"


@dataclass(frozen=True, slots=True)
class BackgroundSettings:
    mode: BackgroundMode = BackgroundMode.IMAGE
    color: str = DEFAULT_BACKGROUND_COLOR
    image_path: str | None = None
    alignment_x: float = DEFAULT_BACKGROUND_ALIGNMENT
    alignment_y: float = DEFAULT_BACKGROUND_ALIGNMENT

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
            alignment_x=cls._alignment_value(payload.get("alignment_x")),
            alignment_y=cls._alignment_value(payload.get("alignment_y")),
        )

    def to_dict(self) -> dict[str, str | float | None]:
        return {
            "mode": self.mode.value,
            "color": self.color,
            "image_path": self.image_path,
            "alignment_x": self.alignment_x,
            "alignment_y": self.alignment_y,
        }

    @staticmethod
    def _alignment_value(value: Any) -> float:
        try:
            return max(-1.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return DEFAULT_BACKGROUND_ALIGNMENT
