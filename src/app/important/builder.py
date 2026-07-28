import flet as ft

from app.detail.components.document_card import DocumentCard
from app.important.state import ImportantState
from app.theme.state_view import StateView


class ImportantBuilder:
    @staticmethod
    def build_documents(*, page: ft.Page, state: ImportantState, on_preview, on_changed, on_retry) -> list[ft.Control]:
        if state.error_message:
            return [StateView.error(state.error_message, action_text="Réessayer", on_action=on_retry)]

        if not state.documents:
            return [ImportantBuilder.build_empty_state(state.selected_tab)]

        return [
            DocumentCard(page=page, document=document, selected=(document.document_id == state.selected_document_id), on_preview=on_preview, on_changed=on_changed)
            for document in state.documents
        ]

    @staticmethod
    def build_empty_state(selected_tab: str) -> StateView:
        if selected_tab == "favorites":
            return StateView.empty(title="Aucun favori", message=("Ajoutez une étoile à un document pour le retrouver ici."), icon=ft.Icons.STAR_BORDER_ROUNDED)
        return StateView.empty(title="Aucune échéance", message="Aucune échéance dans les 30 prochains jours.", icon=ft.Icons.EVENT_AVAILABLE_ROUNDED)

    @staticmethod
    def count_labels(selected_tab: str) -> tuple[str, str]:
        if selected_tab == "favorites":
            return "favori", "favoris"
        return "échéance", "échéances"
