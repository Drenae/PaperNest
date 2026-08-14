import flet as ft

from app.theme.buttons import IconAction
from app.theme.forms import BaseTextField
from utils.text import normalize_search_text
from app.theme.tokens import AppColors
from repositories.tag_repository import tag_repository
from services.tags.service import tag_service


class TagEditor(ft.Column):
    def __init__(
        self,
        *,
        initial_tags: tuple[str, ...] | list[str] = (),
        suggestions: list[str] | None = None,
        on_error=None,
    ):
        self.selected_tags = tag_repository.normalize_tags(
            list(initial_tags)
        )
        self.base_suggestions = suggestions or []
        self.on_error = on_error

        self.input_field = BaseTextField(
            label="Ajouter un tag",
            hint_text="Ex. assurance, maison, 2026",
            prefix_icon=ft.Icons.LABEL_OUTLINE_ROUNDED,
            expand=True,
            on_submit=self.add_from_input,
            on_change=self.handle_input_change,
        )

        self.add_button = IconAction(
            icon=ft.Icons.ADD_CIRCLE_ROUNDED,
            tooltip="Ajouter le tag",
            icon_color=AppColors.SECONDARY,
            compact=True,
            on_click=self.add_from_input,
        )

        self.selected_container = ft.Column(
            tight=True,
            spacing=6,
        )

        self.suggestion_title = ft.Text(
            "Suggestions",
            size=11,
            color=AppColors.TEXT_MUTED,
            visible=False,
        )

        self.suggestion_row = ft.Row(
            wrap=True,
            spacing=6,
            run_spacing=6,
        )

        super().__init__(
            tight=True,
            spacing=8,
            controls=[
                self.selected_container,
                ft.Row(
                    spacing=4,
                    controls=[
                        self.input_field,
                        self.add_button,
                    ],
                ),
                self.suggestion_title,
                self.suggestion_row,
            ],
        )

        self.render_selected_tags()
        self.render_suggestions(self.base_suggestions)

    def get_tags(self) -> list[str]:
        return list(self.selected_tags)

    def set_suggestions(self, suggestions: list[str]) -> None:
        self.base_suggestions = suggestions
        self.render_suggestions(suggestions)
        self.safe_update()

    def add_from_input(self, event=None) -> None:
        raw_value = self.input_field.value or ""
        candidates = [
            item
            for part in raw_value.split(",")
            for item in part.split(";")
        ]

        self.add_tags(candidates)
        self.input_field.value = ""
        self.render_suggestions(self.base_suggestions)
        self.safe_update()

        try:
            self.input_field.focus()
        except RuntimeError:
            pass

    def add_tag(self, tag_name: str) -> None:
        self.add_tags([tag_name])
        self.render_suggestions(self.base_suggestions)
        self.safe_update()

    def add_tags(self, tags: list[str]) -> None:
        try:
            combined = tag_repository.normalize_tags(
                self.selected_tags + tags
            )
        except ValueError as error:
            self.show_error(str(error))
            return

        self.selected_tags = combined
        self.render_selected_tags()

    def remove_tag(self, tag_name: str) -> None:
        normalized_to_remove = normalize_search_text(tag_name)
        self.selected_tags = [
            tag
            for tag in self.selected_tags
            if normalize_search_text(tag) != normalized_to_remove
        ]

        self.render_selected_tags()
        self.render_suggestions(self.base_suggestions)
        self.safe_update()

    def handle_input_change(self, event=None) -> None:
        query = self.input_field.value or ""

        if query.strip():
            suggestions = tag_service.filter_suggestions(
                query,
                selected_tags=self.selected_tags,
            )
        else:
            suggestions = self.base_suggestions

        self.render_suggestions(suggestions)
        self.safe_update()

    def render_selected_tags(self) -> None:
        if not self.selected_tags:
            self.selected_container.controls = [
                ft.Text(
                    "Aucun tag ajouté.",
                    size=11,
                    color=AppColors.TEXT_MUTED,
                )
            ]
            return

        self.selected_container.controls = [
            ft.Row(
                wrap=True,
                spacing=6,
                run_spacing=6,
                controls=[
                    self.build_selected_tag(tag)
                    for tag in self.selected_tags
                ],
            )
        ]

    def render_suggestions(self, suggestions: list[str]) -> None:
        selected = {
            normalize_search_text(tag)
            for tag in self.selected_tags
        }

        filtered = []
        seen = set()
        for suggestion in suggestions:
            normalized = normalize_search_text(suggestion)
            if not normalized or normalized in selected or normalized in seen:
                continue
            seen.add(normalized)
            filtered.append(suggestion)

        self.suggestion_title.visible = bool(filtered)
        self.suggestion_row.controls = [
            self.build_suggestion_tag(tag)
            for tag in filtered[:10]
        ]

    def build_selected_tag(self, tag_name: str) -> ft.Container:
        return ft.Container(
            bgcolor=ft.Colors.BLUE_50,
            border=ft.Border.all(1, ft.Colors.BLUE_200),
            border_radius=14,
            padding=ft.Padding.only(left=9, right=2, top=3, bottom=3),
            content=ft.Row(
                tight=True,
                spacing=1,
                controls=[
                    ft.Text(
                        tag_name,
                        size=11,
                        color=AppColors.SECONDARY,
                    ),
                    IconAction(
                        icon=ft.Icons.CLOSE_ROUNDED,
                        icon_size=14,
                        compact=True,
                        tooltip=f"Retirer {tag_name}",
                        on_click=(
                            lambda event, name=tag_name: self.remove_tag(name)
                        ),
                    ),
                ],
            ),
        )

    def build_suggestion_tag(self, tag_name: str) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Row(
                tight=True,
                spacing=4,
                controls=[
                    ft.Icon(
                        ft.Icons.ADD_ROUNDED,
                        size=14,
                    ),
                    ft.Text(
                        tag_name,
                        size=11,
                    ),
                ],
            ),
            on_click=lambda event, name=tag_name: self.add_tag(name),
        )

    def set_disabled(self, disabled: bool) -> None:
        self.input_field.disabled = disabled
        self.add_button.disabled = disabled

        for control in self.suggestion_row.controls:
            control.disabled = disabled

        for row in self.selected_container.controls:
            if isinstance(row, ft.Row):
                for container in row.controls:
                    if isinstance(container, ft.Container) and isinstance(container.content, ft.Row):
                        for item in container.content.controls:
                            if isinstance(item, ft.IconButton):
                                item.disabled = disabled

    def show_error(self, message: str) -> None:
        if self.on_error:
            self.on_error(message)

    def safe_update(self) -> None:
        try:
            self.update()
        except RuntimeError:
            pass
