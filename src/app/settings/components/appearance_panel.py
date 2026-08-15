from __future__ import annotations

from pathlib import Path

import flet as ft
from papernestextension import PaperNestFilePickerFilesChangedEvent

from app.notifications import notifications
from app.theme.buttons import PrimaryButton, SecondaryButton
from app.theme.cards import AppSection
from app.theme.forms import BaseDropDown, PaperNestDropdownOption
from app.theme.pickers import BaseColorPicker, BaseFilePicker
from app.theme.tokens import AppColors, AppRadius, AppSpacing
from core.models.background_settings import BackgroundMode
from services.settings import background_service


class AppearancePanel(AppSection):
    def __init__(self, page: ft.Page) -> None:
        self.app_page = page
        self.settings = background_service.load()
        self.pending_image: Path | None = None

        self.mode_field = BaseDropDown(
            label="Type de fond",
            leading_icon=ft.Icons.WALLPAPER_ROUNDED,
            value=self.settings.mode.value,
            on_select=self._handle_mode_change,
            options=[
                PaperNestDropdownOption(key=BackgroundMode.IMAGE.value, text="Image"),
                PaperNestDropdownOption(key=BackgroundMode.COLOR.value, text="Couleur"),
            ],
        )

        self.color_field = BaseColorPicker(
            label="Couleur du fond",
            value=self.settings.color,
            on_change=self._handle_color_change,
        )
        self.file_picker = BaseFilePicker(
            allow_multiple=False,
            drag_and_drop=True,
            with_data=False,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
            dialog_title="Choisir une image de fond",
            drop_text="Déposez une image de fond ici",
            drop_subtitle="PNG, JPG, JPEG ou WebP — haute résolution acceptée",
            icon=ft.Icons.ADD_PHOTO_ALTERNATE_ROUNDED,
            click_to_pick=True,
            show_file_list=True,
            show_file_size=True,
            show_constraints=True,
            max_file_size="50 MB",
            height=178,
            on_files_changed=self._handle_files_changed,
        )

        self.preview = ft.Container(
            border_radius=AppRadius.MD,
            border=ft.Border.all(1, AppColors.BORDER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
        self.apply_button = PrimaryButton(
            "Appliquer",
            icon=ft.Icons.CHECK_ROUNDED,
            on_click=self._apply,
        )
        self.reset_button = SecondaryButton(
            "Restaurer le fond PaperNest",
            icon=ft.Icons.RESTART_ALT_ROUNDED,
            on_click=self._reset,
        )
        self._render_preview()
        self.mode_content = ft.Column(
            spacing=AppSpacing.MD,
            controls=self._build_mode_controls(),
        )

        super().__init__(
            title="Apparence",
            icon=ft.Icons.PALETTE_OUTLINED,
            content=ft.Column(
                spacing=AppSpacing.MD,
                controls=[
                    ft.Text(
                        "Choisissez une couleur ou une image personnelle. "
                        "L’image est copiée dans les données PaperNest.",
                        size=12,
                        color=AppColors.TEXT_MUTED,
                    ),
                    self.mode_field,
                    self.mode_content,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[self.reset_button, self.apply_button],
                    ),
                ],
            ),
        )

    def _handle_mode_change(self, event=None) -> None:
        selected_value = getattr(event, "data", None)
        if selected_value in {mode.value for mode in BackgroundMode}:
            self.mode_field.value = selected_value
        self._render_preview()
        self.mode_content.controls = self._build_mode_controls()
        self._safe_update()

    def _handle_color_change(self, value: str | None) -> None:
        if value:
            self._render_preview(color=value)
            self._safe_update()

    def _handle_files_changed(self, event: PaperNestFilePickerFilesChangedEvent) -> None:
        self.pending_image = None
        if event.selected_files and event.selected_files[0].path:
            path = Path(event.selected_files[0].path)
            if path.is_file():
                self.pending_image = path
        self._render_preview()
        self._safe_update()

    def _apply(self, _event=None) -> None:
        try:
            mode = self._selected_mode()
            if mode is BackgroundMode.COLOR:
                settings = background_service.use_color(str(self.color_field.value or ""))
            elif self.pending_image is not None:
                settings = background_service.import_image(self.pending_image)
            else:
                settings = background_service.use_image()
            self.settings = settings
            self.pending_image = None
            background_service.apply(self.app_page, settings)
            notifications(self.app_page).success("Le fond de l’application a été mis à jour.")
            self.app_page.update()
        except ValueError as error:
            notifications(self.app_page).error(str(error))
        except OSError:
            notifications(self.app_page).error("Impossible d’enregistrer l’image de fond.")

    def _reset(self, _event=None) -> None:
        self.settings = background_service.reset()
        self.pending_image = None
        self.mode_field.value = self.settings.mode.value
        self.color_field.value = self.settings.color
        background_service.apply(self.app_page, self.settings)
        self._render_preview()
        self.mode_content.controls = self._build_mode_controls()
        notifications(self.app_page).success("Le fond PaperNest par défaut a été restauré.")
        self.app_page.update()

    def _selected_mode(self) -> BackgroundMode:
        try:
            return BackgroundMode(str(self.mode_field.value))
        except ValueError:
            return BackgroundMode.IMAGE

    def _render_preview(self, *, color: str | None = None) -> None:
        mode = self._selected_mode()
        if mode is BackgroundMode.COLOR:
            self.preview.height = 72
            self.preview.bgcolor = color or str(self.color_field.value or self.settings.color)
            self.preview.content = None
            return
        self.preview.height = 178
        self.preview.bgcolor = None
        source = background_service.resolve_image_source(
            str(self.pending_image)
            if self.pending_image is not None
            else self.settings.image_path
        )
        self.preview.content = ft.Image(
            src=source,
            fit=ft.BoxFit.COVER,
            width=1200,
            height=180,
        )

    def _build_mode_controls(self) -> list[ft.Control]:
        if self._selected_mode() is BackgroundMode.COLOR:
            return [
                self.color_field,
                ft.Text("Aperçu", weight=ft.FontWeight.BOLD),
                self.preview,
            ]
        return [
            ft.ResponsiveRow(
                spacing=AppSpacing.LG,
                run_spacing=AppSpacing.MD,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        col={"sm": 12, "lg": 6},
                        content=self.file_picker,
                    ),
                    ft.Container(
                        col={"sm": 12, "lg": 6},
                        content=ft.Column(
                            spacing=AppSpacing.SM,
                            controls=[
                                ft.Text("Aperçu", weight=ft.FontWeight.BOLD),
                                self.preview,
                            ],
                        ),
                    ),
                ],
            )
        ]

    def _safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
