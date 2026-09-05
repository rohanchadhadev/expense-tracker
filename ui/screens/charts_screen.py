import flet as ft
import flet_charts as fch

from data import repository as repo
from ui.app_state import AppState
from utils.formatting import (
    format_currency,
    month_label,
    month_label_short,
    shift_month,
    trailing_months,
)


def build(state: AppState):
    month = state.selected_month

    def go_prev(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, -1)
        state.refresh()

    def go_next(e: ft.Event):
        state.selected_month = shift_month(state.selected_month, 1)
        state.refresh()

    category_spend = repo.sum_by_category(month)
    category_spend_no_bills = [cs for cs in category_spend if cs.category_name != "Bills"]

    def build_pie_section(spend, empty_message):
        if not spend:
            return ft.Container(
                height=220,
                alignment=ft.Alignment.CENTER,
                content=ft.Text(empty_message, color=ft.Colors.OUTLINE),
            )
        pie = fch.PieChart(
            sections=[
                fch.PieChartSection(
                    value=cs.total,
                    color=cs.category_color,
                    title=cs.category_name,
                    radius=70,
                    title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE),
                )
                for cs in spend
            ],
            sections_space=2,
            center_space_radius=30,
        )
        legend = ft.Column(
            spacing=4,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=cs.category_color,
                            border_radius=3,
                        ),
                        ft.Text(
                            cs.category_name,
                            expand=True,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(format_currency(cs.total)),
                    ]
                )
                for cs in spend
            ],
        )
        return ft.Column(
            spacing=12,
            controls=[
                ft.Container(height=220, content=pie),
                legend,
            ],
        )

    pie_section_no_bills = build_pie_section(
        category_spend_no_bills, "No expenses (excluding Bills) this month yet."
    )
    pie_section = build_pie_section(category_spend, "No expenses this month yet.")

    months = trailing_months(month, 6)
    totals = repo.monthly_totals(months)
    bar = fch.BarChart(
        groups=[
            fch.BarChartGroup(
                x=i,
                rods=[
                    fch.BarChartRod(
                        from_y=0,
                        to_y=totals[m],
                        color=ft.Colors.INDIGO,
                        width=18,
                    )
                ],
            )
            for i, m in enumerate(months)
        ],
        bottom_axis=fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(value=i, label=month_label_short(m))
                for i, m in enumerate(months)
            ],
            show_labels=True,
        ),
    )

    content = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Container(
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
            ),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16, vertical=4),
                content=ft.Text(
                    "By category (excluding Bills)", size=16, weight=ft.FontWeight.BOLD
                ),
            ),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16),
                content=pie_section_no_bills,
            ),
            ft.Divider(),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16, vertical=4),
                content=ft.Text(
                    "By category (including Bills)", size=16, weight=ft.FontWeight.BOLD
                ),
            ),
            ft.Container(padding=ft.Padding.symmetric(horizontal=16), content=pie_section),
            ft.Divider(),
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=16),
                content=ft.Text("Last 6 months", size=16, weight=ft.FontWeight.BOLD),
            ),
            ft.Container(
                height=220,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                content=bar,
            ),
        ],
    )
    return content, None
