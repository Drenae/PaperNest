from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import flet as ft

from app.theme.forms import BaseCheckbox, BaseFilePicker, PaperNestDropdownOption

from app.theme.buttons import IconAction
from app.theme.forms import BaseDropDown

from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors
from repositories.category_repository import category_repository
from services.documents.duplicates import duplicate_detection_service
from services.files.archive import ArchiveFileService
from app.theme.buttons import PrimaryButton, SecondaryButton
from app.theme.cards import Section
from app.shared.file_drop_zone import FileDropZone
from app.notifications import notifications


@dataclass
class StagedFile:
    path: Path
    category_key: str | None = None


class UploadPanel(Section):
    """Import stable, multiple et séquentiel de documents locaux."""

    def __init__(
        self,
        page: ft.Page,
        file_picker: BaseFilePicker,
        processing_bar: ft.ProgressBar,
        on_storage_done: Callable | None = None,
    ):
        self.app_page = page
        self.file_picker = file_picker
        self.processing_bar = processing_bar
        self.on_storage_done = on_storage_done
        self.staged_files: list[StagedFile] = []
        self.category_options: list[PaperNestDropdownOption] = []
        self.loading = False
        self.picker_open = False
        self._mounted = True

        self.drop_zone = FileDropZone(on_file_dropped=self.handle_dropped_files)
        self.upload_trigger = PrimaryButton(
            "Sélectionner des fichiers",
            icon=ft.Icons.UPLOAD_FILE_ROUNDED,
            on_click=self.pick_files,
            expand=True,
        )
        self.replace_trigger = SecondaryButton(
            text="Remplacer la sélection",
            icon=ft.Icons.SWAP_HORIZ_ROUNDED,
            on_click=self.pick_files,
        )
        self.replace_trigger.visible = False
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
                            ft.Text("Documents préparés", expand=True, weight=ft.FontWeight.BOLD),
                            self.replace_trigger,
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
                    self.drop_zone,
                    ft.Row([self.upload_trigger]),
                    self.files_container,
                    self.processing_bar,
                    self.summary_text,
                    ft.Row([self.commit_trigger]),
                ],
            ),
            expand=1,
        )
        self.refresh_categories()

    def refresh_categories(self) -> None:
        categories = category_repository.list_all()
        self.category_options = [
            PaperNestDropdownOption(key=str(category["key"]), text=(f"↳ {category['name']}" if category.get("parent_key") else str(category["name"])))
            for category in categories
        ]
        self.category_selector.options = list(self.category_options)
        self._safe_update()

    async def pick_files(self, _event=None) -> None:
        if self.loading or self.picker_open:
            return
        self.picker_open = True
        self.upload_trigger.disabled = True
        self.replace_trigger.disabled = True
        self._safe_page_update()
        try:
            files = await self.file_picker.pick_files(
                allow_multiple=True,
                on_error=self.handle_picker_error,
            )
            if not files:
                return
            paths = [Path(item.path) for item in files if item.path]
            self.stage_files(paths)
        finally:
            self.picker_open = False
            self.upload_trigger.disabled = self.loading
            self.replace_trigger.disabled = self.loading
            self._safe_page_update()


    def handle_picker_error(self, error: RuntimeError) -> None:
        message = str(error)
        if "TimeoutException" in message or "Timeout waiting" in message:
            notifications(self.app_page).warning(
                "Le sélecteur de fichiers n’a pas répondu. Fermez toute fenêtre de sélection encore ouverte puis réessayez."
            )
        else:
            notifications(self.app_page).error(
                "Impossible d’ouvrir le sélecteur de fichiers."
            )

    def handle_dropped_files(self, files: list[Path]) -> None:
        if not self.loading:
            self.stage_files(files)

    def stage_files(self, paths: list[Path]) -> None:
        valid = [path for path in paths if path.exists() and path.is_file()]
        if not valid:
            notifications(self.app_page).warning("Aucun fichier valide n’a été sélectionné.")
            return
        unique: dict[str, Path] = {str(path.resolve()).casefold(): path for path in valid}
        default_category = str(self.category_selector.value) if self.category_selector.value else None
        self.staged_files = [StagedFile(path=path, category_key=default_category) for path in unique.values()]
        self.drop_zone.show_selected_files([item.path for item in self.staged_files])
        self.files_container.visible = True
        self.replace_trigger.visible = True
        self.clear_trigger.visible = True
        self.category_selector.disabled = False
        self.keep_duplicates.disabled = False
        self.commit_trigger.disabled = False
        self.summary_text.visible = False
        self.render_file_rows()
        self._safe_page_update()

    def render_file_rows(self) -> None:
        rows: list[ft.Control] = []
        for index, item in enumerate(self.staged_files):
            dropdown = BaseDropDown(
                value=item.category_key,
                width=190,
                dense=True,
                options=[PaperNestDropdownOption(key=option.key, text=option.text) for option in self.category_options],
                data=index,
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
                                data=index,
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
        index = int(event.control.data)
        if 0 <= index < len(self.staged_files):
            self.staged_files[index].category_key = str(event.control.value) if event.control.value else None

    def remove_file(self, event) -> None:
        index = int(event.control.data)
        if 0 <= index < len(self.staged_files):
            self.staged_files.pop(index)
        if not self.staged_files:
            self.reset_form()
        else:
            self.drop_zone.show_selected_files([item.path for item in self.staged_files])
            self.render_file_rows()
        self._safe_page_update()

    def clear_staged_files(self, _event=None) -> None:
        if not self.loading:
            self.reset_form()
            self._safe_page_update()

    def finalize_storage(self, _event=None) -> None:
        if self.loading or not self.staged_files:
            return
        missing = [item.path.name for item in self.staged_files if not item.category_key]
        if missing:
            notifications(self.app_page).warning("Choisissez un classeur pour chaque document.")
            return
        self.app_page.run_task(self.run_batch_storage)

    async def run_batch_storage(self) -> None:
        self.set_loading(True)
        imported = 0
        duplicates = 0
        errors = 0
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
                except PaperNestError:
                    errors += 1
                except Exception:
                    errors += 1
            self.processing_bar.value = 1
            notifications(self.app_page).success(
                f"Import terminé : {imported} classé(s), {duplicates} doublon(s) ignoré(s), {errors} erreur(s)."
            )
            self.reset_form()
            if self.on_storage_done is not None:
                result = self.on_storage_done(None)
                if asyncio.iscoroutine(result):
                    await result
        finally:
            self.set_loading(False)

    def reset_form(self) -> None:
        self.staged_files = []
        self.category_selector.value = None
        self.category_selector.disabled = True
        self.keep_duplicates.value = False
        self.keep_duplicates.disabled = True
        self.files_list.controls.clear()
        self.files_container.visible = False
        self.replace_trigger.visible = False
        self.clear_trigger.visible = False
        self.commit_trigger.disabled = True
        self.summary_text.visible = False
        self.drop_zone.reset()

    def set_loading(self, loading: bool) -> None:
        self.loading = loading
        self.processing_bar.visible = loading
        if not loading:
            self.processing_bar.value = 0
        self.drop_zone.set_loading(loading)
        self.upload_trigger.disabled = loading or self.picker_open
        self.replace_trigger.disabled = loading or self.picker_open
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
