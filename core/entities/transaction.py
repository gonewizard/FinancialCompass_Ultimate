# core/entities/transaction.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    """Сущность финансовой операции"""
    user_id: int
    type: str  # 'income' или 'expense'
    amount: float
    category: str
    counterparty: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """Валидация после инициализации"""
        if self.type not in ('income', 'expense'):
            raise ValueError("Type must be 'income' or 'expense'")

        if self.amount <= 0:
            raise ValueError("Amount must be positive")

        if not self.date:
            from datetime import date
            self.date = date.today().isoformat()