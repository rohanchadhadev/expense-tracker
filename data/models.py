from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    id: int
    name: str
    color: str
    is_default: bool
    is_savings: bool = False


@dataclass
class Expense:
    id: int
    amount: float
    category_id: int
    category_name: str
    category_color: str
    date: str  # ISO format: YYYY-MM-DD
    note: str
    created_at: str


@dataclass
class Budget:
    id: int
    category_id: Optional[int]  # None means the overall monthly budget
    category_name: Optional[str]
    monthly_amount: float


@dataclass
class CategorySpend:
    category_id: int
    category_name: str
    category_color: str
    total: float
