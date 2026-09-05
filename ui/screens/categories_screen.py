import flet as ft

from data import repository as repo
from data.models import Category
from ui.app_state import AppState
from ui.components.confirm_dialog import confirm_action
from ui.screens.category_edit_screen import open_category_dialog


def build(state: AppState):
    page = state.page
    categories = repo.list_categories()

    def edit_cat(cat: Category):
        open_category_dialog(state, cat)

    def delete_cat(cat: Category):
        def do_delete():
            ok, reason = repo.delete_category(cat.id)
            state.refresh()
            state.notify("Category deleted." if ok else reason, error=not ok)

        confirm_action(
            page, "Delete category?", f"Delete '{cat.name}'?", do_delete
        )

    tiles = []
    for cat in categories:
        actions: list[ft.Control] = []
        if cat.is_default:
            actions.append(ft.Text("Default", size=12, color=ft.Colors.OUTLINE))
        else:
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_size=18,
                    on_click=lambda e, c=cat: edit_cat(c),
                )
            )
            actions.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    on_click=lambda e, c=cat: delete_cat(c),
                )
            )
        tiles.append(
            ft.Card(
                content=ft.Container(
                    padding=12,
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=24, height=24, bgcolor=cat.color, border_radius=12
                            ),
                            ft.Text(
                                cat.name,
                                expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            *actions,
                        ],
                    ),
                )
            )
        )

    content = ft.Column(
        expand=True,
        controls=[
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                content=ft.Text("Categories", size=18, weight=ft.FontWeight.BOLD),
            ),
            ft.ListView(
                expand=True,
                spacing=8,
                padding=ft.Padding.symmetric(horizontal=16),
                controls=tiles,
            ),
        ],
    )
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=lambda e: open_category_dialog(state)
    )
    return content, fab
