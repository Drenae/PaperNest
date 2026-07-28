from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PreviewState:
    file_path: Path | None = None
    title: str = ""
    extension: str = ""
    category_name: str = ""
    file_size: str = ""
