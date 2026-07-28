import asyncio
import logging
from pathlib import Path

import flet as ft

from app.notifications import notifications
from app.preview.builder import PreviewBuilder
from app.preview.components.preview_placeholder import PreviewPlaceholder
from app.preview.controller import PreviewController
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors, AppRadius, AppSpacing
from services.files.archive import ArchiveFileService
from services.preview.image import (
    ImagePreviewError,
    image_preview_service,
)
from services.preview.pdf import (
    PdfPreviewError,
    pdf_preview_service,
)

logger = logging.getLogger(__name__)


class PreviewPanel(ft.Container):
    MIN_VISUAL_SCALE = 0.5
    MAX_VISUAL_SCALE = 10.0
    ZOOM_FACTOR = 1.4
    PDF_RENDER_SCALE = 2.0

    def __init__(
        self,
        page: ft.Page,
        controller: PreviewController,
        on_close=None,
        on_toggle_layout=None,
        on_previous_document=None,
        on_next_document=None,
    ):
        self.app_page = page
        self.controller = controller
        self.on_close = on_close
        self.on_toggle_layout = on_toggle_layout
        self.on_previous_document = on_previous_document
        self.on_next_document = on_next_document

        self.render_generation = 0
        self.page_index = 0
        self.page_count = 0
        self.rotation = 0
        self.preview_type = ""
        self.full_width = False
        self.visual_scale = 1.0
        self.image_viewer: ft.InteractiveViewer | None = None

        self.title_text = ft.Text(
            "Aperçu",
            expand=True,
            size=16,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_MAIN,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.information_text = ft.Text(
            "",
            size=11,
            color=AppColors.TEXT_MUTED,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.previous_document_button = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
            tooltip="Document précédent",
            disabled=True,
            on_click=self.previous_document,
        )

        self.next_document_button = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT_ROUNDED,
            tooltip="Document suivant",
            disabled=True,
            on_click=self.next_document,
        )

        self.layout_button = ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            tooltip="Agrandir l’aperçu",
            on_click=self.toggle_layout,
        )

        self.page_text = ft.Text(
            "",
            size=12,
            weight=ft.FontWeight.W_600,
            color=AppColors.TEXT_MUTED,
        )

        self.zoom_text = ft.Text(
            "100 %",
            size=11,
            color=AppColors.TEXT_MUTED,
        )

        self.previous_page_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
            tooltip="Page précédente",
            disabled=True,
            on_click=self.previous_page,
        )

        self.next_page_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
            tooltip="Page suivante",
            disabled=True,
            on_click=self.next_page,
        )

        self.zoom_out_button = ft.IconButton(
            icon=ft.Icons.REMOVE_ROUNDED,
            tooltip="Réduire",
            disabled=True,
            on_click=self.zoom_out,
        )

        self.zoom_in_button = ft.IconButton(
            icon=ft.Icons.ADD_ROUNDED,
            tooltip="Agrandir",
            disabled=True,
            on_click=self.zoom_in,
        )

        self.reset_zoom_button = ft.IconButton(
            icon=ft.Icons.FIT_SCREEN_ROUNDED,
            tooltip="Taille normale",
            disabled=True,
            on_click=self.reset_zoom,
        )

        self.rotate_button = ft.IconButton(
            icon=ft.Icons.ROTATE_RIGHT_ROUNDED,
            tooltip="Faire pivoter",
            disabled=True,
            on_click=self.rotate,
        )

        self.preview_toolbar = ft.Row(
            visible=False,
            spacing=2,
            wrap=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.previous_page_button,
                self.page_text,
                self.next_page_button,
                ft.VerticalDivider(width=12),
                self.zoom_out_button,
                self.zoom_in_button,
                self.reset_zoom_button,
                self.zoom_text,
                self.rotate_button,
            ],
        )

        self.body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            padding=AppSpacing.SM,
            bgcolor=ft.Colors.GREY_100,
            border=ft.Border.all(1, AppColors.BORDER_LIGHT),
            border_radius=AppRadius.LG,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=PreviewPlaceholder(),
        )

        super().__init__(
            expand=6,
            visible=False,
            padding=AppSpacing.MD,
            bgcolor=AppColors.CARD_BG,
            border=ft.Border.all(
                1,
                AppColors.BORDER,
            ),
            border_radius=AppRadius.XL,
            content=ft.Column(
                expand=True,
                spacing=AppSpacing.SM,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.VISIBILITY_ROUNDED,
                                color=AppColors.SECONDARY,
                            ),
                            self.title_text,
                            self.previous_document_button,
                            self.next_document_button,
                            self.layout_button,
                            ft.IconButton(
                                icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                tooltip="Ouvrir le dossier",
                                on_click=self.open_parent_folder,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW_ROUNDED,
                                tooltip="Ouvrir dans Windows",
                                on_click=self.open_document,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                tooltip="Fermer l’aperçu",
                                on_click=self.close,
                            ),
                        ],
                    ),
                    self.information_text,
                    self.preview_toolbar,
                    ft.Divider(
                        height=1,
                        color=AppColors.BORDER,
                    ),
                    self.body,
                ],
            ),
        )

    def show_document(self) -> None:
        state = self.controller.state
        self.render_generation += 1

        if state.file_path is None:
            self.clear()
            return

        self.visible = True
        self.title_text.value = state.title
        self.page_index = 0
        self.page_count = 0
        self.rotation = 0
        self.preview_type = ""
        self.visual_scale = 1.0
        self.image_viewer = None
        self.preview_toolbar.visible = False

        information_parts = []

        if state.category_name:
            information_parts.append(
                f"Classeur : {state.category_name}"
            )

        if state.file_size:
            information_parts.append(
                f"Taille : {state.file_size}"
            )

        if state.extension:
            information_parts.append(
                state.extension.upper().lstrip(".")
            )

        self.information_text.value = (
            "   •   ".join(information_parts)
        )

        if not state.file_path.exists():
            self.body.content = PreviewBuilder.build_error(
                "Le fichier n’existe plus sur le disque."
            )
            self.update_zoom_buttons()
            return

        generation = self.render_generation

        if state.extension == ".pdf":
            self.preview_type = "pdf"
            self.preview_toolbar.visible = True
            self.body.content = PreviewBuilder.build_loading(
                "Génération de l’aperçu PDF..."
            )

            self.update_toolbar()

            self.app_page.run_task(
                self.load_pdf,
                state.file_path,
                generation,
            )
            return

        if image_preview_service.is_supported(
            state.file_path
        ):
            self.preview_type = "image"
            self.preview_toolbar.visible = True
            self.body.content = PreviewBuilder.build_loading(
                "Génération de l’aperçu de l’image..."
            )

            self.update_toolbar()

            self.app_page.run_task(
                self.load_image,
                state.file_path,
                generation,
            )
            return

        self.preview_type = "unsupported"

        self.body.content = PreviewBuilder.build_unsupported_preview(
            state.file_path,
            state.extension,
        )

        self.update_toolbar()

    async def load_pdf(
        self,
        file_path: Path,
        generation: int,
    ) -> None:
        try:
            page_count = await asyncio.to_thread(
                pdf_preview_service.get_page_count,
                file_path,
            )

            image_base64 = await asyncio.to_thread(
                pdf_preview_service.render_page_base64,
                file_path,
                self.page_index,
                self.PDF_RENDER_SCALE,
                self.rotation,
            )

            if generation != self.render_generation:
                return

            self.page_count = page_count
            self.visual_scale = 1.0

            self.body.content, self.image_viewer = PreviewBuilder.build_preview_image(
                image_base64,
                min_scale=self.MIN_VISUAL_SCALE,
                max_scale=self.MAX_VISUAL_SCALE,
            )
            self.update_zoom_buttons(update_control=False)

            self.update_toolbar()
            self.safe_update()

        except PdfPreviewError as error:
            if generation != self.render_generation:
                return

            self.body.content = PreviewBuilder.build_error(
                str(error)
            )

            self.preview_toolbar.visible = False
            self.image_viewer = None
            self.update_zoom_buttons()
            self.safe_update()

        except Exception:
            logger.exception(
                "Erreur inattendue pendant l’aperçu PDF : %s",
                file_path,
            )

            if generation != self.render_generation:
                return

            self.body.content = PreviewBuilder.build_error(
                "Impossible d’afficher l’aperçu du PDF."
            )

            self.preview_toolbar.visible = False
            self.image_viewer = None
            self.update_zoom_buttons()
            self.safe_update()

    async def load_image(
        self,
        file_path: Path,
        generation: int,
    ) -> None:
        try:
            image_base64 = await asyncio.to_thread(
                image_preview_service.render_base64,
                file_path,
                self.rotation,
            )

            if generation != self.render_generation:
                return

            self.page_count = 1
            self.page_index = 0
            self.visual_scale = 1.0

            self.body.content, self.image_viewer = PreviewBuilder.build_preview_image(
                image_base64,
                min_scale=self.MIN_VISUAL_SCALE,
                max_scale=self.MAX_VISUAL_SCALE,
            )
            self.update_zoom_buttons(update_control=False)

            self.update_toolbar()
            self.safe_update()

        except ImagePreviewError as error:
            if generation != self.render_generation:
                return

            self.body.content = PreviewBuilder.build_error(
                str(error)
            )

            self.preview_toolbar.visible = False
            self.image_viewer = None
            self.update_zoom_buttons()
            self.safe_update()

        except Exception:
            logger.exception(
                "Erreur inattendue pendant l’aperçu image : %s",
                file_path,
            )

            if generation != self.render_generation:
                return

            self.body.content = PreviewBuilder.build_error(
                "Impossible d’afficher l’aperçu de l’image."
            )

            self.preview_toolbar.visible = False
            self.image_viewer = None
            self.update_zoom_buttons()
            self.safe_update()

    def refresh_rendered_preview(self) -> None:
        state = self.controller.state

        if state.file_path is None:
            return

        if self.preview_type not in {
            "pdf",
            "image",
        }:
            return

        self.render_generation += 1
        generation = self.render_generation

        self.image_viewer = None
        self.visual_scale = 1.0
        self.body.content = PreviewBuilder.build_loading()
        self.update_zoom_buttons()
        self.safe_update()

        if self.preview_type == "pdf":
            self.app_page.run_task(
                self.load_pdf,
                state.file_path,
                generation,
            )

        else:
            self.app_page.run_task(
                self.load_image,
                state.file_path,
                generation,
            )

    def previous_page(self, event=None) -> None:
        if self.preview_type != "pdf":
            return

        if self.page_index <= 0:
            return

        self.page_index -= 1
        self.refresh_rendered_preview()

    def next_page(self, event=None) -> None:
        if self.preview_type != "pdf":
            return

        if self.page_index >= self.page_count - 1:
            return

        self.page_index += 1
        self.refresh_rendered_preview()

    async def zoom_in(self, event=None) -> None:
        if self.image_viewer is None:
            return

        if self.visual_scale >= self.MAX_VISUAL_SCALE:
            return

        await self.image_viewer.zoom(
            self.ZOOM_FACTOR
        )

        self.visual_scale = min(
            self.visual_scale * self.ZOOM_FACTOR,
            self.MAX_VISUAL_SCALE,
        )

        self.update_zoom_buttons()

    async def zoom_out(self, event=None) -> None:
        if self.image_viewer is None:
            return

        if self.visual_scale <= self.MIN_VISUAL_SCALE:
            return

        await self.image_viewer.zoom(
            1 / self.ZOOM_FACTOR
        )

        self.visual_scale = max(
            self.visual_scale / self.ZOOM_FACTOR,
            self.MIN_VISUAL_SCALE,
        )

        self.update_zoom_buttons()

    async def reset_zoom(self, event=None) -> None:
        if self.image_viewer is None:
            return

        await self.image_viewer.reset()

        self.visual_scale = 1.0
        self.update_zoom_buttons()

    def rotate(self, event=None) -> None:
        if self.preview_type not in {
            "pdf",
            "image",
        }:
            return

        self.rotation = (
            self.rotation + 90
        ) % 360

        self.refresh_rendered_preview()

    def update_toolbar(self) -> None:
        is_pdf = self.preview_type == "pdf"
        is_previewable = self.preview_type in {
            "pdf",
            "image",
        }

        self.page_text.visible = is_pdf
        self.previous_page_button.visible = is_pdf
        self.next_page_button.visible = is_pdf

        self.page_text.value = (
            f"Page {self.page_index + 1} / {self.page_count}"
            if is_pdf and self.page_count > 0
            else ""
        )

        self.previous_page_button.disabled = (
            not is_pdf
            or self.page_index <= 0
        )

        self.next_page_button.disabled = (
            not is_pdf
            or self.page_count <= 0
            or self.page_index >= self.page_count - 1
        )

        self.zoom_out_button.visible = is_previewable
        self.zoom_in_button.visible = is_previewable
        self.reset_zoom_button.visible = is_previewable
        self.rotate_button.visible = is_previewable

        self.rotate_button.disabled = (
            not is_previewable
        )

        self.zoom_text.value = f"{int(self.visual_scale * 100)} %"

        self.update_zoom_buttons(
            update_control=False
        )

    def update_zoom_buttons(
        self,
        *,
        update_control: bool = True,
    ) -> None:
        viewer_available = (
            self.image_viewer is not None
        )

        self.zoom_out_button.disabled = (
            not viewer_available
            or self.visual_scale
            <= self.MIN_VISUAL_SCALE
        )

        self.zoom_in_button.disabled = (
            not viewer_available
            or self.visual_scale
            >= self.MAX_VISUAL_SCALE
        )

        self.reset_zoom_button.disabled = (
            not viewer_available
            or abs(
                self.visual_scale - 1.0
            ) < 0.01
        )

        self.zoom_text.value = f"{int(self.visual_scale * 100)} %"

        if update_control:
            self.safe_update()

    def previous_document(self, event=None) -> None:
        if self.previous_document_button.disabled:
            return

        if self.on_previous_document:
            self.on_previous_document()

    def next_document(self, event=None) -> None:
        if self.next_document_button.disabled:
            return

        if self.on_next_document:
            self.on_next_document()

    def set_document_navigation(
        self,
        *,
        has_previous: bool,
        has_next: bool,
    ) -> None:
        self.previous_document_button.disabled = (
            not has_previous
        )

        self.next_document_button.disabled = (
            not has_next
        )

    def set_full_width(
        self,
        full_width: bool,
    ) -> None:
        self.full_width = full_width

        self.layout_button.icon = (
            ft.Icons.FULLSCREEN_EXIT_ROUNDED
            if full_width
            else ft.Icons.FULLSCREEN_ROUNDED
        )

        self.layout_button.tooltip = (
            "Réafficher la liste"
            if full_width
            else "Agrandir l’aperçu"
        )

    def toggle_layout(self, event=None) -> None:
        if self.on_toggle_layout:
            self.on_toggle_layout()

    def clear(self) -> None:
        self.render_generation += 1
        self.controller.clear()
        self.visible = False
        self.title_text.value = "Aperçu"
        self.information_text.value = ""
        self.preview_toolbar.visible = False
        self.preview_type = ""
        self.page_index = 0
        self.page_count = 0
        self.rotation = 0
        self.visual_scale = 1.0
        self.image_viewer = None
        self.body.content = PreviewPlaceholder()

        self.set_document_navigation(
            has_previous=False,
            has_next=False,
        )

        self.update_zoom_buttons(
            update_control=False
        )

    def close(self, event=None) -> None:
        self.clear()

        if self.on_close:
            self.on_close()

    def open_document(self, event=None) -> None:
        file_path = self.controller.state.file_path

        if file_path is None:
            return

        try:
            ArchiveFileService.execute_native_file_open(
                str(file_path)
            )

        except PaperNestError as error:
            notifications(self.app_page).error(
                str(error)
            )

    def open_parent_folder(self, event=None) -> None:
        file_path = self.controller.state.file_path

        if file_path is None:
            return

        try:
            ArchiveFileService.execute_native_file_open(
                str(file_path.parent)
            )

        except PaperNestError as error:
            notifications(self.app_page).error(
                str(error)
            )

    def safe_update(self) -> None:
        try:
            self.update()

        except RuntimeError:
            pass