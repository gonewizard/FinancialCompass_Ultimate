from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
from typing import Optional


class PaymentFrequency(Enum):
    """Периодичность платежа"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class ScheduledPayment:
    """
    Сущность планового платежа.

    Attributes:
        id: Уникальный идентификатор
        user_id: Идентификатор пользователя
        name: Название платежа
        amount: Сумма платежа
        category: Категория
        frequency: Периодичность
        next_due_date: Следующая дата платежа
        is_active: Активен ли платеж
        created_at: Дата создания
        description: Описание
    """
    id: int
    user_id: int
    name: str
    amount: float
    category: str
    frequency: PaymentFrequency
    next_due_date: date
    is_active: bool
    created_at: datetime
    description: Optional[str] = None

    def is_due_today(self) -> bool:
        """Проверить, наступила ли дата платежа"""
        return date.today() >= self.next_due_date

    def calculate_next_due_date(self) -> date:
        """Рассчитать следующую дату платежа"""
        from datetime import timedelta

        if self.frequency == PaymentFrequency.DAILY:
            return self.next_due_date + timedelta(days=1)
        elif self.frequency == PaymentFrequency.WEEKLY:
            return self.next_due_date + timedelta(weeks=1)
        elif self.frequency == PaymentFrequency.MONTHLY:
            # Добавляем месяц
            year = self.next_due_date.year
            month = self.next_due_date.month + 1
            if month > 12:
                month = 1
                year += 1
            day = min(self.next_due_date.day, self._days_in_month(year, month))
            return date(year, month, day)
        elif self.frequency == PaymentFrequency.YEARLY:
            return date(self.next_due_date.year + 1, self.next_due_date.month, self.next_due_date.day)

        return self.next_due_date

    def _days_in_month(self, year: int, month: int) -> int:
        """Количество дней в месяце"""
        from calendar import monthrange
        return monthrange(year, month)[1]

    def advance(self) -> None:
        """Перейти к следующему платежу"""
        self.next_due_date = self.calculate_next_due_date()

    @classmethod
    def create(
            cls,
            user_id: int,
            name: str,
            amount: float,
            category: str,
            frequency: PaymentFrequency,
            start_date: date,
            description: Optional[str] = None
    ) -> "ScheduledPayment":
        """Фабричный метод для создания планового платежа"""
        return cls(
            id=0,
            user_id=user_id,
            name=name,
            amount=amount,
            category=category,
            frequency=frequency,
            next_due_date=start_date,
            is_active=True,
            created_at=datetime.now(),
            description=description
        )