import flet as ft

from data import repository as repo
from data.database import init_db
from ui.app_state import AppState
from ui.screens import budgets_screen, categories_screen, charts_screen, home_screen
from ui.screens.settings_dialog import open_settings_dialog
from utils.formatting import set_currency

SCREENS = [home_screen, charts_screen, budgets_screen, categories_screen]


def main(page: ft.Page):
    init_db()
    set_currency(repo.get_setting("currency", "USD"))
    page.title = "Expense Tracker"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO, use_material3=True)

    state = AppState(page)
    body = ft.Column(expand=True)
    page.appbar = ft.AppBar(
        title=ft.Text("Expense Tracker"),
        center_title=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                tooltip="Settings",
                on_click=lambda e: open_settings_dialog(state),
            ),
        ],
    )

    def render(index: int):
        state.current_index = index
        content, fab = SCREENS[index].build(state)
        body.controls = [content]
        page.floating_action_button = fab
        page.navigation_bar.selected_index = index
        page.update()

    state.set_render(render)

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART, label="Charts"),
            ft.NavigationBarDestination(icon=ft.Icons.SAVINGS, label="Budgets"),
            ft.NavigationBarDestination(icon=ft.Icons.CATEGORY, label="Categories"),
        ],
        selected_index=0,
        on_change=lambda e: render(e.control.selected_index),
    )
    page.add(body)
    render(0)


ft.run(main)
