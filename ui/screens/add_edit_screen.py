import datetime
from typing import Optional

import flet as ft

from data import repository as repo
from data.models import Expense
from ui.app_state import AppState
from utils.formatting import (
    format_currency,
    format_date_display,
    get_currency_symbol,
    month_label,
)


def _to_date(value) -> datetime.date:
    if isinstance(value, datetime.datetime):
        return value.date()
    return value


def _check_budget_alert(state: AppState, category_id: int, date_value: str) -> None:
    month = date_value[:7]

    cat_budget = repo.get_budget(category_id)
    if cat_budget:
        spent = repo.total_for_category_month(category_id, month)
        if spent > cat_budget.monthly_amount:
            categories = {c.id: c for c in repo.list_categories()}
            name = categories[category_id].name if category_id in categories else "This category"
            state.notify(
                f"Over budget: {name} spent {format_currency(spent)} of "
                f"{format_currency(cat_budget.monthly_amount)} for {month_label(month)}.",
                error=True,
            )
            return

    overall_budget = repo.get_budget(None)
    if overall_budget:
        total = repo.total_for_month(month)
        if total > overall_budget.monthly_amount:
            state.notify(
                f"Over budget: total spending is {format_currency(total)} of "
                f"{format_currency(overall_budget.monthly_amount)} for {month_label(month)}.",
                error=True,
            )


def open_expense_dialog(state: AppState, expense: Optional[Expense] = None) -> None:
    page = state.page
    categories = repo.list_categories()
    if not categories:
        state.notify("Add a category first.", error=True)
        return

    is_edit = expense is not None
    initial_date = (
        datetime.date.fromisoformat(expense.date)
        if expense
        else datetime.date.today()
    )
    selected_date = {"value": initial_date}

    amount_field = ft.TextField(
        label="Amount",
        value=f"{expense.amount:.2f}" if expense else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix=get_currency_symbol(),
        autofocus=not is_edit,
    )
    category_dropdown = ft.Dropdown(
        label="Category",
        value=str(expense.category_id if expense else categories[0].id),
        options=[ft.DropdownOption(key=str(c.id), text=c.name) for c in categories],
    )
    note_field = ft.TextField(
        label="Note (optional)",
        value=expense.note if expense else "",
    )
    date_text = ft.Text(format_date_display(selected_date["value"].isoformat()))
    error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)

    def on_date_change(e: ft.Event):
        if date_picker.value:
            selected_date["value"] = _to_date(date_picker.value)
            date_text.value = format_date_display(selected_date["value"].isoformat())
            date_text.update()

    date_picker = ft.DatePicker(
        value=selected_date["value"],
        first_date=datetime.date(2000, 1, 1),
        last_date=datetime.date(2100, 1, 1),
        on_change=on_date_change,
    )

    def pick_date(e: ft.Event):
        page.show_dialog(date_picker)

    def close_dialog(e: Optional[ft.Event] = None):
        page.pop_dialog()

    def save(e: ft.Event):
        raw_amount = (amount_field.value or "").strip().replace(",", "")
        try:
            amount = float(raw_amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            error_text.value = "Enter a valid amount greater than 0."
            error_text.visible = True
            error_text.update()
            return

        category_id = int(category_dropdown.value)
        date_value = selected_date["value"].isoformat()
        note = note_field.value or ""

        if is_edit:
            repo.update_expense(expense.id, amount, category_id, date_value, note)
        else:
            repo.add_expense(amount, category_id, date_value, note)

        close_dialog()
        state.refresh()
        _check_budget_alert(state, category_id, date_value)

    dialog_width = min(360, (page.width or 400) - 48)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit expense" if is_edit else "Add expense"),
        content=ft.Column(
            width=dialog_width,
            tight=True,
            spacing=14,
            controls=[
                amount_field,
                category_dropdown,
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Date:"),
                        date_text,
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            tooltip="Pick date",
                            on_click=pick_date,
                        ),
                    ],
                ),
                note_field,
                error_text,
            ],
        ),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.FilledButton("Save", on_click=save),
        ],
    )

    page.show_dialog(dialog)
