from typing import Optional

import flet as ft

from data import repository as repo
from data.models import Category
from ui.app_state import AppState

PALETTE = [
    ("Red", "#EF5350"),
    ("Orange", "#FF7043"),
    ("Amber", "#FFCA28"),
    ("Green", "#66BB6A"),
    ("Teal", "#26A69A"),
    ("Blue", "#42A5F5"),
    ("Indigo", "#5C6BC0"),
    ("Purple", "#AB47BC"),
    ("Pink", "#EC407A"),
    ("Grey", "#78909C"),
]


def open_category_dialog(state: AppState, category: Optional[Category] = None) -> None:
    page = state.page
    is_edit = category is not None

    name_field = ft.TextField(
        label="Name", value=category.name if category else "", autofocus=True
    )
    color_dropdown = ft.Dropdown(
        label="Color",
        value=category.color if category else PALETTE[0][1],
        options=[ft.DropdownOption(key=hex_, text=name) for name, hex_ in PALETTE],
    )
    error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)

    def close(e: Optional[ft.Event] = None):
        page.pop_dialog()

    def save(e: ft.Event):
        name = (name_field.value or "").strip()
        if not name:
            error_text.value = "Name can't be empty."
            error_text.visible = True
            error_text.update()
            return

        color = color_dropdown.value
        if is_edit:
            repo.update_category(category.id, name, color)
        else:
            repo.add_category(name, color)

        close()
        state.refresh()

    dialog_width = min(360, (page.width or 400) - 48)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit category" if is_edit else "Add category"),
        content=ft.Column(
            width=dialog_width,
            tight=True,
            spacing=14,
            controls=[name_field, color_dropdown, error_text],
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close),
            ft.FilledButton("Save", on_click=save),
        ],
    )
    page.show_dialog(dialog)
