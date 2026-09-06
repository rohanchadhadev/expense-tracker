import datetime

import flet as ft

from data import repository as repo
from ui.app_state import AppState
from ui.components.calendar_grid import build_calendar_grid
from ui.components.confirm_dialog import confirm_action
from ui.components.expense_tile import build_expense_tile
from ui.screens.add_edit_screen import open_expense_dialog
from utils.formatting import (
    current_month,
    format_currency,
    format_date_display,
    month_label,
    shift_month,
)


def build(state: AppState):
    page = state.page
    month = state.selected_month
    expenses = repo.list_expenses(month)
    total = repo.total_for_month(month)

    today_iso = datetime.date.today().isoformat()
    selected_date = state.selected_date
    if selected_date is None and month == current_month():
        selected_date = today_iso

    def go_prev(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, -1)
        state.selected_date = None
        state.refresh()

    def go_next(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, 1)
        state.selected_date = None
        state.refresh()

    def select_date(d: str):
        state.selected_date = d
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

    calendar_grid = build_calendar_grid(month, expenses, selected_date, today_iso, select_date)

    day_expenses = [e for e in expenses if e.date == selected_date] if selected_date else []

    if day_expenses:
        list_body: ft.Control = ft.Container(
            padding=ft.Padding.symmetric(horizontal=16),
            content=ft.Column(
                spacing=8,
                controls=[
                    build_expense_tile(exp, edit_expense, delete_expense)
                    for exp in day_expenses
                ],
            ),
        )
    else:
        message = (
            "No expenses on this date."
            if selected_date
            else "Tap a date above to view its expenses."
        )
        list_body = ft.Container(
            height=180,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.RECEIPT_LONG, size=48, color=ft.Colors.OUTLINE),
                    ft.Text(message, color=ft.Colors.OUTLINE),
                ],
            ),
        )

    day_label = (
        ft.Container(
            padding=ft.Padding.only(left=16, right=16, top=8, bottom=4),
            content=ft.Text(
                format_date_display(selected_date), size=14, weight=ft.FontWeight.BOLD
            ),
        )
        if selected_date
        else ft.Container(height=8)
    )

    content = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[header, calendar_grid, ft.Divider(height=1), day_label, list_body],
    )
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=lambda e: open_expense_dialog(
            state,
            default_date=(
                datetime.date.fromisoformat(selected_date) if selected_date else None
            ),
        ),
    )
    return content, fab
