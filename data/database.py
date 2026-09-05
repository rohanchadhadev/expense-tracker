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
                is_default INTEGER NOT NULL DEFAULT 0
            )
            """
        )
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER UNIQUE REFERENCES categories(id),
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
        conn.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('currency', 'USD')"
        )
        conn.commit()
    finally:
        conn.close()
