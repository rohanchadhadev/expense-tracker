from typing import Optional

import flet as ft

from data import repository as repo
from ui.app_state import AppState
from utils.formatting import get_currency_symbol


def open_budget_dialog(
    state: AppState, category_id: Optional[int], label: str, current_amount: float
) -> None:
    page = state.page

    amount_field = ft.TextField(
        label=f"Monthly budget for {label}",
        value=f"{current_amount:.2f}" if current_amount else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix=get_currency_symbol(),
        autofocus=True,
    )
    error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)

    def close(e: Optional[ft.Event] = None):
        page.pop_dialog()

    def clear(e: ft.Event):
        repo.delete_budget(category_id)
        close()
        state.refresh()

    def save(e: ft.Event):
        raw = (amount_field.value or "").strip()
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            error_text.value = "Enter a valid amount greater than 0."
            error_text.visible = True
            error_text.update()
            return

        repo.set_budget(category_id, amount)
        close()
        state.refresh()

    actions = [ft.TextButton("Cancel", on_click=close)]
    if current_amount:
        actions.append(ft.TextButton("Remove", on_click=clear))
    actions.append(ft.FilledButton("Save", on_click=save))

    dialog_width = min(360, (page.width or 400) - 48)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Set budget: {label}"),
        content=ft.Column(
            width=dialog_width, tight=True, spacing=14, controls=[amount_field, error_text]
        ),
        actions=actions,
    )
    page.show_dialog(dialog)
