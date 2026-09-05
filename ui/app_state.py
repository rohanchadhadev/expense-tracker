from typing import Callable, Optional

import flet as ft

from utils.formatting import current_month


class AppState:
    def __init__(self, page: ft.Page):
        self.page = page
        self.selected_month: str = current_month()
        self.current_index: int = 0
        self._render: Optional[Callable[[int], None]] = None

    def set_render(self, render: Callable[[int], None]) -> None:
        self._render = render

    def refresh(self) -> None:
        if self._render:
            self._render(self.current_index)

    def notify(self, message: str, error: bool = False) -> None:
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_400 if error else ft.Colors.GREEN_600,
        )
        self.page.show_dialog(snack)
