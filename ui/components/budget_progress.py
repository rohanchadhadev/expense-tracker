from typing import Callable, Optional

import flet as ft

from utils.formatting import format_currency


def _progress_color(ratio: float, invert: bool = False) -> str:
    if invert:
        ratio = 1.0 - ratio
    if ratio >= 1.0:
        return ft.Colors.RED_400
    if ratio >= 0.8:
        return ft.Colors.AMBER_600
    return ft.Colors.GREEN_600


def build_budget_progress(
    title: str,
    spent: float,
    limit: float,
    on_edit: Optional[Callable[[ft.Event], None]] = None,
    invert: bool = False,
) -> ft.Control:
    """`invert=True` treats `spent` as a "remaining" amount instead of a "used"
    amount — e.g. for Savings, where a full bar close to `limit` is good (green)
    and a bar drained toward 0 is bad (red), the opposite of a spending budget."""
    ratio = spent / limit if limit > 0 else 0.0
    bar_value = min(ratio, 1.0) if limit > 0 else 0.0
    color = _progress_color(ratio, invert=invert)

    header_controls: list[ft.Control] = [
        ft.Text(
            title,
            weight=ft.FontWeight.BOLD,
            expand=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
        ft.Text(
            f"{format_currency(spent)} / {format_currency(limit)}",
            size=12,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
    ]
    if on_edit:
        header_controls.append(
            ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, on_click=on_edit)
        )

    return ft.Container(
        padding=ft.Padding.symmetric(vertical=8),
        content=ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    controls=header_controls,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.ProgressBar(
                    value=bar_value if limit > 0 else 0,
                    color=color,
                    bar_height=8,
                    border_radius=4,
                ),
            ],
        ),
    )
