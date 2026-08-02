import asyncio

import flet as ft

from app.notifications import notifications
from app.shared.tag_editor import TagEditor
from app.theme.buttons import PrimaryButton, GhostButton
from app.theme.pickers import BaseDatePickerField
from app.theme.dialogs import AppDialog, DialogVariant
from app.theme.forms import BaseTextField
from app.theme.forms import BaseSwitch, BaseTextArea
from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors
from services.documents.metadata import InvalidMetadataError, metadata_service
from services.tags.service import tag_service


class MetadataDialog:
    def __init__(self, page: ft.Page, document, on_saved=None):
        self.page = page
        self.document = document
        self.on_saved = on_saved
        self.dialog: AppDialog | None = None

    async def show(self) -> None:
        if self.document.document_id is None:
            notifications(self.page).error(
                "Ce document ne possède pas d’identifiant."
            )
            return

        try:
            details, suggestions = await asyncio.gather(
                asyncio.to_thread(
                    metadata_service.get_details,
                    self.document.document_id,
                ),
                asyncio.to_thread(
                    tag_service.suggest_for_document,
                    file_name=self.document.name,
                    category_name=self.document.category,
                    person_name=self.document.person_name,
                    notes=self.document.notes,
                    selected_tags=self.document.tags,
                ),
            )

        except PaperNestError as error:
            notifications(self.page).error(str(error))
            return

        except Exception:
            notifications(self.page).error(
                "Impossible de charger les informations du document."
            )
            return

        self.build(details, suggestions)
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def build(self, details, suggestions: list[str]) -> None:
        self.favorite_field = BaseSwitch(
            label=ft.Text(
                "Favori",
                color=AppColors.TEXT_LIGHT,
                weight=ft.FontWeight.W_600,
            ),
            value=details.is_favorite,
        )

        self.tag_editor = TagEditor(
            initial_tags=details.tags,
            suggestions=suggestions,
            on_error=self.show_error,
        )

        self.document_date_field = BaseDatePickerField(
            page=self.page,
            label="Date du document",
            value=details.document_date,
            icon=ft.Icons.EVENT_ROUNDED,
            expand=True,
        )

        self.due_date_field = BaseDatePickerField(
            page=self.page,
            label="Date d’échéance",
            value=details.due_date,
            icon=ft.Icons.EVENT_BUSY_ROUNDED,
            expand=True,
        )

        self.amount_field = BaseTextField(
            label="Montant",
            hint_text="145,50",
            value=(
                str(details.amount)
                if details.amount is not None
                else ""
            ),
            prefix_icon=ft.Icons.EURO_ROUNDED,
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
        )

        self.person_field = BaseTextField(
            label="Personne concernée",
            value=details.person_name,
            prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
            expand=True,
        )

        self.notes_field = BaseTextArea(
            label="Notes",
            value=details.notes,
            min_lines=5,
            max_lines=8,
            prefix_icon=ft.Icons.NOTES_ROUNDED,
            expand=True
        )

        self.error_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.RED_600,
        )

        self.save_button = PrimaryButton(
            text="Enregistrer",
            icon=ft.Icons.SAVE_ROUNDED,
            on_click=self.save,
        )

        self.dialog = AppDialog(
            modal=True,
            title="Informations du document",
            icon=ft.Icons.INFO_OUTLINE_ROUNDED,
            variant=DialogVariant.PRIMARY,
            title_action=self.favorite_field,
            content=ft.Container(
                width=650,
                content=ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        ft.Text(self.document.name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            padding=12,
                            border_radius=12,
                            bgcolor=ft.Colors.GREY_50,
                            border=ft.Border.all(1, AppColors.BORDER),
                            content=ft.Column(
                                tight=True,
                                spacing=8,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.LABEL_ROUNDED, size=18, color=AppColors.SECONDARY),
                                            ft.Text("Tags", weight=ft.FontWeight.BOLD),
                                        ],
                                    ),
                                    ft.Text("Clique sur une suggestion ou saisis un nouveau tag.", size=11,
                                            color=AppColors.TEXT_MUTED),
                                    self.tag_editor,
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=12,
                            border_radius=12,
                            bgcolor=ft.Colors.GREY_50,
                            border=ft.Border.all(1, AppColors.BORDER),
                            content=ft.Column(
                                tight=True,
                                spacing=8,
                                controls=[
                                    ft.Row(
                                        controls=[
                                            self.document_date_field,
                                            self.due_date_field,
                                        ],
                                        spacing=12,
                                    ),
                                    ft.Row(
                                        controls=[
                                            self.amount_field,
                                            self.person_field,
                                        ],
                                        spacing=12,
                                    ),
                                ],
                            ),
                        ),
                        self.notes_field,
                        self.error_text,
                    ],
                ),
            ),
            actions=[
                GhostButton(
                    "Annuler",
                    on_click=lambda event: self.close(),
                ),
                self.save_button,
            ],
        )

    async def save(self, event) -> None:
        self.set_loading(True)
        self.error_text.value = ""

        try:
            await asyncio.to_thread(
                metadata_service.update_details,
                self.document.document_id,
                is_favorite=bool(self.favorite_field.value),
                tags=self.tag_editor.get_tags(),
                document_date=self.clean_value(
                    self.document_date_field.iso_value
                ),
                due_date=self.clean_value(
                    self.due_date_field.iso_value
                ),
                amount=self.clean_value(
                    self.amount_field.value
                ),
                person_name=self.person_field.value or "",
                notes=self.notes_field.value or "",
            )

            self.close()
            notifications(self.page).success(
                "Informations du document enregistrées."
            )

            if self.on_saved:
                result = self.on_saved()

                if asyncio.iscoroutine(result):
                    await result

        except (InvalidMetadataError, PaperNestError, ValueError) as error:
            self.show_error(str(error))

        except Exception:
            self.show_error(
                "Une erreur inattendue est survenue."
            )

    def set_loading(self, loading: bool) -> None:
        self.favorite_field.disabled = loading
        self.tag_editor.set_disabled(loading)
        self.document_date_field.disabled = loading
        self.due_date_field.disabled = loading
        self.amount_field.disabled = loading
        self.person_field.disabled = loading
        self.notes_field.disabled = loading
        self.save_button.disabled = loading
        self.page.update()

    def show_error(self, message: str) -> None:
        if hasattr(self, "error_text"):
            self.error_text.value = message
        self.set_loading(False)

    def close(self) -> None:
        if self.dialog is None:
            return

        self.dialog.open = False
        self.page.update()

    @staticmethod
    def clean_value(value: str | None) -> str | None:
        if not value:
            return None

        clean_value = value.strip()
        return clean_value or None
