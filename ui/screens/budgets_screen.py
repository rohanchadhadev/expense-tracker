from typing import Optional

import flet as ft

from data import repository as repo
from ui.app_state import AppState
from ui.components.budget_progress import build_budget_progress
from ui.screens.budget_edit_screen import open_budget_dialog
from utils.formatting import month_label, shift_month


def build(state: AppState):
    page = state.page
    month = state.selected_month
    prev_month = shift_month(month, -1)
    all_categories = repo.list_categories()
    savings_category = next((c for c in all_categories if c.is_savings), None)
    categories = [c for c in all_categories if not c.is_savings]
    budgets = {b.category_id: b for b in repo.list_budgets(month)}

    def go_prev(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, -1)
        state.refresh()

    def go_next(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, 1)
        state.refresh()

    def copy_from_previous(e: ft.Event):
        prev_budgets = repo.list_budgets(prev_month)
        if not prev_budgets:
            state.notify(
                f"No budgets set for {month_label(prev_month)} to copy.", error=True
            )
            return

        def do_copy(ev: Optional[ft.Event] = None):
            page.pop_dialog()
            count = repo.copy_budgets(prev_month, month)
            state.notify(f"Copied {count} budget(s) from {month_label(prev_month)}.")
            state.refresh()

        def cancel(ev: Optional[ft.Event] = None):
            page.pop_dialog()

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Copy previous month's budgets?"),
                content=ft.Text(
                    f"This copies budgets from {month_label(prev_month)} into "
                    f"{month_label(month)}, overwriting any values already set "
                    f"this month."
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel),
                    ft.FilledButton("Copy", on_click=do_copy),
                ],
            )
        )

    overall_budget = budgets.get(None)
    overall_amount = overall_budget.monthly_amount if overall_budget else 0.0
    overall_spent = repo.total_for_month(month)

    rows: list[ft.Control] = [
        build_budget_progress(
            "Overall",
            overall_spent,
            overall_amount,
            on_edit=lambda e: open_budget_dialog(
                state, None, "Overall", overall_amount, month
            ),
        ),
        ft.Divider(),
    ]

    total_overage = 0.0
    for cat in categories:
        b = budgets.get(cat.id)
        amount = b.monthly_amount if b else 0.0
        spent = repo.total_for_category_month(cat.id, month)
        if amount > 0 and spent > amount:
            total_overage += spent - amount
        rows.append(
            build_budget_progress(
                cat.name,
                spent,
                amount,
                on_edit=lambda e, c=cat, a=amount: open_budget_dialog(
                    state, c.id, c.name, a, month
                ),
            )
        )

    if savings_category is not None:
        savings_budget = budgets.get(savings_category.id)
        savings_target = savings_budget.monthly_amount if savings_budget else 0.0
        rows.append(ft.Divider())
        rows.append(
            build_budget_progress(
                "Savings",
                total_overage,
                savings_target,
                on_edit=lambda e, a=savings_target: open_budget_dialog(
                    state, savings_category.id, "Savings", a, month
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
    )

    copy_row = ft.Container(
        padding=ft.Padding.only(left=16, right=16, bottom=4),
        alignment=ft.Alignment.CENTER_RIGHT,
        content=ft.TextButton(
            content=ft.Row(
                spacing=4,
                tight=True,
                controls=[
                    ft.Icon(ft.Icons.CONTENT_COPY, size=14),
                    ft.Text("Copy last month's budgets", size=12),
                ],
            ),
            on_click=copy_from_previous,
        ),
    )

    content = ft.Column(
        expand=True,
        controls=[
            header,
            copy_row,
            ft.ListView(
                expand=True,
                spacing=4,
                padding=ft.Padding.symmetric(horizontal=16),
                controls=rows,
            ),
        ],
    )
    return content, None
