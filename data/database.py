import datetime
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

DEFAULT_CATEGORIES = [
    ("Food", "#FF7043"),
    ("Transport", "#42A5F5"),
    ("Bills", "#AB47BC"),
    ("Shopping", "#66BB6A"),
    ("Entertainment", "#FFCA28"),
    ("Other", "#78909C"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL,
                is_default INTEGER NOT NULL DEFAULT 0,
                is_savings INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        _migrate_categories_table(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category_id INTEGER NOT NULL REFERENCES categories(id),
                date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        _migrate_budgets_table(conn)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id),
                month TEXT NOT NULL,
                monthly_amount REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        existing = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        if existing == 0:
            conn.executemany(
                "INSERT INTO categories (name, color, is_default) VALUES (?, ?, 1)",
                DEFAULT_CATEGORIES,
            )
        has_savings = conn.execute(
            "SELECT COUNT(*) FROM categories WHERE is_savings = 1"
        ).fetchone()[0]
        if not has_savings:
            conn.execute(
                "INSERT INTO categories (name, color, is_default, is_savings) "
                "VALUES ('Savings', '#26A69A', 1, 1)"
            )
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', 'USD')"
        )
        conn.commit()
    finally:
        conn.close()


def _migrate_categories_table(conn: sqlite3.Connection) -> None:
    """Older installs' categories table predates the is_savings column."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(categories)").fetchall()}
    if "is_savings" not in columns:
        conn.execute("ALTER TABLE categories ADD COLUMN is_savings INTEGER NOT NULL DEFAULT 0")


def _migrate_budgets_table(conn: sqlite3.Connection) -> None:
    """Budgets used to be a single value per category shared across all months.
    Rebuild the table with a `month` column, carrying old values into the
    current month so per-month budgets can start from there."""
    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'budgets'"
    ).fetchone()
    if not table_exists:
        return
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(budgets)").fetchall()}
    if "month" in columns:
        return

    current_month = datetime.date.today().strftime("%Y-%m")
    old_rows = conn.execute("SELECT category_id, monthly_amount FROM budgets").fetchall()
    conn.execute("DROP TABLE budgets")
    conn.execute(
        """
        CREATE TABLE budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER REFERENCES categories(id),
            month TEXT NOT NULL,
            monthly_amount REAL NOT NULL
        )
        """
    )
    for row in old_rows:
        conn.execute(
            "INSERT INTO budgets (category_id, month, monthly_amount) VALUES (?, ?, ?)",
            (row["category_id"], current_month, row["monthly_amount"]),
        )
