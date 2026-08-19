from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.dashboard.components.cabinet_panel import CabinetPanel
from app.dashboard.components.upload_panel import UploadPanel
from app.dashboard.state import DashboardState
from app.detail.detail_view import DetailView
from app.theme.buttons import IconAction
from app.theme.cards import PageHeader
from app.theme.forms import BaseDropDown, PaperNestDropdownOption
from app.theme.tokens import AppColors, AppSpacing


class DashboardBuilder:
    def __init__(
        self,
        *,
        on_category_click,
        on_browse,
        on_clear,
        on_commit,
        on_default_category,
        on_keep_duplicates,
        on_files_changed,
        on_validation_error,
        on_duplicate_file,
    ):
        self.cabinet_panel = CabinetPanel(
            on_category_click=on_category_click,
        )
        self.upload_panel = UploadPanel(
            on_browse=on_browse,
            on_clear=on_clear,
            on_commit=on_commit,
            on_default_category=on_default_category,
            on_keep_duplicates=on_keep_duplicates,
            on_files_changed=on_files_changed,
            on_validation_error=on_validation_error,
            on_duplicate_file=on_duplicate_file,
        )

    def build_main_controls(self) -> list[ft.Control]:
        return [
            PageHeader(
                icon=ft.Icons.DASHBOARD_ROUNDED,
                title="Accueil",
                subtitle=(
                    "Classez vos fichiers puis ouvrez directement "
                    "le classeur souhaité."
                ),
            ),
            ft.ResponsiveRow(
                spacing=AppSpacing.LG,
                run_spacing=AppSpacing.LG,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 5, "lg": 5},
                        content=self.upload_panel,
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 7, "lg": 7},
                        content=self.cabinet_panel,
                    ),
                ],
            ),
        ]

    @staticmethod
    def build_category_options(
        categories: list[dict],
    ) -> list[PaperNestDropdownOption]:
        return [
            PaperNestDropdownOption(
                key=str(category["key"]),
                text=(
                    f"↳ {category['name']}"
                    if category.get("parent_key")
                    else str(category["name"])
                ),
            )
            for category in categories
        ]

    @staticmethod
    def build_file_rows(
        state: DashboardState,
        category_options: list[PaperNestDropdownOption],
        on_category_changed,
        on_remove,
    ) -> list[ft.Control]:
        rows: list[ft.Control] = []

        for item in state.staged_files:
            dropdown = BaseDropDown(
                value=item.category_key,
                width=190,
                dense=True,
                options=[
                    PaperNestDropdownOption(
                        key=option.key,
                        text=option.text,
                    )
                    for option in category_options
                ],
                data=item.file_id,
                on_change=on_category_changed,
            )
            rows.append(
                ft.Container(
                    padding=8,
                    border=ft.Border.all(1, AppColors.BORDER),
                    border_radius=10,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.INSERT_DRIVE_FILE_OUTLINED,
                                size=18,
                                color=AppColors.TEXT_MUTED,
                            ),
                            ft.Text(
                                item.path.name,
                                expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            dropdown,
                            IconAction(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                tooltip="Retirer ce fichier",
                                data=item.file_id,
                                on_click=on_remove,
                            ),
                        ],
                    ),
                )
            )

        return rows

    @staticmethod
    def build_detail_view(
        *,
        page: ft.Page,
        category: dict,
        on_back: Callable,
    ) -> DetailView:
        return DetailView(
            page=page,
            category_cat=category,
            on_back=on_back,
        )
