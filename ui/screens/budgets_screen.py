import flet as ft

from data import repository as repo
from ui.app_state import AppState
from ui.components.budget_progress import build_budget_progress
from ui.screens.budget_edit_screen import open_budget_dialog
from utils.formatting import month_label, shift_month


def build(state: AppState):
    month = state.selected_month
    categories = repo.list_categories()
    budgets = {b.category_id: b for b in repo.list_budgets()}

    def go_prev(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, -1)
        state.refresh()

    def go_next(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, 1)
        state.refresh()

    overall_budget = budgets.get(None)
    overall_amount = overall_budget.monthly_amount if overall_budget else 0.0
    overall_spent = repo.total_for_month(month)

    rows: list[ft.Control] = [
        build_budget_progress(
            "Overall",
            overall_spent,
            overall_amount,
            on_edit=lambda e: open_budget_dialog(state, None, "Overall", overall_amount),
        ),
        ft.Divider(),
    ]

    for cat in categories:
        b = budgets.get(cat.id)
        amount = b.monthly_amount if b else 0.0
        spent = repo.total_for_category_month(cat.id, month)
        rows.append(
            build_budget_progress(
                cat.name,
                spent,
                amount,
                on_edit=lambda e, c=cat, a=amount: open_budget_dialog(
                    state, c.id, c.name, a
                ),
            )
        )

    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=go_prev),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        f"Budgets — {month_label(month)}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),
                ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=go_next),
            ],
        ),
    )

    content = ft.Column(
        expand=True,
        controls=[
            header,
            ft.ListView(
                expand=True,
                spacing=4,
                padding=ft.Padding.symmetric(horizontal=16),
                controls=rows,
            ),
        ],
    )
    return content, None
