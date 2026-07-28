from __future__ import annotations

import flet as ft

from app.theme.empty_state import (
    EmptyState,
    EmptyStateVariant,
    LoadingState,
)


class StateView(EmptyState):
    """Alias de compatibilité avec les anciennes vues.

    Les nouveaux écrans devront importer directement ``EmptyState`` ou
    ``LoadingState``.
    """

    def __init__(
        self,
        *,
        icon,
        title: str,
        message: str = "",
        icon_color=None,
        action_text: str | None = None,
        on_action=None,
        padding: int = 40,
    ):
        variant = (
            EmptyStateVariant.ERROR
            if icon_color == ft.Colors.RED_600
            else EmptyStateVariant.NEUTRAL
        )

        super().__init__(
            icon=icon,
            title=title,
            message=message,
            variant=variant,
            action_text=action_text,
            action_icon=ft.Icons.REFRESH_ROUNDED,
            on_action=on_action,
            padding=padding,
        )

        if icon_color is not None:
            icon_container = self.content.controls[0]

            if isinstance(icon_container, ft.Container):
                icon = icon_container.content

                if isinstance(icon, ft.Icon):
                    icon.color = icon_color

    @classmethod
    def empty(
        cls,
        title: str,
        message: str = "",
        *,
        icon=ft.Icons.INBOX_OUTLINED,
        action_text: str | None = None,
        on_action=None,
    ) -> "StateView":
        return cls(
            icon=icon,
            title=title,
            message=message,
            action_text=action_text,
            on_action=on_action,
        )

    @classmethod
    def error(
        cls,
        message: str,
        *,
        title: str = "Une erreur est survenue",
        action_text: str | None = None,
        on_action=None,
    ) -> "StateView":
        return cls(
            icon=ft.Icons.ERROR_OUTLINE_ROUNDED,
            icon_color=ft.Colors.RED_600,
            title=title,
            message=message,
            action_text=action_text,
            on_action=on_action,
        )

    @classmethod
    def loading(
        cls,
        message: str = "Chargement en cours...",
    ) -> ft.Container:
        return LoadingState(
            message=message,
        )