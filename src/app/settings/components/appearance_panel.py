from __future__ import annotations

from pathlib import Path

import flet as ft
from papernestextension import (
    PaperNestFilePickerFile,
    PaperNestFilePickerFilesChangedEvent,
)

from app.notifications import notifications
from app.theme.buttons import IconAction, PrimaryButton, SecondaryButton
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
        self.pending_alignment_x = 0.0
        self.pending_alignment_y = 0.0
        self.pending_zoom = 1.0
        self._preview_source = None
        self._normalizing_picker = False

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
            show_file_list=False,
            show_file_size=True,
            show_constraints=True,
            max_file_size="50 MB",
            height=178,
            on_files_changed=self._handle_files_changed,
        )

        self.selected_file_name = ft.Text(
            "",
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.selected_file_size = ft.Text(
            "",
            size=12,
            color=AppColors.TEXT_MUTED,
        )
        self.selected_file = ft.Container(
            visible=False,
            padding=ft.Padding.only(
                left=AppSpacing.MD,
                right=AppSpacing.XS,
                top=AppSpacing.XS,
                bottom=AppSpacing.XS,
            ),
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=AppRadius.MD,
            content=ft.Row(
                spacing=AppSpacing.SM,
                controls=[
                    ft.Icon(
                        ft.Icons.IMAGE_OUTLINED,
                        size=20,
                        color=AppColors.INFO,
                    ),
                    self.selected_file_name,
                    self.selected_file_size,
                    IconAction(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        tooltip="Retirer l’image sélectionnée",
                        compact=True,
                        on_click=self._clear_selected_file,
                    ),
                ],
            ),
        )

        self.current_preview = self._new_preview_container()
        self.preview = self._new_preview_container()
        self.zoom_label = ft.Text("100 %", size=11, color=AppColors.TEXT_LIGHT)
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
        self._render_previews()
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
        self._render_previews()
        self.mode_content.controls = self._build_mode_controls()
        self._safe_update()

    def _handle_color_change(self, value: str | None) -> None:
        if value:
            self._render_previews(color=value)
            self._safe_update()

    def _handle_files_changed(self, event: PaperNestFilePickerFilesChangedEvent) -> None:
        selected_files = event.selected_files
        selected = selected_files[-1] if selected_files else None
        self._set_selected_file(selected)
        if len(selected_files) > 1 and not self._normalizing_picker:
            self._normalizing_picker = True
            self.app_page.run_task(
                self._keep_last_picker_file,
                len(selected_files) - 1,
            )
        self._render_previews()
        self._safe_update()

    def _set_selected_file(self, selected: PaperNestFilePickerFile | None) -> None:
        previous_path = self.pending_image
        self.pending_image = None
        self.selected_file.visible = False
        if selected is None or not selected.path:
            return
        path = Path(selected.path)
        if not path.is_file():
            return
        self.pending_image = path
        if previous_path != path:
            self.pending_alignment_x = 0.0
            self.pending_alignment_y = 0.0
            self.pending_zoom = 1.0
        self._preview_source = background_service.load_preview_image(path)
        self.selected_file_name.value = selected.name
        self.selected_file_size.value = self._format_file_size(selected.size)
        self.selected_file.visible = True

    async def _keep_last_picker_file(self, files_to_remove: int) -> None:
        try:
            for _ in range(files_to_remove):
                await self.file_picker.remove_file(0)
        finally:
            self._normalizing_picker = False

    def _clear_selected_file(self, _event=None) -> None:
        self.pending_image = None
        self.pending_alignment_x = 0.0
        self.pending_alignment_y = 0.0
        self.pending_zoom = 1.0
        self._preview_source = None
        self.selected_file.visible = False
        self._render_previews()
        self._safe_update()
        self.app_page.run_task(self.file_picker.clear_files)

    def _apply(self, _event=None) -> None:
        try:
            mode = self._selected_mode()
            if mode is BackgroundMode.COLOR:
                settings = background_service.use_color(str(self.color_field.value or ""))
            elif self.pending_image is not None:
                settings = background_service.import_image(
                    self.pending_image,
                    alignment_x=self.pending_alignment_x,
                    alignment_y=self.pending_alignment_y,
                    zoom=self.pending_zoom,
                    target_aspect_ratio=self._page_aspect_ratio(),
                )
            else:
                settings = background_service.use_image()
            self.settings = settings
            self.pending_image = None
            self.pending_alignment_x = settings.alignment_x
            self.pending_alignment_y = settings.alignment_y
            self.pending_zoom = 1.0
            self._preview_source = None
            self.selected_file.visible = False
            background_service.apply(self.app_page, settings)
            self._render_previews()
            self.app_page.run_task(self.file_picker.clear_files)
            notifications(self.app_page).success("Le fond de l’application a été mis à jour.")
            self.app_page.update()
        except ValueError as error:
            notifications(self.app_page).error(str(error))
        except OSError:
            notifications(self.app_page).error("Impossible d’enregistrer l’image de fond.")

    def _reset(self, _event=None) -> None:
        self.settings = background_service.reset()
        self.pending_image = None
        self.pending_alignment_x = 0.0
        self.pending_alignment_y = 0.0
        self.pending_zoom = 1.0
        self._preview_source = None
        self.selected_file.visible = False
        self.mode_field.value = self.settings.mode.value
        self.color_field.value = self.settings.color
        background_service.apply(self.app_page, self.settings)
        self._render_previews()
        self.mode_content.controls = self._build_mode_controls()
        self.app_page.run_task(self.file_picker.clear_files)
        notifications(self.app_page).success("Le fond PaperNest par défaut a été restauré.")
        self.app_page.update()

    def _selected_mode(self) -> BackgroundMode:
        try:
            return BackgroundMode(str(self.mode_field.value))
        except ValueError:
            return BackgroundMode.IMAGE

    @staticmethod
    def _new_preview_container() -> ft.Container:
        return ft.Container(
            height=190,
            border_radius=AppRadius.MD,
            border=ft.Border.all(1, AppColors.BORDER),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    def _render_previews(self, *, color: str | None = None) -> None:
        self._render_current_preview()
        mode = self._selected_mode()
        if mode is BackgroundMode.COLOR:
            self.preview.height = 190
            self.preview.image = None
            self.preview.bgcolor = color or str(self.color_field.value or self.settings.color)
            self.preview.content = None
            return
        self.preview.height = 190
        if self.pending_image is None:
            self._render_empty_image_preview()
            return
        source = background_service.resolve_image_source(str(self.pending_image))
        preview_alignment_x = self.pending_alignment_x
        preview_alignment_y = self.pending_alignment_y
        if self.pending_zoom > 1.0 and self._preview_source is not None:
            source = background_service.render_crop_preview(
                self._preview_source,
                alignment_x=self.pending_alignment_x,
                alignment_y=self.pending_alignment_y,
                zoom=self.pending_zoom,
                target_aspect_ratio=self._page_aspect_ratio(),
            )
            preview_alignment_x = 0.0
            preview_alignment_y = 0.0
        self._render_image(
            self.preview,
            source,
            alignment_x=preview_alignment_x,
            alignment_y=preview_alignment_y,
            interactive=True,
        )

    def _render_current_preview(self) -> None:
        if self.settings.mode is BackgroundMode.COLOR:
            self.current_preview.image = None
            self.current_preview.bgcolor = self.settings.color
            self.current_preview.content = None
            return
        source = background_service.resolve_image_source(self.settings.image_path)
        self._render_image(
            self.current_preview,
            source,
            alignment_x=self.settings.alignment_x,
            alignment_y=self.settings.alignment_y,
        )

    def _render_image(
        self,
        container: ft.Container,
        source: str | bytes,
        *,
        alignment_x: float,
        alignment_y: float,
        interactive: bool = False,
    ) -> None:
        container.bgcolor = None
        container.image = ft.DecorationImage(
            src=source,
            fit=ft.BoxFit.COVER,
            alignment=ft.Alignment(alignment_x, alignment_y),
        )
        container.content = (
            ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                drag_interval=16,
                on_pan_update=self._handle_crop_pan,
                on_scroll=self._handle_crop_scroll,
                content=ft.Container(
                    expand=True,
                    alignment=ft.Alignment.BOTTOM_CENTER,
                    padding=AppSpacing.SM,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=AppSpacing.XS,
                        controls=[
                            self._zoom_controls(),
                            ft.Container(
                                padding=ft.Padding.symmetric(
                                    horizontal=AppSpacing.MD,
                                    vertical=AppSpacing.XS,
                                ),
                                border_radius=AppRadius.PILL,
                                bgcolor=ft.Colors.with_opacity(
                                    0.72,
                                    AppColors.PANEL_DARK,
                                ),
                                content=ft.Text(
                                    "Glissez pour cadrer · molette pour zoomer",
                                    size=11,
                                    color=AppColors.TEXT_LIGHT,
                                ),
                            ),
                        ],
                    ),
                ),
            )
            if interactive
            else None
        )

    def _render_empty_image_preview(self) -> None:
        self.preview.image = None
        self.preview.bgcolor = ft.Colors.with_opacity(
            0.45,
            AppColors.SURFACE,
        )
        self.preview.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=AppSpacing.SM,
            controls=[
                ft.Icon(
                    ft.Icons.CROP_FREE_ROUNDED,
                    color=AppColors.TEXT_MUTED,
                ),
                ft.Text(
                    "Sélectionnez une image pour voir l’aperçu",
                    color=AppColors.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        )

    def _handle_crop_pan(
        self,
        event: ft.DragUpdateEvent[ft.GestureDetector],
    ) -> None:
        if self.pending_image is None:
            return
        self.pending_alignment_x = self._clamp_alignment(
            self.pending_alignment_x - (event.local_delta.x / 150)
        )
        self.pending_alignment_y = self._clamp_alignment(
            self.pending_alignment_y - (event.local_delta.y / 95)
        )
        if self.preview.image is not None:
            self._refresh_interactive_preview()

    def _handle_crop_scroll(self, event) -> None:
        delta = getattr(getattr(event, "scroll_delta", None), "y", 0.0)
        if not delta:
            return
        self._set_zoom(self.pending_zoom + (-0.15 if delta > 0 else 0.15))

    def _zoom_out(self, _event=None) -> None:
        self._set_zoom(self.pending_zoom - 0.25)

    def _zoom_in(self, _event=None) -> None:
        self._set_zoom(self.pending_zoom + 0.25)

    def _reset_crop(self, _event=None) -> None:
        self.pending_alignment_x = 0.0
        self.pending_alignment_y = 0.0
        self._set_zoom(1.0)

    def _set_zoom(self, value: float) -> None:
        if self.pending_image is None:
            return
        self.pending_zoom = max(1.0, min(4.0, value))
        self.zoom_label.value = f"{round(self.pending_zoom * 100):d} %"
        self._refresh_interactive_preview()

    def _refresh_interactive_preview(self) -> None:
        self._render_previews()
        self._safe_update()

    def _zoom_controls(self) -> ft.Container:
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=AppSpacing.XS),
            border_radius=AppRadius.PILL,
            bgcolor=ft.Colors.with_opacity(0.82, AppColors.PANEL_DARK),
            content=ft.Row(
                tight=True,
                spacing=0,
                controls=[
                    IconAction(
                        icon=ft.Icons.REMOVE_ROUNDED,
                        tooltip="Dézoomer",
                        compact=True,
                        on_click=self._zoom_out,
                    ),
                    self.zoom_label,
                    IconAction(
                        icon=ft.Icons.RESTART_ALT_ROUNDED,
                        tooltip="Réinitialiser le cadrage",
                        compact=True,
                        on_click=self._reset_crop,
                    ),
                    IconAction(
                        icon=ft.Icons.ADD_ROUNDED,
                        tooltip="Zoomer",
                        compact=True,
                        on_click=self._zoom_in,
                    ),
                ],
            ),
        )

    def _page_aspect_ratio(self) -> float:
        width = float(getattr(self.app_page, "width", 0) or 0)
        height = float(getattr(self.app_page, "height", 0) or 0)
        return width / height if width > 0 and height > 0 else 16 / 9

    @staticmethod
    def _clamp_alignment(value: float) -> float:
        return max(-1.0, min(1.0, value))

    def _build_mode_controls(self) -> list[ft.Control]:
        if self._selected_mode() is BackgroundMode.COLOR:
            return [
                self._responsive_pair(
                    self.mode_field,
                    self.color_field,
                ),
                self._responsive_pair(
                    self._preview_block("Fond actuel", self.current_preview),
                    self._preview_block("Aperçu", self.preview),
                ),
            ]
        return [
            self._responsive_pair(
                ft.Column(
                    spacing=AppSpacing.MD,
                    controls=[
                        self.mode_field,
                        self.selected_file,
                    ],
                ),
                self.file_picker,
            ),
            self._responsive_pair(
                self._preview_block("Fond actuel", self.current_preview),
                self._preview_block("Aperçu", self.preview),
            ),
        ]

    @staticmethod
    def _responsive_pair(left: ft.Control, right: ft.Control) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            spacing=AppSpacing.LG,
            run_spacing=AppSpacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    col={"sm": 12, "md": 6},
                    content=left,
                ),
                ft.Container(
                    col={"sm": 12, "md": 6},
                    content=right,
                ),
            ],
        )

    @staticmethod
    def _preview_block(title: str, preview: ft.Control) -> ft.Column:
        return ft.Column(
            spacing=AppSpacing.SM,
            controls=[
                ft.Text(title, weight=ft.FontWeight.BOLD),
                preview,
            ],
        )

    @staticmethod
    def _format_file_size(size: int) -> str:
        value = float(max(0, size))
        units = ("o", "Ko", "Mo", "Go")
        for unit in units:
            if value < 1024 or unit == units[-1]:
                precision = 0 if unit == "o" else 1
                return f"{value:.{precision}f} {unit}"
            value /= 1024
        return "0 o"

    def _safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
