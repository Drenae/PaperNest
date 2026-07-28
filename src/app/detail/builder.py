from __future__ import annotations

import flet as ft

from app.detail.components.document_card import DocumentCard
from app.detail.state import DetailState
from app.theme.buttons import PrimaryButton
from app.theme.state_view import StateView
from app.theme.tokens import AppColors, AppRadius, AppSpacing


class DetailBuilder:
    @staticmethod
    def build_category_filters(state: DetailState, on_select) -> list[ft.Control]:
        items = [(state.FILTER_ALL, "Tous", ft.Icons.FOLDER_COPY_ROUNDED)]
        items.extend(
            (str(item["key"]), str(item["name"]), getattr(ft.Icons, str(item.get("icon") or ""), ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED))
            for item in state.subcategories
        )
        items.append((state.FILTER_DIRECT, "Sans sous-catégorie", ft.Icons.FOLDER_OPEN_ROUNDED))
        return [
            PrimaryButton(
                label,
                icon=icon,
                compact=True,
                bgcolor=AppColors.PRIMARY if key == state.selected_category_key else AppColors.PANEL,
                color=AppColors.TEXT,
                on_click=lambda event, value=key: on_select(value),
            )
            for key, label, icon in items
        ]

    @staticmethod
    def build_documents(state: DetailState, page, on_preview, on_changed, on_retry) -> list[ft.Control]:
        if state.error_message:
            return [StateView.error(state.error_message, action_text="Réessayer", on_action=on_retry)]
        if not state.documents:
            return [DetailBuilder.build_empty_state(state.search_query)]

        def card(document):
            return DocumentCard(
                page=page,
                document=document,
                searching=bool(state.search_query),
                selected=document.document_id == state.selected_document_id,
                on_preview=on_preview,
                on_changed=on_changed,
            )

        if state.selected_category_key != state.FILTER_ALL:
            return [card(document) for document in state.documents]

        controls: list[ft.Control] = []
        by_category: dict[str, list] = {}
        for document in state.documents:
            by_category.setdefault(str(document.category_key or ""), []).append(document)

        for subcategory in state.subcategories:
            key = str(subcategory["key"])
            documents = by_category.get(key, [])
            if documents:
                controls.append(DetailBuilder.build_group_header(
                    str(subcategory["name"]), len(documents),
                    getattr(ft.Icons, str(subcategory.get("icon") or ""), ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED),
                ))
                controls.extend(card(document) for document in documents)

        direct = by_category.get(state.category_key, [])
        if direct:
            controls.append(DetailBuilder.build_group_header("Sans sous-catégorie", len(direct), ft.Icons.FOLDER_OPEN_ROUNDED))
            controls.extend(card(document) for document in direct)

        known = {state.category_key, *state.subcategory_by_key.keys()}
        ungrouped = [document for document in state.documents if str(document.category_key or "") not in known]
        if ungrouped:
            controls.append(DetailBuilder.build_group_header("Documents", len(ungrouped), ft.Icons.DESCRIPTION_OUTLINED))
            controls.extend(card(document) for document in ungrouped)
        return controls

    @staticmethod
    def build_empty_state(search_query: str) -> StateView:
        if search_query:
            return StateView.empty(
                title="Aucun résultat",
                message="Aucun document ne correspond à cette recherche.",
                icon=ft.Icons.SEARCH_OFF_ROUNDED,
            )
        return StateView.empty(
            title="Aucun document",
            message="Ce classeur ne contient encore aucun document.",
            icon=ft.Icons.FOLDER_OPEN_OUTLINED,
        )

    @staticmethod
    def build_group_header(title: str, count: int, icon) -> ft.Container:
        return ft.Container(
            margin=ft.Margin.only(top=AppSpacing.SM, bottom=AppSpacing.XS),
            padding=ft.Padding.symmetric(horizontal=AppSpacing.MD, vertical=AppSpacing.SM),
            bgcolor=AppColors.PANEL,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=AppRadius.MD,
            content=ft.Row(controls=[
                ft.Icon(icon, color=AppColors.SECONDARY, size=20),
                ft.Text(title, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN, expand=True),
                ft.Text(f"{count} document{'s' if count != 1 else ''}", color=AppColors.TEXT_MUTED, size=12),
            ]),
        )
