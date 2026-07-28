from __future__ import annotations

import asyncio

import flet as ft
from papernestextension.controls.material.papernest_textfield import PaperNestTextFieldState

from app.notifications import notifications
from app.preview import PreviewController, PreviewPanel
from app.search.builder import SearchBuilder
from app.search.controller import SearchController
from app.search.state import SearchState
from app.theme.buttons import DangerButton, PrimaryButton, SecondaryButton
from app.theme.cards import AppSection
from app.theme.dialogs import AppDialog, DialogVariant
from app.theme.forms import (
    BaseCheckbox,
    BaseDropDown,
    BaseTextField,
    PaperNestDropdownOption,
    SearchDropDown,
    SearchTextField,
)
from app.theme.status_bar import StatusBar
from app.theme.tokens import AppSpacing
from core.errors.exceptions import PaperNestError
from core.models.search_filters import SearchFilters
from repositories.category_repository import category_repository


class SearchPanel(AppSection):
    SEARCH_DELAY_SECONDS = 0.35

    def __init__(self, page: ft.Page):
        self.app_page = page
        self._mounted = False
        self.state = SearchState()
        self.controller = SearchController(self.state, on_state_changed=self.render_state)

        self.search_field = SearchTextField(
            hint_text="Nom, contenu, notes…",
            expand=True,
            debounce_ms=int(self.SEARCH_DELAY_SECONDS * 1000),
            on_search=self.handle_search,
        )

        categories = category_repository.list_all()
        self.category_filter = SearchDropDown(
            label="Classeur",
            value="all",
            width=190,
            options=[
                PaperNestDropdownOption(
                    key="all",
                    text="Tous",
                    leading_icon=ft.Icons.FOLDER_COPY_ROUNDED,
                )
            ]
            + [
                PaperNestDropdownOption(
                    key=str(item["key"]),
                    text=(
                        f"↳ {item['name']}"
                        if item.get("parent_key")
                        else str(item["name"])
                    ),
                    leading_icon=getattr(
                        ft.Icons,
                        str(item.get("icon") or ""),
                        (
                            ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED
                            if item.get("parent_key")
                            else ft.Icons.FOLDER_ROUNDED
                        ),
                    ),
                )
                for item in categories
            ],
            on_change=self.handle_filter_change,
            on_clear=self.handle_filter_clear,
        )
        self.type_filter = SearchDropDown(
            label="Type",
            value="all",
            width=145,
            options=[
                PaperNestDropdownOption(
                    key="all",
                    text="Tous",
                    leading_icon=ft.Icons.INSERT_DRIVE_FILE_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key=".pdf",
                    text="PDF",
                    leading_icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="image",
                    text="Images",
                    leading_icon=ft.Icons.IMAGE_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key=".docx",
                    text="Word",
                    leading_icon=ft.Icons.DESCRIPTION_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key=".xlsx",
                    text="Excel",
                    leading_icon=ft.Icons.TABLE_CHART_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key=".txt",
                    text="Texte",
                    leading_icon=ft.Icons.NOTES_ROUNDED,
                ),
            ],
            on_change=self.handle_filter_change,
            on_clear=self.handle_filter_clear,
        )
        self.period_filter = SearchDropDown(
            label="Importé",
            value="all",
            width=165,
            hint_text="Choisir une période",
            options=[
                PaperNestDropdownOption(
                    key="all",
                    text="Toute période",
                    leading_icon=ft.Icons.DATE_RANGE_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="7_days",
                    text="7 derniers jours",
                    leading_icon=ft.Icons.TODAY_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="30_days",
                    text="30 derniers jours",
                    leading_icon=ft.Icons.CALENDAR_VIEW_MONTH_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="90_days",
                    text="90 derniers jours",
                    leading_icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="1_year",
                    text="12 derniers mois",
                    leading_icon=ft.Icons.EVENT_NOTE_ROUNDED,
                ),
            ],
            on_change=self.handle_filter_change,
            on_clear=self.handle_filter_clear,
        )
        self.person_filter = BaseTextField(
            label="Personne",
            prefix_icon=ft.Icon(ft.Icons.PERSON_ROUNDED),
            width=175,
            on_change=self.handle_filter_text_change,
        )
        self.tag_filter = BaseTextField(
            label="Tag",
            prefix_icon=ft.Icon(ft.Icons.TAG_ROUNDED),
            width=155,
            on_change=self.handle_filter_text_change,
        )
        self.favorite_filter = BaseCheckbox(
            label="Favoris",
            value=False,
            on_change=self.handle_filter_change,
        )
        self.sort_filter = SearchDropDown(
            label="Trier par",
            value="relevance",
            width=180,
            options=[
                PaperNestDropdownOption(
                    key="relevance",
                    text="Pertinence",
                    leading_icon=ft.Icons.AUTO_AWESOME_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="newest",
                    text="Import récent",
                    leading_icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="oldest",
                    text="Import ancien",
                    leading_icon=ft.Icons.ARROW_UPWARD_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="name",
                    text="Nom A → Z",
                    leading_icon=ft.Icons.SORT_BY_ALPHA_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="name_desc",
                    text="Nom Z → A",
                    leading_icon=ft.Icons.SORT_BY_ALPHA_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="size_desc",
                    text="Taille décroissante",
                    leading_icon=ft.Icons.DATA_USAGE_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="size_asc",
                    text="Taille croissante",
                    leading_icon=ft.Icons.DATA_USAGE_ROUNDED,
                ),
                PaperNestDropdownOption(
                    key="favorite",
                    text="Favoris d'abord",
                    leading_icon=ft.Icons.STAR_ROUNDED,
                ),
            ],
            on_change=self.handle_filter_change,
            on_clear=self.handle_sort_clear,
        )

        self.saved_search_filter = BaseDropDown(
            width=220,
            value="",
            options=[],
            on_change=self.load_saved_search,
        )
        self.save_button = PrimaryButton(
            "Enregistrer Modèle",
            icon=ft.Icons.BOOKMARK_ADD_ROUNDED,
            on_click=self.open_save_dialog,
        )
        self.delete_saved_button = DangerButton(
            "Supprimer Modèle",
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            on_click=self.delete_saved_search,
        )
        self.reset_filters_button = SecondaryButton(
            "Réinitialiser",
            icon=ft.Icons.FILTER_ALT_OFF_ROUNDED,
            on_click=self.reset_filters,
        )

        self.status_bar = StatusBar()
        self.results_list = ft.ListView(
            spacing=AppSpacing.SM,
            expand=True,
            padding=2,
        )
        self.preview_controller = PreviewController()
        self.preview_panel = PreviewPanel(
            page,
            self.preview_controller,
            on_close=self.close_preview,
            on_previous_document=self.previous_preview,
            on_next_document=self.next_preview,
        )
        self.preview_panel.visible = False

        self.results_container = ft.Container(expand=1, content=self.results_list)
        self.preview_container = ft.Container(
            expand=1,
            visible=False,
            content=self.preview_panel,
        )
        self.body = ft.Row(
            expand=True,
            spacing=AppSpacing.MD,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[self.results_container, self.preview_container],
        )

        content = ft.Column(
            spacing=AppSpacing.MD,
            controls=[
                self.search_field,
                ft.Row(
                    spacing=AppSpacing.SM,
                    run_spacing=AppSpacing.SM,
                    controls=[
                        self.category_filter,
                        self.type_filter,
                        self.period_filter,
                        self.person_filter,
                        self.tag_filter,
                        self.favorite_filter,
                        self.sort_filter,
                        self.reset_filters_button,
                    ],
                ),
                self.status_bar,
                ft.Container(content=self.body),
            ],
        )
        super().__init__(
            title="Recherche avancée",
            icon=ft.Icons.MANAGE_SEARCH_ROUNDED,
            content=content,
        )
        self.refresh_saved_searches()
        self.render_state()

    def did_mount(self) -> None:
        self._mounted = True

    def will_unmount(self) -> None:
        self.dispose()

    def dispose(self) -> None:
        self._mounted = False
        self.controller.invalidate_search()

    async def handle_search(self, _event) -> None:
        await self.trigger_search_async()

    async def handle_filter_text_change(self, _event) -> None:
        generation = self.controller.begin_search(self.get_query(), self.get_filters())
        await asyncio.sleep(self.SEARCH_DELAY_SECONDS)
        if generation == self.state.generation:
            await self.controller.search(
                self.state.query,
                self.state.filters,
                generation,
            )

    async def handle_filter_change(self, _event) -> None:
        await self.trigger_search_async()

    async def handle_filter_clear(self, event) -> None:
        event.control.value = "all"
        await self.trigger_search_async()

    async def handle_sort_clear(self, event) -> None:
        event.control.value = "relevance"
        await self.trigger_search_async()

    async def trigger_search_async(self) -> None:
        generation = self.controller.begin_search(self.get_query(), self.get_filters())
        await self.controller.search(self.state.query, self.state.filters, generation)

    def trigger_search(self) -> None:
        generation = self.controller.begin_search(self.get_query(), self.get_filters())
        self.app_page.run_task(
            self.controller.search,
            self.state.query,
            self.state.filters,
            generation,
        )

    def render_state(self) -> None:
        self.results_list.controls = SearchBuilder.build_results(
            state=self.state,
            on_preview=self.show_preview,
            on_open_folder=self.open_parent_folder,
            on_open_document=self.open_document,
            on_retry=lambda _event: self.trigger_search(),
        )

        self.search_field.searching = self.state.loading
        self.search_field.state = (
            PaperNestTextFieldState.ERROR
            if self.state.error_message
            else PaperNestTextFieldState.NORMAL
        )
        self.search_field.state_message = self.state.error_message or None
        self.status_bar.set_loading(self.state.loading, "Recherche…")
        if not self.state.loading:
            if self.state.has_searched and not self.state.error_message:
                self.status_bar.set_count(
                    len(self.state.documents),
                    "résultat",
                    "résultats",
                )
            else:
                self.status_bar.clear_message()
                self.status_bar.counter.value = ""

        if self.state.selected_index < 0 and self.preview_container.visible:
            self.preview_panel.clear()
            self.preview_container.visible = False

        if self.state.error_message:
            notifications(self.app_page).error(self.state.error_message)

        self.safe_update()

    def show_preview(self, index: int) -> None:
        document = self.controller.select_document(index)
        if document is None:
            return

        self.preview_controller.select_file(
            document.absolute_path,
            document.name,
            category_name=document.category,
            file_size=document.file_size,
        )
        self.preview_panel.set_document_navigation(
            has_previous=index > 0,
            has_next=index < len(self.state.documents) - 1,
        )
        self.preview_panel.show_document()
        self.preview_container.visible = True
        self.safe_update()

    def previous_preview(self) -> None:
        self.show_preview(self.state.selected_index - 1)

    def next_preview(self) -> None:
        self.show_preview(self.state.selected_index + 1)

    def close_preview(self) -> None:
        self.state.clear_selection()
        self.preview_panel.clear()
        self.preview_container.visible = False
        self.safe_update()

    def get_query(self) -> str:
        return str(self.search_field.value or "").strip()

    def get_filters(self) -> SearchFilters:
        value = lambda control, default="all": str(control.value or default)
        return SearchFilters(
            category_key=(
                None
                if value(self.category_filter) == "all"
                else value(self.category_filter)
            ),
            file_type=(
                None if value(self.type_filter) == "all" else value(self.type_filter)
            ),
            favorites_only=bool(self.favorite_filter.value),
            imported_period=(
                None
                if value(self.period_filter) == "all"
                else value(self.period_filter)
            ),
            person_query=str(self.person_filter.value or "").strip() or None,
            tag_query=str(self.tag_filter.value or "").strip() or None,
            sort_order=value(self.sort_filter, "relevance"),
            limit=500,
        )

    def clear_search(self, _event=None) -> None:
        self.search_field.value = ""
        self.trigger_search()

    def reset_filters(self, _event=None) -> None:
        for control in (
            self.category_filter,
            self.type_filter,
            self.period_filter,
        ):
            control.value = "all"
        for control in (self.person_filter, self.tag_filter):
            control.value = ""
        self.favorite_filter.value = False
        self.sort_filter.value = "relevance"
        self.saved_search_filter.value = ""
        self.search_field.value = ""
        self.trigger_search()

    def refresh_saved_searches(self) -> None:
        self.saved_search_filter.options = [
            PaperNestDropdownOption(key="", text="Choisir un modèle…")
        ] + [
            PaperNestDropdownOption(key=item["name"], text=item["name"])
            for item in self.controller.list_saved_searches()
        ]

    def open_save_dialog(self, _event=None) -> None:
        name_field = BaseTextField(label="Nom de la recherche", autofocus=True)

        def close(_event=None) -> None:
            dialog.open = False
            self.app_page.update()

        def save(_event=None) -> None:
            try:
                saved_name = self.controller.save_search(
                    str(name_field.value or ""),
                    self.get_query(),
                    self.get_filters(),
                )
                self.refresh_saved_searches()
                self.saved_search_filter.value = saved_name
                close()
                self.safe_update()
                notifications(self.app_page).success("Recherche enregistrée.")
            except ValueError as error:
                name_field.state = PaperNestTextFieldState.ERROR
                name_field.state_message = str(error)
                name_field.update()

        dialog = AppDialog(
            title="Enregistrer la recherche",
            icon=ft.Icons.BOOKMARK_ADD_ROUNDED,
            variant=DialogVariant.PRIMARY,
            content=name_field,
            actions=[
                SecondaryButton("Annuler", on_click=close),
                PrimaryButton(
                    "Enregistrer",
                    icon=ft.Icons.SAVE_ROUNDED,
                    on_click=save,
                ),
            ],
        )
        self.app_page.overlay.append(dialog)
        dialog.open = True
        self.app_page.update()

    async def load_saved_search(self, _event=None) -> None:
        name = str(self.saved_search_filter.value or "")
        saved_search = self.controller.load_saved_search(name)
        if saved_search is None:
            return

        query, filters = saved_search
        self.search_field.value = query
        self.category_filter.value = filters.category_key or "all"
        self.type_filter.value = filters.file_type or "all"
        self.period_filter.value = filters.imported_period or "all"
        self.person_filter.value = filters.person_query or ""
        self.tag_filter.value = filters.tag_query or ""
        self.favorite_filter.value = filters.favorites_only
        self.sort_filter.value = filters.sort_order
        await self.trigger_search_async()

    def delete_saved_search(self, _event=None) -> None:
        name = str(self.saved_search_filter.value or "")
        if not name:
            return
        self.controller.delete_saved_search(name)
        self.saved_search_filter.value = ""
        self.refresh_saved_searches()
        self.safe_update()
        notifications(self.app_page).success("Recherche supprimée.")

    def open_document(self, target_path: str) -> None:
        try:
            self.controller.open_document(target_path)
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))

    def open_parent_folder(self, target_path: str) -> None:
        try:
            self.controller.open_parent_folder(target_path)
        except PaperNestError as error:
            notifications(self.app_page).error(str(error))

    def safe_update(self) -> None:
        try:
            if self.page is not None:
                self.update()
        except RuntimeError:
            pass
