import calendar
import datetime

CURRENCIES = [
    ("USD", "$", "US Dollar"),
    ("EUR", "€", "Euro"),
    ("GBP", "£", "British Pound"),
    ("INR", "₹", "Indian Rupee"),
    ("JPY", "¥", "Japanese Yen"),
    ("CNY", "¥", "Chinese Yuan"),
    ("CAD", "C$", "Canadian Dollar"),
    ("AUD", "A$", "Australian Dollar"),
]
_CODE_TO_SYMBOL = {code: symbol for code, symbol, _ in CURRENCIES}

_current_symbol = "$"


def set_currency(code: str) -> None:
    global _current_symbol
    _current_symbol = _CODE_TO_SYMBOL.get(code, "$")


def get_currency_symbol() -> str:
    return _current_symbol


def format_currency(amount: float) -> str:
    return f"{_current_symbol}{amount:,.2f}"


def month_label(month: str) -> str:
    """month is 'YYYY-MM' -> 'September 2026'."""
    year, mon = month.split("-")
    return f"{calendar.month_name[int(mon)]} {year}"


def month_label_short(month: str) -> str:
    """month is 'YYYY-MM' -> 'Sep'."""
    _, mon = month.split("-")
    return calendar.month_abbr[int(mon)]


def shift_month(month: str, delta: int) -> str:
    year, mon = (int(p) for p in month.split("-"))
    total = year * 12 + (mon - 1) + delta
    new_year, new_mon = divmod(total, 12)
    return f"{new_year:04d}-{new_mon + 1:02d}"


def trailing_months(month: str, count: int) -> list[str]:
    return [shift_month(month, -i) for i in reversed(range(count))]


def current_month() -> str:
    return datetime.date.today().strftime("%Y-%m")


def format_date_display(date_str: str) -> str:
    d = datetime.date.fromisoformat(date_str)
    return d.strftime("%b %d, %Y")
