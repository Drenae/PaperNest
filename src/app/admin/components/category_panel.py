import flet as ft

from core.events.event_bus import CategoryCreated, CategoryDeleted, CategoryRenamed, event_bus
from app.theme.tokens import AppColors, AppSpacing
from repositories.category_repository import category_repository
from app.theme.buttons import IconAction, PrimaryButton
from app.theme.cards import AppCard, AppSection, CardDensity, CardOrientation


def _color(value, fallback):
    raw = str(value or "").strip()
    return raw if raw.startswith("#") else getattr(ft.Colors, raw, fallback)


class CategoryPanel(AppSection):
    def __init__(self, page: ft.Page, on_add_parent, on_add_child, on_rename, on_delete):
        self.app_page = page
        self.on_add_parent = on_add_parent
        self.on_add_child = on_add_child
        self.on_rename = on_rename
        self.on_delete = on_delete
        self._subscribed = False
        self._mounted = False
        self.category_list = ft.Column(spacing=AppSpacing.SM)
        self.add_button = PrimaryButton(
            "Ajouter un classeur",
            icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
            on_click=self.on_add_parent,
        )
        super().__init__(
            title="Classeurs et sous-catégories",
            icon=ft.Icons.ACCOUNT_TREE_ROUNDED,
            actions=[self.add_button],
            content=self.category_list,
            expand=2,
        )
        self.subscribe()
        self.refresh(update_control=False)

    def did_mount(self):
        self._mounted = True
        self.subscribe()
        self.refresh()

    def will_unmount(self):
        self._mounted = False
        self.unsubscribe()

    def subscribe(self):
        if self._subscribed:
            return
        for event_type in (CategoryCreated, CategoryRenamed, CategoryDeleted):
            event_bus.subscribe(event_type, self._handle_event)
        self._subscribed = True

    def unsubscribe(self):
        if not self._subscribed:
            return
        for event_type in (CategoryCreated, CategoryRenamed, CategoryDeleted):
            event_bus.unsubscribe(event_type, self._handle_event)
        self._subscribed = False

    def _handle_event(self, _event):
        self.refresh()

    def refresh(self, update_control: bool = True):
        tree = category_repository.list_tree()
        self.category_list.controls = [self.build_parent_control(item) for item in tree]
        if not tree:
            self.category_list.controls = [self.build_empty_state()]
        if update_control and self._mounted:
            self.update()

    def build_parent_control(self, category: dict) -> AppCard:
        children = list(category.get("children") or [])
        actions = self._build_parent_actions(category)
        count = int(category.get("document_count", 0))
        subtitle = f"{count} document{'s' if count != 1 else ''}"
        expansion_content = None
        if children:
            child_count = len(children)
            subtitle = (
                f"{subtitle} · {child_count} sous-catégorie"
                f"{'s' if child_count != 1 else ''}"
            )
            expansion_content = ft.Column(
                spacing=AppSpacing.SM,
                controls=[self.build_child_card(child) for child in children],
            )

        return AppCard(
            title=str(category["name"]),
            subtitle=subtitle,
            icon=getattr(
                ft.Icons,
                str(category.get("icon")),
                ft.Icons.FOLDER_ROUNDED,
            ),
            icon_color=_color(category.get("color"), AppColors.SECONDARY),
            icon_bgcolor=_color(category.get("bg"), AppColors.PANEL),
            actions=actions,
            expansion_content=expansion_content,
            orientation=CardOrientation.HORIZONTAL,
            density=CardDensity.COMPACT,
            shadow=False,
        )

    def _build_parent_actions(self, category: dict) -> list[ft.Control]:
        return [
            IconAction(
                icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED,
                tooltip="Ajouter une sous-catégorie",
                icon_color=AppColors.SECONDARY,
                on_click=lambda e, item=category: self.on_add_child(item),
            ),
            IconAction(
                icon=ft.Icons.EDIT_OUTLINED,
                tooltip="Modifier",
                icon_color=AppColors.SECONDARY,
                on_click=lambda e, item=category: self.on_rename(item),
            ),
            IconAction(
                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                tooltip="Supprimer",
                icon_color=AppColors.ERROR,
                on_click=lambda e, item=category: self.on_delete(item),
            ),
        ]

    def build_child_card(self, category: dict) -> AppCard:
        count = int(category.get("document_count", 0))
        return AppCard(
            title=str(category["name"]),
            subtitle=f"{count} document{'s' if count != 1 else ''}",
            icon=getattr(
                ft.Icons,
                str(category.get("icon")),
                ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED,
            ),
            icon_color=_color(category.get("color"), AppColors.SECONDARY),
            icon_bgcolor=_color(category.get("bg"), AppColors.PANEL),
            actions=[
                IconAction(
                    icon=ft.Icons.EDIT_OUTLINED,
                    tooltip="Modifier",
                    icon_color=AppColors.SECONDARY,
                    on_click=lambda e, item=category: self.on_rename(item),
                ),
                IconAction(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    tooltip="Supprimer",
                    icon_color=AppColors.ERROR,
                    on_click=lambda e, item=category: self.on_delete(item),
                ),
            ],
            orientation=CardOrientation.HORIZONTAL,
            density=CardDensity.COMPACT,
            bgcolor=AppColors.PANEL,
            shadow=False,
        )

    @staticmethod
    def build_empty_state():
        return ft.Container(
            padding=35,
            alignment=ft.Alignment.CENTER,
            content=ft.Text("Aucun classeur disponible.", italic=True, color=AppColors.TEXT_MUTED),
        )
