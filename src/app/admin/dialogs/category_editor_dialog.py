from __future__ import annotations

import asyncio
import logging

import flet as ft
from papernestextension.controls.material.papernest_textfield import PaperNestTextFieldState

from core.errors.exceptions import PaperNestError
from app.theme.tokens import AppColors, AppRadius, AppSpacing
from services.categories.service import category_service
from app.theme.buttons import GhostButton, PrimaryButton
from app.theme.dialogs import AppDialog, DialogVariant
from app.theme.forms import BaseTextField
from app.theme.pickers import (
    BaseColorPicker,
    BaseIconPicker,
    PaperNestIconPickerOption,
)


logger = logging.getLogger(__name__)

AVAILABLE_ICONS = [
    PaperNestIconPickerOption(label="Dossier", value="FOLDER_ROUNDED", icon=ft.Icons.FOLDER_ROUNDED),
    PaperNestIconPickerOption(label="Identité", value="BADGE_ROUNDED", icon=ft.Icons.BADGE_ROUNDED),
    PaperNestIconPickerOption(label="Logement", value="OTHER_HOUSES_ROUNDED", icon=ft.Icons.OTHER_HOUSES_ROUNDED),
    PaperNestIconPickerOption(label="Santé", value="HEALTH_AND_SAFETY_ROUNDED", icon=ft.Icons.HEALTH_AND_SAFETY_ROUNDED),
    PaperNestIconPickerOption(label="Fiscalité", value="REQUEST_QUOTE_ROUNDED", icon=ft.Icons.REQUEST_QUOTE_ROUNDED),
    PaperNestIconPickerOption(label="Banque", value="ACCOUNT_BALANCE_ROUNDED", icon=ft.Icons.ACCOUNT_BALANCE_ROUNDED),
    PaperNestIconPickerOption(label="Assurance", value="VERIFIED_USER_ROUNDED", icon=ft.Icons.VERIFIED_USER_ROUNDED),
    PaperNestIconPickerOption(label="Travail", value="WORK_ROUNDED", icon=ft.Icons.WORK_ROUNDED),
    PaperNestIconPickerOption(label="Véhicule", value="DIRECTIONS_CAR_ROUNDED", icon=ft.Icons.DIRECTIONS_CAR_ROUNDED),
    PaperNestIconPickerOption(label="Famille", value="FAMILY_RESTROOM_ROUNDED", icon=ft.Icons.FAMILY_RESTROOM_ROUNDED),
    PaperNestIconPickerOption(label="Études", value="SCHOOL_ROUNDED", icon=ft.Icons.SCHOOL_ROUNDED),
    PaperNestIconPickerOption(label="Contrats", value="DESCRIPTION_ROUNDED", icon=ft.Icons.DESCRIPTION_ROUNDED),
    PaperNestIconPickerOption(label="Énergie", value="BOLT_ROUNDED", icon=ft.Icons.BOLT_ROUNDED),
    PaperNestIconPickerOption(label="Télécom", value="ROUTER_ROUNDED", icon=ft.Icons.ROUTER_ROUNDED),
    PaperNestIconPickerOption(label="Voyages", value="FLIGHT_ROUNDED", icon=ft.Icons.FLIGHT_ROUNDED),
    PaperNestIconPickerOption(label="Animaux", value="PETS_ROUNDED", icon=ft.Icons.PETS_ROUNDED),
    PaperNestIconPickerOption(label="Loisirs", value="SPORTS_ESPORTS_ROUNDED", icon=ft.Icons.SPORTS_ESPORTS_ROUNDED),
    PaperNestIconPickerOption(label="Achats", value="SHOPPING_BAG_ROUNDED", icon=ft.Icons.SHOPPING_BAG_ROUNDED),
    PaperNestIconPickerOption(label="Abonnements", value="AUTORENEW_ROUNDED", icon=ft.Icons.AUTORENEW_ROUNDED),
    PaperNestIconPickerOption(label="Archives", value="ARCHIVE_ROUNDED", icon=ft.Icons.ARCHIVE_ROUNDED),
]

DEFAULT_ICON = "FOLDER_ROUNDED"
DEFAULT_COLOR = "#1E88E5"


def light_background(color: str, ratio: float = 0.88) -> str:
    color = BaseColorPicker.normalize_value(color, DEFAULT_COLOR)
    red, green, blue = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    blend = lambda channel: round(channel + (255 - channel) * ratio)
    return f"#{blend(red):02X}{blend(green):02X}{blend(blue):02X}"


