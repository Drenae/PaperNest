from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import flet as ft
from papernestextension import (
    PaperNestFilePickerFile,
    PaperNestFilePickerFilesChangedEvent,
    PaperNestFilePickerValidationEvent,
)

from app.notifications import notifications
from app.theme.buttons import IconAction, PrimaryButton
from app.theme.cards import AppSection
from app.theme.pickers import BaseFilePicker
from app.theme.forms import BaseCheckbox, BaseDropDown, PaperNestDropdownOption
from app.theme.tokens import AppColors
from core.errors.exceptions import PaperNestError
from repositories.category_repository import category_repository
from services.documents.duplicates import duplicate_detection_service
from services.files.archive import ArchiveFileService


logger = logging.getLogger(__name__)


@dataclass
class StagedFile:
    file_id: int
    path: Path
    category_key: str | None = None


class UploadPanel(AppSection):
    """Import multiple piloté par la sélection interne de PaperNestFilePicker."""

    def __init__(
        self,
        page: ft.Page,
        processing_bar: ft.ProgressBar,
        on_storage_done: Callable | None = None,
    ):
        self.app_page = page
        self.processing_bar = processing_bar
        self.on_storage_done = on_storage_done
        self.staged_files: list[StagedFile] = []
        self.category_options: list[PaperNestDropdownOption] = []
        self.loading = False
        self._mounted = True

        self.file_picker = BaseFilePicker(
            allow_multiple=True,
            drag_and_drop=True,
            with_data=False,
            show_file_list=True,
            show_file_size=True,
            use_file_type_colors=True,
            dialog_title="Sélectionner des documents",
            drop_text="Déposez vos documents ici",
            drop_subtitle="ou utilisez le bouton ci-dessous",
            icon=ft.Icons.UPLOAD_FILE_ROUNDED,
            click_to_pick=True,
            show_constraints=False,
            on_files_changed=self.handle_files_changed,
            on_validation_error=self.handle_validation_error,
            on_duplicate_file=self.handle_duplicate_file,
        )
        self.browse_trigger = PrimaryButton(
            "Ajouter des fichiers",
            icon=ft.Icons.FOLDER_OPEN_ROUNDED,
            on_click=self.browse_files,
            expand=True,
        )
        self.clear_trigger = IconAction(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_color=AppColors.TEXT_MUTED,
            tooltip="Retirer tous les fichiers préparés",
            visible=False,
            on_click=self.clear_staged_files,
        )
        self.category_selector = BaseDropDown(
            label="Classeur par défaut",
            icon=ft.Icons.FOLDER_COPY_ROUNDED,
            options=[],
        )
        self.category_selector.disabled = True
        self.category_selector.on_select = self.apply_default_category
        self.keep_duplicates = BaseCheckbox(
            label="Importer aussi les doublons détectés",
            value=False,
            disabled=True,
        )
        self.files_list = ft.Column(spacing=8)
        self.files_container = ft.Container(
            visible=False,
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Classement des documents", expand=True, weight=ft.FontWeight.BOLD),
                            self.clear_trigger,
                        ]
                    ),
                    self.category_selector,
                    ft.Text(
                        "Le classeur par défaut est appliqué à tous. Modifiez seulement les exceptions.",
                        size=11,
                        color=AppColors.TEXT_MUTED,
                    ),
                    self.files_list,
                    self.keep_duplicates,
                ],
            ),
        )
        self.commit_trigger = PrimaryButton(
            "Classer les documents",
            icon=ft.Icons.INVENTORY_2_ROUNDED,
            on_click=self.finalize_storage,
            expand=True,
        )
        self.commit_trigger.disabled = True
        self.summary_text = ft.Text("", size=11, color=AppColors.TEXT_MUTED, visible=False)

        self.processing_bar.visible = False
        self.processing_bar.value = 0
        self.processing_bar.color = AppColors.PRIMARY_DARK
        self.processing_bar.bgcolor = ft.Colors.GREY_300

        super().__init__(
            title="Classer des fichiers",
            icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            content=ft.Column(
                spacing=14,
                controls=[
                    self.file_picker,
                    ft.Row([self.browse_trigger]),
                    self.files_container,
                    self.processing_bar,
                    self.summary_text,
                    ft.Row([self.commit_trigger]),
                ],
            ),
            expand=1,
        )
        self.refresh_categories()

    async def browse_files(self, _event=None) -> None:
        if self.loading:
            return
        await self.file_picker.pick_files(
            dialog_title="Ajouter des documents",
            allow_multiple=True,
            with_data=False,
            on_error=self.handle_picker_error,
        )

    def handle_picker_error(self, _error: RuntimeError) -> None:
        notifications(self.app_page).error("Impossible d’ouvrir le sélecteur de fichiers.")

    def refresh_categories(self) -> None:
        categories = category_repository.list_all()
        self.category_options = [
            PaperNestDropdownOption(
                key=str(category["key"]),
                text=f"↳ {category['name']}" if category.get("parent_key") else str(category["name"]),
            )
            for category in categories
        ]
        self.category_selector.options = list(self.category_options)
        self._safe_update()

    def handle_files_changed(self, event: PaperNestFilePickerFilesChangedEvent) -> None:
        previous_categories = {
            str(item.path.resolve()).casefold(): item.category_key for item in self.staged_files
        }
        default_category = str(self.category_selector.value) if self.category_selector.value else None
        staged: list[StagedFile] = []
        invalid_paths = 0
        for selected in event.selected_files:
            item = self._to_staged_file(selected, previous_categories, default_category)
            if item is None:
                invalid_paths += 1
            else:
                staged.append(item)
        self.staged_files = staged
        if invalid_paths:
            notifications(self.app_page).warning(
                "Certains fichiers sélectionnés ne fournissent pas de chemin local exploitable."
            )
        self._refresh_selection_ui()

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

    def handle_validation_error(self, event: PaperNestFilePickerValidationEvent) -> None:
        notifications(self.app_page).warning(
            event.message or "Ce fichier ne respecte pas les contraintes de sélection."
        )

    def handle_duplicate_file(self, _event) -> None:
        notifications(self.app_page).warning("Ce fichier est déjà présent dans la sélection.")

    def _refresh_selection_ui(self) -> None:
        has_files = bool(self.staged_files)
        self.files_container.visible = has_files
        self.clear_trigger.visible = has_files
        self.category_selector.disabled = self.loading or not has_files
        self.keep_duplicates.disabled = self.loading or not has_files
        self.commit_trigger.disabled = self.loading or not has_files
        self.summary_text.visible = False
        if has_files:
            self.render_file_rows()
        else:
            self.files_list.controls.clear()
            self.category_selector.value = None
            self.keep_duplicates.value = False
        self._safe_page_update()

    def render_file_rows(self) -> None:
        rows: list[ft.Control] = []
        for item in self.staged_files:
            dropdown = BaseDropDown(
                value=item.category_key,
                width=190,
                dense=True,
                options=[
                    PaperNestDropdownOption(key=option.key, text=option.text)
                    for option in self.category_options
                ],
                data=item.file_id,
                on_change=self.handle_row_category,
            )
            rows.append(
                ft.Container(
                    padding=8,
                    border=ft.Border.all(1, AppColors.BORDER),
                    border_radius=10,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=18, color=AppColors.TEXT_MUTED),
                            ft.Text(item.path.name, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            dropdown,
                            IconAction(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                tooltip="Retirer ce fichier",
                                data=item.file_id,
                                on_click=self.remove_file,
                            ),
                        ],
                    ),
                )
            )
        self.files_list.controls = rows

    def apply_default_category(self, _event=None) -> None:
        category = str(self.category_selector.value) if self.category_selector.value else None
        for item in self.staged_files:
            item.category_key = category
        self.render_file_rows()
        self._safe_page_update()

    def handle_row_category(self, event) -> None:
        file_id = int(event.control.data)
        for item in self.staged_files:
            if item.file_id == file_id:
                item.category_key = str(event.control.value) if event.control.value else None
                break

    def remove_file(self, event) -> None:
        if not self.loading:
            self.app_page.run_task(self.file_picker.remove_file, int(event.control.data))

    def clear_staged_files(self, _event=None) -> None:
        if not self.loading:
            self.app_page.run_task(self.file_picker.clear_files)

    def finalize_storage(self, _event=None) -> None:
        if self.loading or not self.staged_files:
            return
        if any(not item.category_key for item in self.staged_files):
            notifications(self.app_page).warning("Choisissez un classeur pour chaque document.")
            return
        self.app_page.run_task(self.run_batch_storage)

    async def run_batch_storage(self) -> None:
        self.set_loading(True)
        imported = duplicates = errors = 0
        total = len(self.staged_files)
        try:
            for index, item in enumerate(list(self.staged_files), start=1):
                self.processing_bar.value = (index - 1) / total
                self.summary_text.value = f"Traitement de {item.path.name} ({index}/{total})"
                self.summary_text.visible = True
                self._safe_page_update()
                try:
                    analysis = await asyncio.to_thread(
                        duplicate_detection_service.analyze,
                        str(item.path),
                        item.path.stem,
                    )
                    if analysis.has_matches and not bool(self.keep_duplicates.value):
                        duplicates += 1
                        continue
                    await asyncio.to_thread(
                        ArchiveFileService.store_document,
                        str(item.path),
                        item.path.stem,
                        str(item.category_key),
                        allow_duplicate=bool(analysis.has_matches and self.keep_duplicates.value),
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
            self.processing_bar.value = 1
            notifications(self.app_page).success(
                f"Import terminé : {imported} classé(s), {duplicates} doublon(s) ignoré(s), {errors} erreur(s)."
            )
            await self.file_picker.clear_files()
            if self.on_storage_done is not None:
                result = self.on_storage_done(None)
                if asyncio.iscoroutine(result):
                    await result
        finally:
            self.set_loading(False)

    def set_loading(self, loading: bool) -> None:
        self.loading = loading
        self.processing_bar.visible = loading
        if not loading:
            self.processing_bar.value = 0
        self.file_picker.disabled = loading
        self.browse_trigger.disabled = loading
        self.clear_trigger.disabled = loading
        self.category_selector.disabled = loading or not bool(self.staged_files)
        self.keep_duplicates.disabled = loading or not bool(self.staged_files)
        self.commit_trigger.disabled = loading or not bool(self.staged_files)
        self._safe_page_update()

    def dispose(self) -> None:
        self._mounted = False

    def _safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass

    def _safe_page_update(self) -> None:
        if not self._mounted:
            return
        try:
            self.app_page.update()
        except RuntimeError:
            pass
