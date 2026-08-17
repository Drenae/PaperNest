from __future__ import annotations

import flet as ft

from app.search.state import SearchState
from app.shared.document_card import DocumentCard, DocumentCardVariant
from app.theme.buttons import IconAction
from app.theme.state_view import StateView
from app.theme.tokens import AppColors


class SearchBuilder:
    @staticmethod
    def build_results(
        *,
        state: SearchState,
        on_preview,
        on_open_folder,
        on_open_document,
        on_retry,
    ) -> list[ft.Control]:
        if state.error_message:
            return [
                StateView.error(
                    state.error_message,
                    action_text="Réessayer",
                    on_action=on_retry,
                )
            ]

        if not state.has_searched:
            return [
                StateView.empty(
                    title="Construisez votre recherche",
                    message=(
                        "Combinez le texte, le classeur, le type, la période, "
                        "le tri, la personne et les tags."
                    ),
                    icon=ft.Icons.TUNE_ROUNDED,
                )
            ]

        if not state.documents:
            return [
                StateView.empty(
                    title="Aucun résultat",
                    message=(
                        "Aucun document ne correspond à cette combinaison de filtres."
                    ),
                    icon=ft.Icons.SEARCH_OFF_ROUNDED,
                )
            ]

        return [
            SearchBuilder.build_result_card(
                document=document,
                index=index,
                on_preview=on_preview,
                on_open_folder=on_open_folder,
                on_open_document=on_open_document,
            )
            for index, document in enumerate(state.documents)
        ]

    @staticmethod
    def build_result_card(
        *,
        document,
        index: int,
        on_preview,
        on_open_folder,
        on_open_document,
    ) -> DocumentCard:
        metadata = [str(document.category), str(document.file_size)]
        if document.person_name:
            metadata.append(f"Personne : {document.person_name}")
        if document.match_reason:
            metadata.append(str(document.match_reason))

        return DocumentCard(
            title=document.name,
            extension=document.extension,
            metadata=metadata,
            tags=document.tags,
            favorite=document.is_favorite,
            variant=DocumentCardVariant.SEARCH,
            tooltip=f"Aperçu de {document.name}",
            on_click=lambda _event, selected=index: on_preview(selected),
            actions=[
                IconAction(
                    icon=ft.Icons.VISIBILITY_ROUNDED,
                    icon_color=AppColors.PRIMARY_DARK,
                    tooltip="Aperçu",
                    on_click=lambda _event, selected=index: on_preview(selected),
                ),
                IconAction(
                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                    icon_color=AppColors.TEXT_MUTED,
                    tooltip="Ouvrir le dossier",
                    on_click=lambda _event, path=document.absolute_path: on_open_folder(path),
                ),
                IconAction(
                    icon=ft.Icons.LAUNCH_ROUNDED,
                    icon_color=AppColors.SECONDARY,
                    tooltip="Ouvrir",
                    on_click=lambda _event, path=document.absolute_path: on_open_document(path),
                ),
            ],
        )
