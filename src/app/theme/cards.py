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


class CardOrientation(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class CardDensity(str, Enum):
    COMPACT = "compact"
    NORMAL = "normal"
    COMFORTABLE = "comfortable"


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
        actions: Optional[Iterable[ft.Control]] = None,
        on_click: Optional[Callable] = None,
        selected: bool = False,
        disabled: bool = False,
        orientation: CardOrientation = CardOrientation.VERTICAL,
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
        actions = list(actions or [])

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

        resolved_bg = bgcolor or (AppColors.PRIMARY_SOFT if selected else AppColors.SURFACE)
        resolved_border = border_color or (AppColors.PRIMARY_DARK if selected else AppColors.BORDER_LIGHT)

        icon_control = None

        if icon is not None:
            icon_control = ft.Container(
                width=(44 if density != CardDensity.COMPACT else 38),
                height=(44 if density != CardDensity.COMPACT else 38),
                border_radius=AppRadius.PILL,
                bgcolor=icon_bgcolor,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(
                    icon,
                    size=(AppSizes.ICON_MD if density != CardDensity.COMPACT else AppSizes.ICON_SM),
                    color=icon_color,
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

        if badge is not None:
            title_row_controls.append(badge)

        if value_control is not None:
            title_row_controls.append(value_control)

        text_controls = []

        if title_row_controls:
            text_controls.append(ft.Row(spacing=AppSpacing.SM, controls=title_row_controls))

        if subtitle_control is not None:
            text_controls.append(subtitle_control)

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

        if orientation == CardOrientation.HORIZONTAL:
            controls = []

            if icon_control is not None:
                controls.append(icon_control)

            controls.append(body)

            if action_row is not None:
                controls.append(action_row)

            layout: ft.Control = ft.Row(
                spacing=spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controls,
            )

        else:
            controls = []

            if icon_control is not None:
                controls.append(icon_control)

            controls.append(body)

            if action_row is not None:
                controls.append(action_row)

            layout = ft.Column(
                spacing=spacing,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=controls,
            )

        super().__init__(
            content=layout,
            padding=card_padding,
            width=width,
            height=height,
            expand=expand,
            bgcolor=resolved_bg,
            border_radius=AppRadius.LG,
            border=ft.Border.all(1, resolved_border),
            shadow=(AppShadows.card() if shadow else None),
            on_click=(None if disabled else on_click),
            opacity=(0.55 if disabled else 1),
            tooltip=tooltip,
            ink=(on_click is not None and not disabled),
            **kwargs,
        )

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
            bgcolor=AppColors.PANEL_DARK,
            border_radius=AppRadius.LG,
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
            border=ft.Border.all(1, AppColors.BORDER_LIGHT),
            bgcolor=AppColors.SURFACE,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            expand=expand,
            shadow=AppShadows.card(),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        bgcolor=AppColors.PANEL_DARK,
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
                        bgcolor=AppColors.SURFACE,
                    ),
                ],
            ),
            **kwargs,
        )


# Compatibilité avec les vues existantes.
class HeaderCard(PageHeader):
    pass


class Section(AppSection):
    pass


class CabinetCard(AppCard):
    def __init__(self, label: str, value, icon, color, bgcolor, on_click=None):
        super().__init__(
            title=label,
            subtitle=f"{value} élément(s)",
            icon=icon,
            icon_color=(color or AppColors.PRIMARY_DARK),
            icon_bgcolor=bgcolor,
            on_click=on_click,
            orientation=CardOrientation.VERTICAL,
        )


class CategoryCard(AppCard):
    def __init__(self, label: str, icon, color, bgcolor, on_open=None, on_edit=None, on_delete=None):
        super().__init__(
            title=label,
            icon=icon,
            icon_color=(color or AppColors.PRIMARY_DARK),
            icon_bgcolor=bgcolor,
            actions=[
                IconAction(
                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                    color=AppColors.PRIMARY_DARK,
                    tooltip="Ouvrir le dossier",
                    on_click=on_open,
                    compact=True,
                ),
                IconAction(
                    icon=ft.Icons.EDIT_ROUNDED,
                    color=AppColors.TEXT_MUTED,
                    tooltip="Modifier / Renommer",
                    on_click=on_edit,
                    compact=True,
                ),
                IconAction(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    color=AppColors.ERROR,
                    tooltip="Supprimer",
                    on_click=on_delete,
                    compact=True,
                ),
            ],
            orientation=CardOrientation.VERTICAL,
            density=CardDensity.COMPACT,
        )