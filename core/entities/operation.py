from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from core.utils.validators import Validators


class OperationType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class FinancialOperation:
    id: int
    user_id: int
    type: OperationType
    amount: float
    category: str
    description: Optional[str]
    counterparty: Optional[str]
    operation_date: datetime

    def __post_init__(self):
        Validators.validate_positive(self.amount, "Amount")
        Validators.validate_not_empty(self.category, "Category")

    @classmethod
    def create(
            cls,
            user_id: int,
            type: OperationType,
            amount: float,
            category: str,
            description: Optional[str] = None,
            counterparty: Optional[str] = None,
            operation_date: Optional[datetime] = None
    ) -> "FinancialOperation":
        """
        Фабричный метод для создания операции.

        Args:
            user_id: ID пользователя
            type: Тип операции (доход/расход)
            amount: Сумма операции
            category: Категория операции
            description: Описание операции (опционально)
            counterparty: Контрагент (магазин, организация) - новое поле
            operation_date: Дата операции (по умолчанию текущая)

        Returns:
            FinancialOperation: Созданная операция
        """
        if operation_date is None:
            operation_date = datetime.now()

        # Временно id=0, реальный id присвоит репозиторий
        return cls(
            id=0,
            user_id=user_id,
            type=type,
            amount=amount,
            category=category,
            description=description,
            counterparty=counterparty,
            operation_date=operation_date
        )

    def update_counterparty(self, new_counterparty: str) -> None:
        """
        Обновляет контрагента операции.

        Args:
            new_counterparty: Новый контрагент
        """
        self.counterparty = new_counterparty