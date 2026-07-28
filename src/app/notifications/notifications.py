import flet as ft

from app.notifications.manager import NotificationManager


def notifications(page: ft.Page) -> NotificationManager:
    return NotificationManager(page)
