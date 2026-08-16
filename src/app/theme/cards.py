from __future__ import annotations

from enum import Enum
from typing import Callable, Iterable, Optional, Union

import flet as ft

from app.theme.tokens import (
    AppColors,
    AppRadius,
    AppShadows,
    AppSizes,
    AppSpacing,
    AppText,
)
from app.theme.buttons import IconAction
from app.theme.badges import TagBadge


class CardOrientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class CardDensity(str, Enum):
    COMPACT = "compact"
    NORMAL = "normal"
    COMFORTABLE = "comfortable"


class CardVariant(str, Enum):
    DEFAULT = "default"
    DOCUMENT = "document"
    SEARCH = "search"
    RECENT = "recent"
    TRASH = "trash"


class AppCard(ft.Container):
    def __init__(
        self,
        title: Union[str, ft.Control, None] = None,
        subtitle: Union[str, ft.Control, None] = None,
        icon=None,
        icon_color=AppColors.PRIMARY_DARK,
        icon_bgcolor=AppColors.PRIMARY_LIGHT,
        badge: Optional[ft.Control] = None,
        value: Union[str, int, ft.Control, None] = None,
        content: Optional[ft.Control] = None,
        metadata: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
        extension: str = "",
        variant: CardVariant = CardVariant.DEFAULT,
        actions: Optional[Iterable[ft.Control]] = None,
        menu_items: Optional[Iterable[ft.PopupMenuItem]] = None,
        primary_action: Optional[ft.Control] = None,
        on_click: Optional[Callable] = None,
        selected: bool = False,
        selectable: bool = False,
        selection_value: Optional[bool] = None,
        on_selected: Optional[Callable] = None,
        favorite: bool = False,
        status_text: Optional[str] = None,
        status_color=None,
        progress: Optional[float] = None,
        leading: Optional[ft.Control] = None,
        expansion_content: Optional[ft.Control] = None,
        expanded: bool = False,
        on_expansion_change: Optional[Callable] = None,
        disabled: bool = False,
        orientation: Optional[CardOrientation] = None,
        density: CardDensity = CardDensity.NORMAL,
        width: Optional[float] = None,
        height: Optional[float] = None,
        expand: Optional[bool] = None,
        bgcolor=None,
        border_color=None,
        padding=None,
        shadow: bool = True,
        tooltip: str = "",
        **kwargs,
    ):
        self.variant = variant
        self.extension = self._normalize_extension(extension)
        self.selected = bool(selected)
        self.selection_value = self.selected if selection_value is None else bool(selection_value)
        self.on_selected = on_selected
        self.expanded = bool(expanded)
        self.on_expansion_change = on_expansion_change
        self._expansion_icon = None
        self._expansion_divider = None
        self._expansion_body = None

        metadata = [str(item) for item in (metadata or []) if item not in (None, "")]
        tags = [str(tag) for tag in (tags or []) if tag not in (None, "")]
        actions = list(actions or [])
        menu_items = list(menu_items or [])
        if primary_action is not None:
            actions.insert(0, primary_action)
        if menu_items:
            actions.append(
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT_ROUNDED,
                    tooltip="Actions",
                    items=menu_items,
                )
            )
        if expansion_content is not None:
            self._expansion_icon = IconAction(
                icon=(
                    ft.Icons.EXPAND_LESS_ROUNDED
                    if self.expanded
                    else ft.Icons.EXPAND_MORE_ROUNDED
                ),
                tooltip="Replier" if self.expanded else "Déplier",
                compact=True,
                on_click=self._toggle_expansion,
            )
            actions.append(self._expansion_icon)

        resolved_orientation = orientation or (
            CardOrientation.HORIZONTAL
            if variant is not CardVariant.DEFAULT or self.extension
            else CardOrientation.VERTICAL
        )

        spacing = {
            CardDensity.COMPACT: AppSpacing.SM,
            CardDensity.NORMAL: AppSpacing.MD,
            CardDensity.COMFORTABLE: AppSpacing.LG,
        }[density]

        card_padding = padding or {
            CardDensity.COMPACT: AppSpacing.MD,
            CardDensity.NORMAL: AppSpacing.LG,
            CardDensity.COMFORTABLE: AppSpacing.XL,
        }[density]

        resolved_bg = bgcolor or self._resolve_background()
        resolved_border = border_color or (AppColors.PRIMARY_DARK if selected else AppColors.BORDER_LIGHT)

        icon_control = leading
        resolved_icon = icon if icon is not None else self._default_file_icon()
        if icon_control is None and resolved_icon is not None:
            icon_control = ft.Container(
                width=(44 if density != CardDensity.COMPACT else 38),
                height=(44 if density != CardDensity.COMPACT else 38),
                border_radius=AppRadius.PILL,
                bgcolor=(icon_bgcolor if icon is not None else self._default_icon_background()),
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(
                    resolved_icon,
                    size=(AppSizes.ICON_MD if density != CardDensity.COMPACT else AppSizes.ICON_SM),
                    color=(icon_color if icon is not None else self._default_icon_color()),
                ),
            )

        title_control = self._to_text(
            title,
            size=AppText.CARD_TITLE,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT,
            max_lines=1,
        )

        subtitle_control = self._to_text(
            subtitle,
            size=AppText.CAPTION,
            color=AppColors.TEXT_MUTED,
            max_lines=2,
        )

        value_control = None

        if value is not None:
            value_control = (
                value
                if isinstance(value, ft.Control)
                else ft.Text(
                    str(value),
                    size=AppText.CARD_TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT,
                )
            )

        title_row_controls = []

        if title_control is not None:
            title_row_controls.append(ft.Container(content=title_control, expand=True))

        if favorite:
            title_row_controls.append(
                ft.Icon(
                    ft.Icons.STAR_ROUNDED,
                    size=16,
                    color=ft.Colors.AMBER_600,
                    tooltip="Favori",
                )
            )

        if badge is not None:
            title_row_controls.append(badge)

        if value_control is not None:
            title_row_controls.append(value_control)

        text_controls = []

        if title_row_controls:
            text_controls.append(ft.Row(spacing=AppSpacing.SM, controls=title_row_controls))

        if subtitle_control is not None:
            text_controls.append(subtitle_control)

        if metadata:
            text_controls.append(
                ft.Text(
                    "   •   ".join(metadata),
                    size=AppText.CAPTION,
                    color=AppColors.TEXT_MUTED,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )

        if tags and density is not CardDensity.COMPACT:
            text_controls.append(self._build_tags(tags))

        if status_text:
            text_controls.append(
                self._build_status(
                    status_text,
                    status_color or AppColors.TEXT_MUTED,
                    progress,
                )
            )

        if content is not None:
            text_controls.append(content)

        body = ft.Column(
            spacing=AppSpacing.XS,
            controls=text_controls,
            expand=True,
        )

        action_row = (
            ft.Row(
                spacing=AppSpacing.XS,
                alignment=ft.MainAxisAlignment.END,
                controls=actions,
            )
            if actions
            else None
        )

        leading_controls = []
        if selectable:
            leading_controls.append(
                ft.Checkbox(
                    value=self.selection_value,
                    tooltip="Sélectionner",
                    on_change=self._handle_selection_change,
                )
            )
        if icon_control is not None:
            leading_controls.append(icon_control)

        if resolved_orientation == CardOrientation.HORIZONTAL:
            controls = [*leading_controls, body]

            if action_row is not None:
                controls.append(action_row)

            layout: ft.Control = ft.Row(
                spacing=spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
            )

        else:
            controls = [*leading_controls, body]

            if action_row is not None:
                controls.append(action_row)

            layout = ft.Column(
                spacing=spacing,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=controls,
            )

        card_controls = [layout]
        if expansion_content is not None:
            self._expansion_divider = ft.Divider(
                visible=self.expanded,
                height=1,
                color=AppColors.BORDER_LIGHT,
            )
            self._expansion_body = ft.Container(
                visible=self.expanded,
                padding=ft.Padding.only(top=AppSpacing.SM),
                content=expansion_content,
            )
            card_controls.extend([self._expansion_divider, self._expansion_body])

        super().__init__(
            content=ft.Column(spacing=0, controls=card_controls),
            padding=card_padding,
            width=width,
            height=height,
            expand=expand,
            bgcolor=resolved_bg,
            border_radius=AppRadius.LG,
            border=ft.Border.all(2 if selected else 1, resolved_border),
            shadow=(AppShadows.card() if shadow else None),
            on_click=(None if disabled else on_click),
            opacity=(0.55 if disabled else 1),
            tooltip=tooltip,
            ink=(on_click is not None and not disabled),
            **kwargs,
        )

    @staticmethod
    def _build_tags(tags: list[str]) -> ft.Row:
        visible = tags[:5]
        controls: list[ft.Control] = [TagBadge(tag) for tag in visible]
        if len(tags) > len(visible):
            controls.append(
                ft.Text(
                    f"+{len(tags) - len(visible)}",
                    size=11,
                    color=AppColors.TEXT_MUTED,
                )
            )
        return ft.Row(
            wrap=True,
            spacing=AppSpacing.XS,
            run_spacing=AppSpacing.XS,
            controls=controls,
        )

    @staticmethod
    def _build_status(text: str, color, progress: Optional[float]) -> ft.Control:
        label = ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=color)
        if progress is None:
            return label
        return ft.Column(
            tight=True,
            spacing=AppSpacing.XXS,
            controls=[
                label,
                ft.ProgressBar(
                    value=max(0.0, min(1.0, float(progress))),
                    height=5,
                    color=color,
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=3,
                ),
            ],
        )

    def _toggle_expansion(self, _event=None) -> None:
        self.expanded = not self.expanded
        if self._expansion_icon is not None:
            self._expansion_icon.icon = (
                ft.Icons.EXPAND_LESS_ROUNDED
                if self.expanded
                else ft.Icons.EXPAND_MORE_ROUNDED
            )
            self._expansion_icon.tooltip = "Replier" if self.expanded else "Déplier"
        if self._expansion_divider is not None:
            self._expansion_divider.visible = self.expanded
        if self._expansion_body is not None:
            self._expansion_body.visible = self.expanded
        if self.on_expansion_change is not None:
            self.on_expansion_change(self.expanded)
        try:
            self.update()
        except RuntimeError:
            pass

    def _handle_selection_change(self, event) -> None:
        self.selection_value = bool(event.control.value)
        if self.on_selected is not None:
            self.on_selected(self.selection_value)

    def _resolve_background(self):
        if self.selected:
            return AppColors.PRIMARY_SOFT
        if self.variant is CardVariant.TRASH:
            return ft.Colors.RED_50
        return AppColors.SURFACE

    def _default_file_icon(self):
        if not self.extension:
            return None
        if self.extension == ".pdf":
            return ft.Icons.PICTURE_AS_PDF_ROUNDED
        if self.extension in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
            return ft.Icons.IMAGE_OUTLINED
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

    @staticmethod
    def _to_text(value, **kwargs) -> Optional[ft.Control]:
        if value is None or value == "":
            return None

        if isinstance(value, ft.Control):
            return value

        return ft.Text(str(value), **kwargs)


