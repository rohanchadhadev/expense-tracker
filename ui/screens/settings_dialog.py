import flet as ft

from data import repository as repo
from ui.app_state import AppState
from utils.formatting import CURRENCIES, set_currency


def open_settings_dialog(state: AppState) -> None:
    page = state.page
    current_code = repo.get_setting("currency", "USD")

    currency_dropdown = ft.Dropdown(
        label="Currency",
        value=current_code,
        options=[
            ft.DropdownOption(key=code, text=f"{code} ({symbol}) — {name}")
            for code, symbol, name in CURRENCIES
        ],
    )

    def close(e=None):
        page.pop_dialog()

    def save(e: ft.Event):
        code = currency_dropdown.value or "USD"
        repo.set_setting("currency", code)
        set_currency(code)
        close()
        state.refresh()

    dialog_width = min(360, (page.width or 400) - 48)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Settings"),
        content=ft.Column(
            width=dialog_width, tight=True, spacing=14, controls=[currency_dropdown]
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close),
            ft.FilledButton("Save", on_click=save),
        ],
    )
    page.show_dialog(dialog)
