from typing import Callable

import flet as ft

from data.models import Expense
from utils.formatting import format_currency, format_date_display


def build_expense_tile(
    expense: Expense,
    on_edit: Callable[[Expense], None],
    on_delete: Callable[[Expense], None],
) -> ft.Control:
    subtitle_parts = [format_date_display(expense.date)]
    if expense.note:
        subtitle_parts.append(expense.note)
    subtitle = "  •  ".join(subtitle_parts)

    return ft.Card(
        content=ft.Container(
            padding=12,
            border_radius=8,
            on_click=lambda e: on_edit(expense),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=10,
                        height=40,
                        bgcolor=expense.category_color,
                        border_radius=6,
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                expense.category_name,
                                weight=ft.FontWeight.BOLD,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                subtitle,
                                size=12,
                                color=ft.Colors.OUTLINE,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.Text(
                        format_currency(expense.amount),
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Delete",
                        on_click=lambda e: on_delete(expense),
                    ),
                ],
            ),
        ),
    )