class CategoryEditorDialog:
    def __init__(self, page: ft.Page, category: dict | None = None, parent: dict | None = None, on_saved=None):
        self.page = page
        self.category = category
        self.parent = parent
        self.on_saved = on_saved
        self.dialog: AppDialog | None = None

    def show(self) -> None:
        editing = self.category is not None
        current_icon = str((self.category or {}).get("icon") or DEFAULT_ICON)
        current_color = BaseColorPicker.normalize_value(
            (self.category or {}).get("color"),
            DEFAULT_COLOR,
        )

        self.name_field = BaseTextField(
            label="Nom du classeur",
            value=str((self.category or {}).get("name") or ""),
            prefix_icon=ft.Icons.DRIVE_FILE_RENAME_OUTLINE_ROUNDED,
            autofocus=True,
        )
        self.icon_field = BaseIconPicker(
            label="Icône",
            options=AVAILABLE_ICONS,
            value=current_icon,
            fallback_value=DEFAULT_ICON,
            on_change=self.update_preview,
        )
        self.color_field = BaseColorPicker(
            label="Couleur",
            value=current_color,
            on_change=self.update_preview,
        )
        self.preview_icon = ft.Icon(
            getattr(ft.Icons, self.icon_field.value or DEFAULT_ICON, ft.Icons.FOLDER_ROUNDED),
            color=current_color,
            size=30,
        )
        default_title = "Nouvelle sous-catégorie" if self.parent else "Nouveau classeur"
        self.preview_title = ft.Text(
            self.name_field.value or default_title,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_MAIN,
        )
        self.preview = ft.Container(
            padding=AppSpacing.MD,
            border_radius=AppRadius.LG,
            bgcolor=light_background(current_color),
            border=ft.Border.all(1, current_color),
            content=ft.Row([self.preview_icon, self.preview_title], spacing=AppSpacing.MD),
        )
        self.error_text = ft.Text("", size=12, color=AppColors.ERROR)
        self.name_field.on_change = self.update_preview
        self.save_button = PrimaryButton(
            "Enregistrer" if editing else "Créer",
            icon=ft.Icons.SAVE_ROUNDED,
            on_click=self.save,
        )
        self.dialog = AppDialog(
            title=("Modifier la sous-catégorie" if editing and self.category and self.category.get("parent_key") else "Modifier le classeur") if editing else (f"Ajouter dans {self.parent['name']}" if self.parent else "Ajouter un classeur"),
            icon=ft.Icons.EDIT_ROUNDED if editing else ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            variant=DialogVariant.PRIMARY,
            width=560,
            content=ft.Column(
                tight=True,
                spacing=AppSpacing.MD,
                controls=[
                    self.preview,
                    self.name_field,
                    self.icon_field,
                    self.color_field,
                    self.error_text,
                ],
            ),
            actions=[GhostButton("Annuler", on_click=self.close), self.save_button],
        )
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def update_preview(self, _event=None) -> None:
        if (self.name_field.value or "").strip():
            self.name_field.state = PaperNestTextFieldState.NORMAL
            self.name_field.state_message = None
        color = BaseColorPicker.normalize_value(self.color_field.value, DEFAULT_COLOR)
        icon_name = self.icon_field.value or DEFAULT_ICON
        self.preview_icon.icon = getattr(
            ft.Icons,
            icon_name,
            ft.Icons.FOLDER_ROUNDED,
        )
        self.preview_icon.color = color
        self.preview_title.value = (self.name_field.value or "").strip() or ("Nouvelle sous-catégorie" if self.parent else "Nouveau classeur")
        self.preview.bgcolor = light_background(color)
        self.preview.border = ft.Border.all(1, color)
        try:
            self.dialog.update() if self.dialog else None
        except RuntimeError:
            pass

    async def save(self, _event=None) -> None:
        name = (self.name_field.value or "").strip()
        if not name:
            self.name_field.state = PaperNestTextFieldState.ERROR
            self.name_field.state_message = "Le nom du classeur est obligatoire."
            self.page.update()
            return
        self.save_button.disabled = True
        self.name_field.state = PaperNestTextFieldState.NORMAL
        self.name_field.state_message = None
        self.error_text.value = ""
        self.page.update()
        try:
            icon = self.icon_field.value or DEFAULT_ICON
            color = BaseColorPicker.normalize_value(self.color_field.value, DEFAULT_COLOR)
            background = light_background(color)
            if self.category is None:
                if self.parent is not None:
                    result = await asyncio.to_thread(category_service.create_subcategory, str(self.parent["key"]), name, icon, color, background)
                else:
                    result = await asyncio.to_thread(category_service.create_category, name, icon, color, background)
            else:
                old_key = str(self.category["key"])
                result = await asyncio.to_thread(category_service.rename_category, old_key, name)
                result = await asyncio.to_thread(category_service.update_appearance, str(result["key"]), name=name, icon=icon, color=color, background=background)
            self.close()
            if self.on_saved:
                callback = self.on_saved(result)
                if asyncio.iscoroutine(callback):
                    await callback
        except PaperNestError as error:
            self.error_text.value = str(error)
            self.save_button.disabled = False
            self.page.update()
        except Exception:
            logger.exception("Impossible d'enregistrer le classeur.")
            self.error_text.value = "Impossible d’enregistrer le classeur."
            self.save_button.disabled = False
            self.page.update()

    def close(self, _event=None) -> None:
        if self.dialog is not None:
            self.dialog.open = False
            self.page.update()
