from __future__ import annotations

import flet as ft


class AppColors:
    """Palette unique de PaperNest."""

    PRIMARY = ft.Colors.YELLOW_700
    PRIMARY_DARK = ft.Colors.YELLOW_800
    PRIMARY_LIGHT = ft.Colors.YELLOW_300
    PRIMARY_SOFT = ft.Colors.YELLOW_50

    SUCCESS = ft.Colors.GREEN_700
    SUCCESS_DARK = ft.Colors.GREEN_800
    SUCCESS_LIGHT = ft.Colors.GREEN_100
    SUCCESS_SOFT = ft.Colors.GREEN_50

    ERROR = ft.Colors.RED_700
    ERROR_DARK = ft.Colors.RED_800
    ERROR_LIGHT = ft.Colors.RED_100
    ERROR_SOFT = ft.Colors.RED_50

    WARNING = ft.Colors.ORANGE_700
    WARNING_DARK = ft.Colors.ORANGE_800
    WARNING_LIGHT = ft.Colors.ORANGE_100
    WARNING_SOFT = ft.Colors.ORANGE_50

    INFO = ft.Colors.BLUE_700
    INFO_DARK = ft.Colors.BLUE_800
    INFO_LIGHT = ft.Colors.BLUE_100

    BACKGROUND = ft.Colors.GREY_100
    SURFACE = ft.Colors.WHITE
    SURFACE_ALT = ft.Colors.GREY_200

    PANEL = ft.Colors.GREY_300
    PANEL_STRONG = ft.Colors.GREY_400
    PANEL_DARK = ft.Colors.GREY_900
    PANEL_DARK_SOFT = ft.Colors.GREY_800

    TEXT = ft.Colors.GREY_900
    TEXT_LIGHT = ft.Colors.WHITE
    TEXT_SECONDARY = ft.Colors.GREY_700
    TEXT_MUTED = ft.Colors.GREY_600

    DISABLED = ft.Colors.GREY_500
    DISABLED_BG = ft.Colors.GREY_200

    BORDER = ft.Colors.GREY_400
    BORDER_LIGHT = ft.Colors.GREY_300
    DIVIDER = ft.Colors.GREY_300

    FAVORITE = ft.Colors.RED_500
    PHOTO = ft.Colors.BLUE_700

    # Alias temporaires pour les écrans pas encore migrés.
    SECONDARY = PRIMARY
    CARD_BG = SURFACE
    TEXT_MAIN = TEXT
    SUBTITLE = TEXT_SECONDARY

    SHOPPING_PENDING = PRIMARY
    SHOPPING_DONE = SUCCESS

    SERVER_ONLINE = SUCCESS
    SERVER_OFFLINE = ERROR
    SERVER_UNKNOWN = ft.Colors.GREY_600


class AppSpacing:
    XXS = 4
    XS = 6
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32


class AppRadius:
    XS = 6
    SM = 8
    MD = 10
    LG = 12
    XL = 16
    PILL = 999


class AppSizes:
    BUTTON_HEIGHT = 44
    BUTTON_HEIGHT_COMPACT = 36

    FIELD_HEIGHT = 48
    FIELD_HEIGHT_COMPACT = 40

    ICON_SM = 18
    ICON_MD = 22
    ICON_LG = 28

    PAGE_ICON = 46

    SIDEBAR_WIDTH = 240
    SIDEBAR_COMPACT_WIDTH = 76

    DIALOG_WIDTH = 520


class AppText:
    PAGE_TITLE = 28
    SECTION_TITLE = 20
    CARD_TITLE = 15
    BODY = 14
    CAPTION = 12


class AppShadows:
    @staticmethod
    def card() -> ft.BoxShadow:
        return ft.BoxShadow(
            blur_radius=16,
            spread_radius=0,
            color=ft.Colors.with_opacity(
                0.25,
                ft.Colors.BLACK,
            ),
            offset=ft.Offset(0, 0),
        )

    @staticmethod
    def floating() -> ft.BoxShadow:
        return ft.BoxShadow(
            blur_radius=24,
            spread_radius=0,
            color=ft.Colors.with_opacity(
                0.14,
                ft.Colors.BLACK,
            ),
            offset=ft.Offset(0, 8),
        )


class AppTheme:
    """Fabriques communes utilisées par les composants UI."""

    @staticmethod
    def button_shape(
        radius: int = AppRadius.MD,
    ) -> ft.RoundedRectangleBorder:
        return ft.RoundedRectangleBorder(
            radius=radius,
        )

    @staticmethod
    def button_gradient(
        color: str,
        dark_color: str,
    ) -> ft.LinearGradient:
        """Construit le gradient standard des boutons PaperNest."""
        return ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[color, dark_color],
        )

    @staticmethod
    def input_border_color() -> str:
        return AppColors.BORDER

    @staticmethod
    def input_focus_color() -> str:
        return AppColors.PRIMARY_DARK
