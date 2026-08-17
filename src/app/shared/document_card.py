from __future__ import annotations

from enum import Enum
from typing import Callable, Iterable

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppSpacing,
)
from app.theme.badges import TagBadge


class DocumentCardVariant(str, Enum):
    """Variantes visuelles disponibles pour une carte de document."""

    COMPACT = "compact"
    STANDARD = "standard"
    SEARCH = "search"
    RECENT = "recent"
    TRASH = "trash"


class DocumentCard(ft.Container):
    """
    Carte visuelle générique pour un document.

    La carte ne contient aucune logique métier. Les actions sont injectées
    par les vues qui l’utilisent.
    """

    def __init__(
        self,
        *,
        title: str,
        extension: str = "",
        subtitle: str = "",
        metadata: Iterable[str] | None = None,
        tags: Iterable[str] | None = None,
        variant: DocumentCardVariant = DocumentCardVariant.STANDARD,
        selected: bool = False,
        selectable: bool = False,
        selection_value: bool | None = None,
        favorite: bool = False,
        leading_icon=None,
        leading_icon_color=None,
        leading_bgcolor=None,
        status_text: str | None = None,
        status_color=None,
        progress: float | None = None,
        primary_action: ft.Control | None = None,
        actions: Iterable[ft.Control] | None = None,
        menu_items: Iterable[ft.PopupMenuItem] | None = None,
        on_click: Callable | None = None,
        on_selected: Callable | None = None,
        tooltip: str = "",
    ):
        self.title_text = str(title or "Document")
        self.extension = self._normalize_extension(extension)
        self.subtitle_text = str(subtitle or "")

        self.metadata = [str(item) for item in (metadata or []) if item not in (None, "")]
        self.tags = [str(tag) for tag in (tags or []) if tag not in (None, "")]

        self.variant = variant
        self.selected = bool(selected)
        self.selectable = bool(selectable)
        self.selection_value = self.selected if selection_value is None else bool(selection_value)
        self.favorite = bool(favorite)

        self.leading_icon = leading_icon if leading_icon is not None else self._default_file_icon()
        self.leading_icon_color = leading_icon_color if leading_icon_color is not None else self._default_icon_color()
        self.leading_bgcolor = leading_bgcolor if leading_bgcolor is not None else self._default_icon_background()

        self.status_text = status_text
        self.status_color = status_color if status_color is not None else AppColors.TEXT_MUTED
        self.progress = progress
        self.primary_action = primary_action
        self.actions = list(actions or [])
        self.menu_items = list(menu_items or [])

        self.on_card_click = on_click
        self.on_selected = on_selected

        compact = self.variant in (DocumentCardVariant.COMPACT, DocumentCardVariant.RECENT)

        super().__init__(
            padding=(AppSpacing.SM if compact else AppSpacing.MD),
            bgcolor=self._resolve_background(),
            border=ft.Border.all(
                2 if self.selected else 1,
                (AppColors.PRIMARY_DARK if self.selected else AppColors.BORDER),
            ),
            border_radius=AppRadius.MD,
            tooltip=tooltip,
            ink=on_click is not None,
            on_click=self._handle_card_click,
            content=self._build_content(),
        )

    def _build_content(self) -> ft.Control:
        if self.variant == DocumentCardVariant.COMPACT:
            return self._build_compact_content()
        if self.variant == DocumentCardVariant.RECENT:
            return self._build_recent_content()
        return self._build_standard_content()

    def _build_compact_content(self) -> ft.Row:
        controls: list[ft.Control] = []
        if self.selectable:
            controls.append(self._build_selection_control())

        controls.extend([
            self._build_file_icon(size=40, icon_size=21),
            self._build_information(compact=True),
        ])

        actions = self._build_actions()
        if actions is not None:
            controls.append(actions)

        return ft.Row(
            spacing=AppSpacing.SM,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        )

    def _build_recent_content(self) -> ft.Row:
        controls: list[ft.Control] = [
            self._build_file_icon(size=42, icon_size=22),
            self._build_information(compact=True),
        ]

        actions = self._build_actions()
        if actions is not None:
            controls.append(actions)

        return ft.Row(
            spacing=AppSpacing.SM,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        )

    def _build_standard_content(self) -> ft.Row:
        controls: list[ft.Control] = []
        if self.selectable:
            controls.append(self._build_selection_control())

        controls.extend([
            self._build_file_icon(size=48, icon_size=25),
            self._build_information(compact=False),
        ])

        actions = self._build_actions()
        if actions is not None:
            controls.append(actions)

        return ft.Row(
            spacing=AppSpacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        )

    def _build_selection_control(self) -> ft.Checkbox:
        return ft.Checkbox(
            value=self.selection_value,
            tooltip="Sélectionner ce document",
            on_change=self._handle_selection_change,
        )

    def _build_file_icon(self, *, size: int, icon_size: int) -> ft.Container:
        return ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment.CENTER,
            border_radius=AppRadius.MD,
            bgcolor=self.leading_bgcolor,
            content=ft.Icon(self.leading_icon, size=icon_size, color=self.leading_icon_color),
        )

    def _build_information(self, *, compact: bool) -> ft.Column:
        controls: list[ft.Control] = [self._build_title_row(compact=compact)]
        subtitle = self._build_subtitle()

        if subtitle:
            controls.append(
                ft.Text(
                    subtitle,
                    size=11 if compact else 12,
                    color=AppColors.TEXT_MUTED,
                    max_lines=1 if compact else 2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        if self.tags and not compact:
            controls.append(self._build_tags())
        if self.status_text:
            controls.append(self._build_status())

        return ft.Column(
            expand=True,
            tight=True,
            spacing=(AppSpacing.XXS if compact else AppSpacing.XS),
            controls=controls,
        )

    def _build_title_row(self, *, compact: bool) -> ft.Row:
        controls: list[ft.Control] = [
            ft.Text(
                self.title_text,
                expand=True,
                size=13 if compact else 14,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_MAIN,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        ]

        if self.favorite:
            controls.append(
                ft.Icon(ft.Icons.STAR_ROUNDED, size=16, color=ft.Colors.AMBER_600, tooltip="Document favori")
            )

        return ft.Row(
            spacing=AppSpacing.XS,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        )

    def _build_subtitle(self) -> str:
        parts: list[str] = []
        if self.subtitle_text:
            parts.append(self.subtitle_text)
        parts.extend(self.metadata)
        return "   •   ".join(parts)

    def _build_tags(self) -> ft.Row:
        visible_tags = self.tags[:5]
        controls: list[ft.Control] = [TagBadge(tag) for tag in visible_tags]
        remaining = len(self.tags) - len(visible_tags)

        if remaining > 0:
            controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=AppSpacing.SM, vertical=AppSpacing.XXS),
                    bgcolor=AppColors.SURFACE_ALT,
                    border=ft.Border.all(1, AppColors.BORDER_LIGHT),
                    border_radius=AppRadius.PILL,
                    content=ft.Text(f"+{remaining}", size=11, weight=ft.FontWeight.W_600, color=AppColors.TEXT_MUTED),
                )
            )

        return ft.Row(wrap=True, spacing=AppSpacing.XS, run_spacing=AppSpacing.XS, controls=controls)

    def _build_status(self) -> ft.Control:
        if self.progress is None:
            return ft.Text(self.status_text or "", size=11, weight=ft.FontWeight.W_600, color=self.status_color)

        progress_value = max(0.0, min(1.0, float(self.progress)))

        return ft.Column(
            tight=True,
            spacing=AppSpacing.XXS,
            controls=[
                ft.Text(self.status_text or "", size=11, weight=ft.FontWeight.W_600, color=self.status_color),
                ft.ProgressBar(
                    value=progress_value,
                    height=5,
                    color=self.status_color,
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=3,
                ),
            ],
        )

    def _build_actions(self) -> ft.Row | None:
        controls: list[ft.Control] = []
        if self.primary_action is not None:
            controls.append(self.primary_action)

        controls.extend(self.actions)

        if self.menu_items:
            controls.append(
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT_ROUNDED,
                    tooltip="Actions du document",
                    items=self.menu_items,
                )
            )

        if not controls:
            return None

        return ft.Row(tight=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=controls)

    def _handle_card_click(self, event) -> None:
        if self.on_card_click is not None:
            self.on_card_click(event)

    def _handle_selection_change(self, event) -> None:
        self.selection_value = bool(event.control.value)
        if self.on_selected is not None:
            self.on_selected(self.selection_value)

    def _resolve_background(self):
        if self.selected:
            return AppColors.PRIMARY_LIGHT
        if self.variant == DocumentCardVariant.TRASH:
            return ft.Colors.RED_50
        return AppColors.CARD_BG

    def _default_file_icon(self):
        if self.extension == ".pdf":
            return ft.Icons.PICTURE_AS_PDF_ROUNDED
        if self.extension in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            return ft.Icons.IMAGE_OUTLINED
        if self.extension in (".doc", ".docx", ".odt"):
            return ft.Icons.DESCRIPTION_OUTLINED
        if self.extension in (".xls", ".xlsx", ".ods", ".csv"):
            return ft.Icons.TABLE_CHART_OUTLINED
        if self.extension in (".zip", ".rar", ".7z"):
            return ft.Icons.FOLDER_ZIP_OUTLINED
        return ft.Icons.INSERT_DRIVE_FILE_ROUNDED

    def _default_icon_color(self):
        if self.extension == ".pdf":
            return ft.Colors.RED_500
        if self.extension in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            return ft.Colors.PURPLE_500
        if self.extension in (".xls", ".xlsx", ".ods", ".csv"):
            return ft.Colors.GREEN_700
        if self.extension in (".zip", ".rar", ".7z"):
            return ft.Colors.ORANGE_700
        return AppColors.SECONDARY

    def _default_icon_background(self):
        if self.extension == ".pdf":
            return ft.Colors.RED_50
        if self.extension in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            return ft.Colors.PURPLE_50
        if self.extension in (".xls", ".xlsx", ".ods", ".csv"):
            return ft.Colors.GREEN_50
        if self.extension in (".zip", ".rar", ".7z"):
            return ft.Colors.ORANGE_50
        return ft.Colors.BLUE_50

    @staticmethod
    def _normalize_extension(extension: str) -> str:
        value = str(extension or "").strip().casefold()
        if value and not value.startswith("."):
            return f".{value}"
        return value