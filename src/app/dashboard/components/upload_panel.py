from __future__ import annotations

from collections.abc import Callable

import flet as ft
from papernestextension import PaperNestFilePickerValidationEvent

from app.dashboard.state import DashboardState
from app.theme.buttons import IconAction, PrimaryButton
from app.theme.cards import AppSection
from app.theme.forms import BaseCheckbox, BaseDropDown, PaperNestDropdownOption
from app.theme.pickers import BaseFilePicker
from app.theme.tokens import AppColors


class UploadPanel(AppSection):
    """Affichage passif de la préparation et de la progression d’un import."""

    def __init__(
        self,
        *,
        on_browse: Callable,
        on_clear: Callable,
        on_commit: Callable,
        on_default_category: Callable,
        on_keep_duplicates: Callable,
        on_files_changed: Callable,
        on_validation_error: Callable[[PaperNestFilePickerValidationEvent], None],
        on_duplicate_file: Callable,
    ):
        self.file_picker = BaseFilePicker(
            allow_multiple=True,
            drag_and_drop=True,
            with_data=False,
            show_file_list=True,
            show_file_size=True,
            use_file_type_colors=True,
            dialog_title="Sélectionner des documents",
            drop_text="Déposez vos documents ici",
            drop_subtitle="ou utilisez le bouton ci-dessous",
            icon=ft.Icons.UPLOAD_FILE_ROUNDED,
            click_to_pick=True,
            show_constraints=False,
            on_files_changed=on_files_changed,
            on_validation_error=on_validation_error,
            on_duplicate_file=on_duplicate_file,
        )
        self.browse_trigger = PrimaryButton(
            "Ajouter des fichiers",
            icon=ft.Icons.FOLDER_OPEN_ROUNDED,
            on_click=on_browse,
            expand=True,
        )
        self.clear_trigger = IconAction(
            icon=ft.Icons.CLOSE_ROUNDED,
            icon_color=AppColors.TEXT_MUTED,
            tooltip="Retirer tous les fichiers préparés",
            visible=False,
            on_click=on_clear,
        )
        self.category_selector = BaseDropDown(
            label="Classeur par défaut",
            icon=ft.Icons.FOLDER_COPY_ROUNDED,
            options=[],
            on_select=on_default_category,
        )
        self.category_selector.disabled = True
        self.keep_duplicates = BaseCheckbox(
            label="Importer aussi les doublons détectés",
            value=False,
            disabled=True,
            on_change=on_keep_duplicates,
        )
        self.files_list = ft.Column(spacing=8)
        self.files_container = ft.Container(
            visible=False,
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=12,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Classement des documents",
                                expand=True,
                                weight=ft.FontWeight.BOLD,
                            ),
                            self.clear_trigger,
                        ]
                    ),
                    self.category_selector,
                    ft.Text(
                        "Le classeur par défaut est appliqué à tous. "
                        "Modifiez seulement les exceptions.",
                        size=11,
                        color=AppColors.TEXT_MUTED,
                    ),
                    self.files_list,
                    self.keep_duplicates,
                ],
            ),
        )
        self.processing_bar = ft.ProgressBar(
            value=0,
            visible=False,
            color=AppColors.PRIMARY_DARK,
            bgcolor=ft.Colors.GREY_300,
            border_radius=4,
        )
        self.summary_text = ft.Text(
            "",
            size=11,
            color=AppColors.TEXT_MUTED,
            visible=False,
        )
        self.commit_trigger = PrimaryButton(
            "Classer les documents",
            icon=ft.Icons.INVENTORY_2_ROUNDED,
            on_click=on_commit,
            expand=True,
        )
        self.commit_trigger.disabled = True

        super().__init__(
            title="Classer des fichiers",
            icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            content=ft.Column(
                spacing=14,
                controls=[
                    self.file_picker,
                    ft.Row([self.browse_trigger]),
                    self.files_container,
                    self.processing_bar,
                    self.summary_text,
                    ft.Row([self.commit_trigger]),
                ],
            ),
            expand=1,
        )

    def render(
        self,
        state: DashboardState,
        category_options: list[PaperNestDropdownOption],
        file_rows: list[ft.Control],
    ) -> None:
        has_files = bool(state.staged_files)
        self.category_selector.options = list(category_options)
        self.files_list.controls = list(file_rows)
        self.files_container.visible = has_files
        self.clear_trigger.visible = has_files
        self.category_selector.disabled = state.loading or not has_files
        self.keep_duplicates.disabled = state.loading or not has_files
        self.keep_duplicates.value = state.keep_duplicates
        self.commit_trigger.disabled = state.loading or not has_files
        self.file_picker.disabled = state.loading
        self.browse_trigger.disabled = state.loading
        self.clear_trigger.disabled = state.loading
        self.processing_bar.visible = state.loading
        self.processing_bar.value = state.progress
        self.summary_text.value = state.summary_text
        self.summary_text.visible = bool(state.summary_text)

        if not has_files:
            self.category_selector.value = None
