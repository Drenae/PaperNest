from pathlib import Path

from app.preview.state import PreviewState


class PreviewController:
    def __init__(self):
        self._state = PreviewState()

    @property
    def state(self) -> PreviewState:
        return self._state

    def clear(self) -> None:
        self._state = PreviewState()

    def select_file(
        self,
        path: str,
        title: str,
        *,
        category_name: str = "",
        file_size: str = "",
    ) -> None:
        file_path = Path(path)

        self._state = PreviewState(
            file_path=file_path,
            title=title,
            extension=file_path.suffix.casefold(),
            category_name=category_name,
            file_size=file_size,
        )
