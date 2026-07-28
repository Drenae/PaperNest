import flet as ft

from app.theme.state_view import StateView
from app.trash.components.trashed_document_card import TrashedDocumentCard
from app.trash.state import TrashState


class TrashBuilder:
    @staticmethod
    def build_documents(state: TrashState, on_selected, on_open_folder, on_restore, on_delete, on_retry) -> list[ft.Control]:
        if state.error_message:
            return [StateView.error(state.error_message, action_text="Réessayer", on_action=on_retry)]

        if not state.documents:
            has_search = bool(state.search_query)
            return [
                StateView.empty(
                    title="Aucun résultat" if has_search else "Corbeille vide",
                    message=("Aucun document ne correspond à cette recherche." if has_search else "Les documents supprimés apparaîtront ici."),
                    icon=(ft.Icons.SEARCH_OFF_ROUNDED if has_search else ft.Icons.DELETE_SWEEP_OUTLINED),
                )
            ]

        return [
            TrashedDocumentCard(
                document=document,
                selected=document.trash_id in state.selected_ids,
                on_selected=on_selected,
                on_open_folder=on_open_folder,
                on_restore=on_restore,
                on_delete=on_delete,
            )
            for document in state.documents
        ]

    @staticmethod
    def selection_label(count: int) -> str:
        if count == 0:
            return "Aucune sélection"
        if count == 1:
            return "1 document sélectionné"
        return f"{count} documents sélectionnés"

    @staticmethod
    def count_labels(search_query: str) -> tuple[str, str]:
        if search_query:
            return "résultat", "résultats"
        return "document", "documents"
