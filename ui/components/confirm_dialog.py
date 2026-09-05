from typing import Callable, Optional

import flet as ft


def confirm_action(
    page: ft.Page, title: str, message: str, on_confirm: Callable[[], None]
) -> None:
    def close(e: Optional[ft.Event] = None):
        page.pop_dialog()

    def confirmed(e: ft.Event):
        close()
        on_confirm()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancel", on_click=close),
            ft.FilledButton("Delete", on_click=confirmed),
        ],
    )
    page.show_dialog(dialog)
