import flet as ft

from data import repository as repo
from ui.app_state import AppState
from ui.components.confirm_dialog import confirm_action
from ui.components.expense_tile import build_expense_tile
from ui.screens.add_edit_screen import open_expense_dialog
from utils.formatting import format_currency, month_label, shift_month


def build(state: AppState):
    page = state.page
    month = state.selected_month
    expenses = repo.list_expenses(month)
    total = repo.total_for_month(month)

    def go_prev(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, -1)
        state.refresh()

    def go_next(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, 1)
        state.refresh()

    def edit_expense(expense):
        open_expense_dialog(state, expense)

    def delete_expense(expense):
        def do_delete():
            repo.delete_expense(expense.id)
            state.refresh()
            state.notify("Expense deleted.")

        confirm_action(
            page,
            "Delete expense?",
            f"Delete the {expense.category_name} expense of "
            f"{format_currency(expense.amount)}?",
            do_delete,
        )

    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=go_prev),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Text(
                                month_label(month),
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
                ft.Text(f"Total spent: {format_currency(total)}", size=16),
            ],
        ),
    )

    if expenses:
        body: ft.Control = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.Padding.symmetric(horizontal=16),
            controls=[
                build_expense_tile(exp, edit_expense, delete_expense) for exp in expenses
            ],
        )
    else:
        body = ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=48, color=ft.Colors.OUTLINE),
                    ft.Text("No expenses yet this month.", color=ft.Colors.OUTLINE),
                ],
            ),
        )

    content = ft.Column(expand=True, controls=[header, body])
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=lambda e: open_expense_dialog(state)
    )
    return content, fab
