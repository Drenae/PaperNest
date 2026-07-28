from enum import Enum

import flet as ft


class NotificationType(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def success(self, message: str) -> None:
        self.show(message, NotificationType.SUCCESS, duration=3500)

    def error(self, message: str) -> None:
        self.show(message, NotificationType.ERROR, duration=6000)

    def warning(self, message: str) -> None:
        self.show(message, NotificationType.WARNING, duration=5000)

    def info(self, message: str) -> None:
        self.show(message, NotificationType.INFO, duration=3500)

    def show(
        self,
        message: str,
        notification_type: NotificationType,
        *,
        duration: int,
    ) -> None:
        icon, background = self.get_style(notification_type)

        self.close_existing_notifications()

        snack_bar = ft.SnackBar(
            behavior=ft.SnackBarBehavior.FLOATING,
            show_close_icon=True,
            duration=duration,
            bgcolor=background,
            margin=20,
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(icon, color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE, expand=True),
                ],
            ),
        )

        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

    def close_existing_notifications(self) -> None:
        for control in list(self.page.overlay):
            if not isinstance(control, ft.SnackBar):
                continue

            control.open = False
            try:
                self.page.overlay.remove(control)
            except ValueError:
                pass

    @staticmethod
    def get_style(notification_type: NotificationType):
        styles = {
            NotificationType.SUCCESS: (
                ft.Icons.CHECK_CIRCLE_ROUNDED,
                ft.Colors.GREEN_700,
            ),
            NotificationType.ERROR: (
                ft.Icons.ERROR_ROUNDED,
                ft.Colors.RED_700,
            ),
            NotificationType.WARNING: (
                ft.Icons.WARNING_ROUNDED,
                ft.Colors.ORANGE_700,
            ),
            NotificationType.INFO: (
                ft.Icons.INFO_ROUNDED,
                ft.Colors.BLUE_700,
            ),
        }
        return styles[notification_type]
