import flet as ft

from core.events.event_bus import CategoryCreated, CategoryDeleted, CategoryRenamed, event_bus
from app.theme.tokens import AppColors, AppSpacing
from repositories.category_repository import category_repository
from app.theme.buttons import IconAction, PrimaryButton
from app.theme.cards import AppSection


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

    def build_parent_control(self, category: dict) -> ft.Container:
        children = list(category.get("children") or [])
        leading = self._build_leading(category)
        actions = self._build_parent_actions(category)
        count = int(category.get("document_count", 0))
        subtitle = f"{count} document{'s' if count != 1 else ''}"

        if not children:
            content = ft.ListTile(
                leading=leading,
                title=ft.Text(str(category["name"]), weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),
                subtitle=ft.Text(subtitle, color=AppColors.TEXT_MUTED),
                trailing=actions,
            )
        else:
            child_count = len(children)
            content = ft.ExpansionTile(
                leading=leading,
                title=ft.Text(str(category["name"]), weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),
                subtitle=ft.Text(
                    f"{subtitle} · {child_count} sous-catégorie{'s' if child_count != 1 else ''}",
                    color=AppColors.TEXT_MUTED,
                ),
                trailing=actions,
                expanded=False,
                controls=[self.build_child_tile(child) for child in children],
            )

        return ft.Container(
            bgcolor=AppColors.CARD_BG,
            border=ft.Border.all(1, AppColors.BORDER),
            border_radius=12,
            content=content,
        )

    def _build_leading(self, category: dict) -> ft.Container:
        return ft.Container(
            width=42,
            height=42,
            alignment=ft.Alignment.CENTER,
            border_radius=10,
            bgcolor=_color(category.get("bg"), AppColors.PANEL),
            content=ft.Icon(
                getattr(ft.Icons, str(category.get("icon")), ft.Icons.FOLDER_ROUNDED),
                color=_color(category.get("color"), AppColors.SECONDARY),
            ),
        )

    def _build_parent_actions(self, category: dict) -> ft.Row:
        return ft.Row(
            tight=True,
            spacing=0,
            controls=[
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
            ],
        )

    def build_child_tile(self, category: dict) -> ft.Control:
        count = int(category.get("document_count", 0))
        return ft.Container(
            margin=ft.Margin.only(left=34, right=10, bottom=8),
            border_radius=10,
            bgcolor=AppColors.PANEL,
            content=ft.ListTile(
                leading=ft.Icon(
                    getattr(ft.Icons, str(category.get("icon")), ft.Icons.SUBDIRECTORY_ARROW_RIGHT_ROUNDED),
                    color=_color(category.get("color"), AppColors.SECONDARY),
                ),
                title=ft.Text(str(category["name"]), weight=ft.FontWeight.W_600),
                subtitle=ft.Text(f"{count} document{'s' if count != 1 else ''}"),
                trailing=ft.Row(
                    tight=True,
                    spacing=0,
                    controls=[
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
                ),
            ),
        )

    @staticmethod
    def build_empty_state():
        return ft.Container(
            padding=35,
            alignment=ft.Alignment.CENTER,
            content=ft.Text("Aucun classeur disponible.", italic=True, color=AppColors.TEXT_MUTED),
        )