class PageHeader(ft.Container):
    def __init__(
        self,
        title: str,
        subtitle: Union[str, ft.Control, None] = None,
        icon=None,
        actions: Optional[Iterable[ft.Control]] = None,
        on_back: Optional[Callable] = None,
        **kwargs,
    ):
        actions = list(actions or [])

        leading = []

        if on_back is not None:
            leading.append(
                IconAction(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    color=AppColors.TEXT_LIGHT,
                    tooltip="Retour",
                    on_click=on_back,
                )
            )

        if icon is not None:
            leading.append(
                ft.Container(
                    width=52,
                    height=52,
                    alignment=ft.Alignment.CENTER,
                    border_radius=AppRadius.LG,
                    bgcolor=ft.Colors.with_opacity(0.12, AppColors.PRIMARY),
                    content=ft.Icon(icon, size=AppSizes.ICON_LG, color=AppColors.PRIMARY),
                )
            )

        text_controls = [
            ft.Text(
                title,
                size=AppText.PAGE_TITLE,
                weight=ft.FontWeight.BOLD,
                color=AppColors.TEXT_LIGHT,
            )
        ]

        if subtitle:
            text_controls.append(
                subtitle
                if isinstance(subtitle, ft.Control)
                else ft.Text(subtitle, size=AppText.BODY, color=ft.Colors.WHITE_70)
            )

        leading.append(ft.Column(spacing=2, controls=text_controls))

        super().__init__(
            padding=AppSpacing.XL,
            bgcolor=ft.Colors.with_opacity(
                0.95,
                AppColors.PANEL_DARK,
            ),
            border_radius=AppRadius.LG,
            shadow=AppShadows.card(),
            content=ft.Row(
                controls=[
                    ft.Row(spacing=AppSpacing.MD, controls=leading),
                    ft.Container(expand=True),
                    ft.Row(spacing=AppSpacing.SM, controls=actions),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            **kwargs,
        )


class AppSection(ft.Container):
    def __init__(
        self,
        title: str,
        content: ft.Control,
        icon=None,
        actions: Optional[Iterable[ft.Control]] = None,
        expand=None,
        **kwargs,
    ):
        actions = list(actions or [])

        title_controls = []

        if icon is not None:
            title_controls.append(ft.Icon(icon, color=AppColors.PRIMARY, size=AppSizes.ICON_MD))

        title_controls.append(
            ft.Text(
                title,
                color=AppColors.TEXT_LIGHT,
                size=AppText.SECTION_TITLE,
                weight=ft.FontWeight.BOLD,
            )
        )

        super().__init__(
            border_radius=AppRadius.LG,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            expand=expand,
            shadow=AppShadows.card(),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(
                            0.95,
                            AppColors.PANEL_DARK,
                        ),
                        padding=ft.Padding.symmetric(
                            horizontal=AppSpacing.LG,
                            vertical=AppSpacing.MD,
                        ),
                        content=ft.Row(
                            controls=[
                                ft.Row(spacing=AppSpacing.SM, controls=title_controls),
                                ft.Container(expand=True),
                                ft.Row(spacing=AppSpacing.XS, controls=actions),
                            ]
                        ),
                    ),
                    ft.Container(
                        padding=AppSpacing.LG,
                        content=content,
                        expand=True,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.TOP_LEFT,
                            end=ft.Alignment.BOTTOM_RIGHT,
                            colors=[
                                ft.Colors.with_opacity(
                                    0.65,
                                    AppColors.SURFACE,
                                ),
                                ft.Colors.with_opacity(
                                    0.65,
                                    AppColors.SURFACE_ALT,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            **kwargs,
        )
