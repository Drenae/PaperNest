import logging

import flet as ft

from app.main_window import MainWindow
from core.application.application import application
from core.config.logging import configure_logging, get_current_log_path
from core.scheduling.scheduler import task_scheduler
from services.files.archive import ArchiveFileService
from services.settings import background_service
from services.trash.service import TrashService
from utils.compatibility import check_python_version

logger = logging.getLogger(__name__)


def main(page: ft.Page) -> None:
    check_python_version()
    configure_logging()

    page.title = "PaperNest - Gestion Documentaire Locale"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.window.maximized = True

    try:
        application.start()
        ArchiveFileService.initialize_storage_tree()
        background_service.apply(page)
        task_scheduler.submit(
            TrashService.purge_expired,
            label="Nettoyage automatique de la corbeille",
        )

    except Exception as error:
        logger.exception("PaperNest n'a pas pu démarrer correctement.")

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                padding=40,
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.ERROR_OUTLINE_ROUNDED,
                            size=64,
                            color=ft.Colors.RED_600,
                        ),
                        ft.Text(
                            "PaperNest n'a pas pu démarrer.",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            str(error),
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Text(
                            f"Consulte le journal {get_current_log_path().name} "
                            "dans Documents/PaperNest/logs/ pour plus de détails.",
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_600,
                        ),
                    ],
                ),
            )
        )
        return

    app_window = MainWindow(page)
    app_window.build()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
