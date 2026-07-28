import flet as ft

from app.theme.tokens import AppColors


class StatusBar(ft.Row):
    def __init__(self):
        self.counter = ft.Text(
            "",
            size=12,
            color=AppColors.TEXT_MUTED,
        )

        self.loading = ft.ProgressRing(
            width=18,
            height=18,
            stroke_width=2,
            visible=False,
        )

        super().__init__(
            controls=[
                self.counter,
                ft.Container(expand=True),
                self.loading,
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def set_count(
        self,
        count: int,
        singular: str,
        plural: str | None = None,
    ) -> None:
        plural = plural or f"{singular}s"

        self.counter.value = (
            f"{count} {singular}"
            if count == 1
            else f"{count} {plural}"
        )

    def set_loading(
        self,
        loading: bool,
        message: str = "Chargement...",
    ) -> None:
        self.loading.visible = loading

        if loading:
            self.counter.value = message

    def clear_message(self) -> None:
        pass