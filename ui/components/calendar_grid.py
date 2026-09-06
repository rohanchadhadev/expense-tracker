import calendar
from typing import Callable, Optional

import flet as ft

from data.models import Expense

_WEEKDAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"]


def build_calendar_grid(
    month: str,
    expenses: list[Expense],
    selected_date: Optional[str],
    today_iso: str,
    on_select: Callable[[str], None],
) -> ft.Control:
    year, mon = (int(p) for p in month.split("-"))
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, mon)

    colors_by_date: dict[str, list[str]] = {}
    for exp in expenses:
        seen = colors_by_date.setdefault(exp.date, [])
        if exp.category_color not in seen:
            seen.append(exp.category_color)

    header_row = ft.Row(
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(
                    label, size=12, color=ft.Colors.OUTLINE, weight=ft.FontWeight.BOLD
                ),
            )
            for label in _WEEKDAY_LABELS
        ]
    )

    rows: list[ft.Control] = [header_row]
    for week in weeks:
        cells: list[ft.Control] = []
        for day in week:
            if day == 0:
                cells.append(ft.Container(expand=True, height=48))
                continue

            date_iso = f"{month}-{day:02d}"
            is_today = date_iso == today_iso
            is_selected = date_iso == selected_date
            dots = [
                ft.Container(width=6, height=6, border_radius=3, bgcolor=c)
                for c in colors_by_date.get(date_iso, [])[:4]
            ]

            cells.append(
                ft.Container(
                    expand=True,
                    height=48,
                    border_radius=8,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER if is_selected else None,
                    on_click=lambda e, d=date_iso: on_select(d),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                        controls=[
                            ft.Text(
                                str(day),
                                size=13,
                                weight=(
                                    ft.FontWeight.BOLD if is_today else ft.FontWeight.NORMAL
                                ),
                                color=(
                                    ft.Colors.PRIMARY if is_today and not is_selected else None
                                ),
                            ),
                            ft.Row(spacing=2, alignment=ft.MainAxisAlignment.CENTER, height=6, controls=dots),
                        ],
                    ),
                )
            )
        rows.append(ft.Row(controls=cells))

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=12),
        content=ft.Column(spacing=4, controls=rows),
    )
