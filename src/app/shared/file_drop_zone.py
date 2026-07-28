from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import flet as ft
import flet_dropzone as ftd

from app.theme.tokens import AppColors


class FileDropZone(ftd.Dropzone):
    """Zone de dépôt locale acceptant un ou plusieurs fichiers."""

    def __init__(self, on_file_dropped: Callable[[list[Path]], None] | None = None):
        self.on_file_dropped = on_file_dropped
        self.selected_files: list[Path] = []
        self.icon_control = ft.Icon(ft.Icons.FILE_DOWNLOAD_OUTLINED, size=40, color=AppColors.PRIMARY_DARK)
        self.title_control = ft.Text(
            "Déposez vos documents ici",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_MAIN,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.subtitle_control = ft.Text(
            "ou sélectionnez plusieurs fichiers depuis votre ordinateur",
            size=12,
            color=AppColors.TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
        )
        self.file_information = ft.Text(
            "",
            size=11,
            color=AppColors.TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
            visible=False,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.visual_container = ft.Container(
            height=150,
            alignment=ft.Alignment.CENTER,
            padding=18,
            bgcolor=ft.Colors.YELLOW_50,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=14,
            content=ft.Column(
                tight=True,
                spacing=7,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.icon_control, self.title_control, self.subtitle_control, self.file_information],
            ),
        )
        super().__init__(
            content=self.visual_container,
            allowed_file_types=[],
            on_entered=self.handle_entered,
            on_exited=self.handle_exited,
            on_dropped=self.handle_dropped,
        )

    def handle_entered(self, _event) -> None:
        if self.disabled:
            return
        self.visual_container.bgcolor = ft.Colors.YELLOW_100
        self.visual_container.border = ft.Border.all(2, AppColors.PRIMARY_DARK)
        self.icon_control.icon = ft.Icons.DOWNLOAD_FOR_OFFLINE_ROUNDED
        self.title_control.value = "Relâchez pour préparer les documents"
        self.subtitle_control.value = "Vous pourrez choisir un classeur commun ou différent"
        self._safe_update()

    def handle_exited(self, _event) -> None:
        if not self.disabled:
            self._restore_current_visual_state()
            self._safe_update()

    def handle_dropped(self, event) -> None:
        if self.disabled:
            return
        paths = [Path(path) for path in (event.files or []) if path]
        valid_files = [path for path in paths if path.exists() and path.is_file()]
        if valid_files:
            self.show_selected_files(valid_files)
        else:
            self.reset_visual_state()
        if self.on_file_dropped is not None:
            self.on_file_dropped(valid_files)
        self._safe_update()

    def show_selected_file(self, file_path: Path) -> None:
        self.show_selected_files([file_path])

    def show_selected_files(self, file_paths: list[Path]) -> None:
        self.selected_files = list(file_paths)
        count = len(self.selected_files)
        self.visual_container.bgcolor = ft.Colors.GREEN_50
        self.visual_container.border = ft.Border.all(1, ft.Colors.GREEN_600)
        self.icon_control.icon = ft.Icons.CHECK_CIRCLE_ROUNDED
        self.icon_control.color = ft.Colors.GREEN_700
        self.title_control.value = f"{count} document{'s' if count > 1 else ''} prêt{'s' if count > 1 else ''}"
        self.subtitle_control.value = "Vérifiez les destinations avant le classement"
        preview = ", ".join(path.name for path in self.selected_files[:3])
        if count > 3:
            preview += f" et {count - 3} autre(s)"
        self.file_information.value = preview
        self.file_information.visible = True
        self._safe_update()

    def set_loading(self, loading: bool) -> None:
        self.disabled = loading
        if loading:
            self.visual_container.bgcolor = ft.Colors.GREY_100
            self.visual_container.border = ft.Border.all(1, ft.Colors.GREY_400)
            self.icon_control.icon = ft.Icons.HOURGLASS_TOP_ROUNDED
            self.icon_control.color = AppColors.TEXT_MUTED
            self.title_control.value = "Classement en cours..."
            self.subtitle_control.value = "PaperNest traite les fichiers un par un"
        else:
            self._restore_current_visual_state()
        self._safe_update()

    def reset(self) -> None:
        self.selected_files = []
        self.reset_visual_state()
        self._safe_update()

    def reset_visual_state(self) -> None:
        self.visual_container.bgcolor = ft.Colors.YELLOW_50
        self.visual_container.border = ft.Border.all(1, AppColors.BORDER)
        self.icon_control.icon = ft.Icons.FILE_DOWNLOAD_OUTLINED
        self.icon_control.color = AppColors.PRIMARY_DARK
        self.title_control.value = "Déposez vos documents ici"
        self.subtitle_control.value = "ou sélectionnez plusieurs fichiers depuis votre ordinateur"
        self.file_information.value = ""
        self.file_information.visible = False

    def _restore_current_visual_state(self) -> None:
        if self.selected_files:
            self.show_selected_files(self.selected_files)
        else:
            self.reset_visual_state()

    def _safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
