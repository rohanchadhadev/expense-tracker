import datetime
from typing import Optional

from data.database import get_connection
from data.models import Budget, Category, CategorySpend, Expense

_EXPENSE_SELECT = """
    SELECT e.id, e.amount, e.category_id, e.date, e.note, e.created_at,
           c.name AS category_name, c.color AS category_color
    FROM expenses e
    JOIN categories c ON c.id = e.category_id
"""


def _category_from_row(row) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        color=row["color"],
        is_default=bool(row["is_default"]),
    )


def _expense_from_row(row) -> Expense:
    return Expense(
        id=row["id"],
        amount=row["amount"],
        category_id=row["category_id"],
        category_name=row["category_name"],
        category_color=row["category_color"],
        date=row["date"],
        note=row["note"] or "",
        created_at=row["created_at"],
    )


# --- Categories ---------------------------------------------------------


def list_categories() -> list[Category]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM categories ORDER BY is_default DESC, name ASC"
        ).fetchall()
        return [_category_from_row(r) for r in rows]
    finally:
        conn.close()


def add_category(name: str, color: str) -> Category:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO categories (name, color, is_default) VALUES (?, ?, 0)",
            (name.strip(), color),
        )
        conn.commit()
        return Category(id=cur.lastrowid, name=name.strip(), color=color, is_default=False)
    finally:
        conn.close()


def update_category(category_id: int, name: str, color: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE categories SET name = ?, color = ? WHERE id = ?",
            (name.strip(), color, category_id),
        )
        conn.commit()
    finally:
        conn.close()


def category_in_use(category_id: int) -> bool:
    conn = get_connection()
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE category_id = ?", (category_id,)
        ).fetchone()[0]
        return count > 0
    finally:
        conn.close()


def delete_category(category_id: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT is_default FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if row is None:
            return False, "Category not found."
        if row["is_default"]:
            return False, "Default categories can't be deleted."
        count = conn.execute(
            "SELECT COUNT(*) FROM expenses WHERE category_id = ?", (category_id,)
        ).fetchone()[0]
        if count > 0:
            return False, "Category is used by existing expenses."
        conn.execute("DELETE FROM budgets WHERE category_id = ?", (category_id,))
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return True, ""
    finally:
        conn.close()


# --- Expenses ------------------------------------------------------------


def list_expenses(month: str) -> list[Expense]:
    conn = get_connection()
    try:
        rows = conn.execute(
            _EXPENSE_SELECT
            + " WHERE substr(e.date, 1, 7) = ? ORDER BY e.date DESC, e.id DESC",
            (month,),
        ).fetchall()
        return [_expense_from_row(r) for r in rows]
    finally:
        conn.close()


def get_expense(expense_id: int) -> Optional[Expense]:
    conn = get_connection()
    try:
        row = conn.execute(_EXPENSE_SELECT + " WHERE e.id = ?", (expense_id,)).fetchone()
        return _expense_from_row(row) if row else None
    finally:
        conn.close()


def add_expense(amount: float, category_id: int, date: str, note: str) -> Expense:
    created_at = datetime.datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO expenses (amount, category_id, date, note, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (amount, category_id, date, note.strip(), created_at),
        )
        conn.commit()
        expense_id = cur.lastrowid
    finally:
        conn.close()
    return get_expense(expense_id)


def update_expense(
    expense_id: int, amount: float, category_id: int, date: str, note: str
) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE expenses SET amount = ?, category_id = ?, date = ?, note = ? "
            "WHERE id = ?",
            (amount, category_id, date, note.strip(), expense_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
    finally:
        conn.close()


def total_for_month(month: str) -> float:
    conn = get_connection()
    try:
        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(date, 1, 7) = ?",
            (month,),
        ).fetchone()[0]
        return float(total)
    finally:
        conn.close()


def total_for_category_month(category_id: int, month: str) -> float:
    conn = get_connection()
    try:
        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses "
            "WHERE category_id = ? AND substr(date, 1, 7) = ?",
            (category_id, month),
        ).fetchone()[0]
        return float(total)
    finally:
        conn.close()


def sum_by_category(month: str) -> list[CategorySpend]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT c.id AS category_id, c.name AS category_name,
                   c.color AS category_color, SUM(e.amount) AS total
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            WHERE substr(e.date, 1, 7) = ?
            GROUP BY c.id
            ORDER BY total DESC
            """,
            (month,),
        ).fetchall()
        return [
            CategorySpend(
                category_id=r["category_id"],
                category_name=r["category_name"],
                category_color=r["category_color"],
                total=float(r["total"]),
            )
            for r in rows
        ]
    finally:
        conn.close()


def monthly_totals(months: list[str]) -> dict[str, float]:
    """months must be a list of 'YYYY-MM' strings generated internally (not raw user input)."""
    totals = {m: 0.0 for m in months}
    conn = get_connection()
    try:
        placeholders = ",".join("?" for _ in months)
        rows = conn.execute(
            f"""
            SELECT substr(date, 1, 7) AS month, SUM(amount) AS total
            FROM expenses
            WHERE substr(date, 1, 7) IN ({placeholders})
            GROUP BY month
            """,
            months,
        ).fetchall()
        for r in rows:
            totals[r["month"]] = float(r["total"])
        return totals
    finally:
        conn.close()


# --- Budgets ---------------------------------------------------------------


def list_budgets() -> list[Budget]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT b.id, b.category_id, b.monthly_amount, c.name AS category_name
            FROM budgets b
            LEFT JOIN categories c ON c.id = b.category_id
            """
        ).fetchall()
        return [
            Budget(
                id=r["id"],
                category_id=r["category_id"],
                category_name=r["category_name"],
                monthly_amount=float(r["monthly_amount"]),
            )
            for r in rows
        ]
    finally:
        conn.close()


def get_budget(category_id: Optional[int]) -> Optional[Budget]:
    conn = get_connection()
    try:
        if category_id is None:
            row = conn.execute(
                "SELECT id, category_id, monthly_amount FROM budgets "
                "WHERE category_id IS NULL"
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id, category_id, monthly_amount FROM budgets "
                "WHERE category_id = ?",
                (category_id,),
            ).fetchone()
        if row is None:
            return None
        return Budget(
            id=row["id"],
            category_id=row["category_id"],
            category_name=None,
            monthly_amount=float(row["monthly_amount"]),
        )
    finally:
        conn.close()


def set_budget(category_id: Optional[int], amount: float) -> None:
    conn = get_connection()
    try:
        if category_id is None:
            existing = conn.execute(
                "SELECT id FROM budgets WHERE category_id IS NULL"
            ).fetchone()
        else:
            existing = conn.execute(
                "SELECT id FROM budgets WHERE category_id = ?", (category_id,)
            ).fetchone()
        if existing:
            conn.execute(
                "UPDATE budgets SET monthly_amount = ? WHERE id = ?",
                (amount, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO budgets (category_id, monthly_amount) VALUES (?, ?)",
                (category_id, amount),
            )
        conn.commit()
    finally:
        conn.close()


def delete_budget(category_id: Optional[int]) -> None:
    conn = get_connection()
    try:
        if category_id is None:
            conn.execute("DELETE FROM budgets WHERE category_id IS NULL")
        else:
            conn.execute("DELETE FROM budgets WHERE category_id = ?", (category_id,))
        conn.commit()
    finally:
        conn.close()


# --- Settings ----------------------------------------------------------


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()
