from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from papernestextension import PaperNestFilePickerFile

from app.dashboard.state import DashboardState, StagedFile
from app.theme.pickers import BaseFilePicker
from core.errors.exceptions import PaperNestError
from core.events.event_bus import (
    CategoryCreated,
    CategoryDeleted,
    CategoryRenamed,
    DocumentDeleted,
    DocumentImported,
    DocumentMoved,
    DocumentRestored,
)
from core.events.subscription import EventSubscription
from repositories.category_repository import category_repository
from services.documents.duplicates import duplicate_detection_service
from services.files.archive import ArchiveFileService


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ImportResult:
    imported: int = 0
    duplicates: int = 0
    errors: int = 0


class DashboardController:
    DASHBOARD_EVENTS = (
        CategoryCreated,
        CategoryRenamed,
        CategoryDeleted,
        DocumentImported,
        DocumentMoved,
        DocumentDeleted,
        DocumentRestored,
    )

    def __init__(
        self,
        state: DashboardState,
        file_picker: BaseFilePicker,
        on_state_changed: Callable[[], None] | None = None,
    ) -> None:
        self.state = state
        self.file_picker = file_picker
        self.on_state_changed = on_state_changed
        self.subscriptions = EventSubscription()

    def subscribe(self) -> None:
        self.subscriptions.add_many(
            self.DASHBOARD_EVENTS,
            self._handle_dashboard_event,
        )

    def unsubscribe(self) -> None:
        self.subscriptions.clear()

    def dispose(self) -> None:
        self.unsubscribe()

    def load_categories(self) -> None:
        self.state.set_categories(
            category_repository.list_roots(),
            category_repository.list_all(),
        )
        self._notify_state_changed()

    def open_category(self, category: dict) -> None:
        self.state.open_category(category)
        self._notify_state_changed()

    def show_dashboard(self) -> None:
        self.state.show_dashboard()
        self.load_categories()

    async def browse_files(self, on_error=None) -> None:
        if self.state.loading:
            return
        await self.file_picker.pick_files(
            dialog_title="Ajouter des documents",
            allow_multiple=True,
            with_data=False,
            on_error=on_error,
        )

    def set_selected_files(
        self,
        selected_files: list[PaperNestFilePickerFile],
        default_category: str | None,
    ) -> int:
        previous_categories = {
            str(item.path.resolve()).casefold(): item.category_key
            for item in self.state.staged_files
        }
        staged_files: list[StagedFile] = []
        invalid_paths = 0

        for selected in selected_files:
            item = self._to_staged_file(
                selected,
                previous_categories,
                default_category,
            )
            if item is None:
                invalid_paths += 1
            else:
                staged_files.append(item)

        self.state.set_staged_files(staged_files)
        if not staged_files:
            self.state.keep_duplicates = False
        self._notify_state_changed()
        return invalid_paths

    def apply_default_category(self, category_key: str | None) -> None:
        for item in self.state.staged_files:
            item.category_key = category_key
        self._notify_state_changed()

    def set_file_category(
        self,
        file_id: int,
        category_key: str | None,
    ) -> None:
        for item in self.state.staged_files:
            if item.file_id == file_id:
                item.category_key = category_key
                break

    def set_keep_duplicates(self, value: bool) -> None:
        self.state.keep_duplicates = bool(value)

    async def remove_file(self, file_id: int) -> None:
        if not self.state.loading:
            await self.file_picker.remove_file(file_id)

    async def clear_files(self) -> None:
        if not self.state.loading:
            await self.file_picker.clear_files()

    def validate_import(self) -> str | None:
        if self.state.loading or not self.state.staged_files:
            return "Aucun document à classer."
        if any(not item.category_key for item in self.state.staged_files):
            return "Choisissez un classeur pour chaque document."
        return None

    async def import_files(self) -> ImportResult:
        self._set_loading(True)
        imported = duplicates = errors = 0
        files = list(self.state.staged_files)
        total = len(files)

        try:
            for index, item in enumerate(files, start=1):
                self.state.progress = (index - 1) / total
                self.state.summary_text = (
                    f"Traitement de {item.path.name} ({index}/{total})"
                )
                self._notify_state_changed()

                try:
                    analysis = await asyncio.to_thread(
                        duplicate_detection_service.analyze,
                        str(item.path),
                        item.path.stem,
                    )
                    if analysis.has_matches and not self.state.keep_duplicates:
                        duplicates += 1
                        continue

                    await asyncio.to_thread(
                        ArchiveFileService.store_document,
                        str(item.path),
                        item.path.stem,
                        str(item.category_key),
                        allow_duplicate=bool(
                            analysis.has_matches
                            and self.state.keep_duplicates
                        ),
                        source_sha256=analysis.source_sha256,
                    )
                    imported += 1

                except PaperNestError as error:
                    logger.warning(
                        "Import refusé pour %s : %s",
                        item.path,
                        error,
                    )
                    errors += 1

                except Exception:
                    logger.exception(
                        "Erreur inattendue pendant l’import de %s.",
                        item.path,
                    )
                    errors += 1

            self.state.progress = 1
            self._notify_state_changed()
            await self.file_picker.clear_files()
            self.state.clear_staged_files()
            self.load_categories()
            return ImportResult(
                imported=imported,
                duplicates=duplicates,
                errors=errors,
            )

        finally:
            self._set_loading(False)

    def _handle_dashboard_event(self, _event) -> None:
        self.load_categories()

    def _set_loading(self, loading: bool) -> None:
        self.state.loading = loading
        if not loading:
            self.state.progress = 0
            self.state.summary_text = ""
        self._notify_state_changed()

    def _notify_state_changed(self) -> None:
        if self.on_state_changed is not None:
            self.on_state_changed()

    @staticmethod
    def _to_staged_file(
        selected: PaperNestFilePickerFile,
        previous_categories: dict[str, str | None],
        default_category: str | None,
    ) -> StagedFile | None:
        if not selected.path:
            return None

        path = Path(selected.path)
        if not path.exists() or not path.is_file():
            return None

        key = str(path.resolve()).casefold()
        return StagedFile(
            file_id=selected.id,
            path=path,
            category_key=previous_categories.get(key, default_category),
        )
