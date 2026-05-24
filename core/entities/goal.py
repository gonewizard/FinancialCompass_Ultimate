from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class GoalStatus(Enum):
    """Статус финансовой цели"""
    ACTIVE = "active"  # Активна
    COMPLETED = "completed"  # Достигнута
    CANCELLED = "cancelled"  # Отменена


@dataclass
class FinancialGoal:
    """
    Сущность финансовой цели.

    Attributes:
        id: Уникальный идентификатор цели
        user_id: Идентификатор пользователя
        name: Название цели
        target_amount: Целевая сумма
        current_amount: Текущая накопленная сумма
        deadline: Срок достижения (опционально)
        status: Статус цели
        created_at: Дата создания
        description: Описание цели
    """
    id: int
    user_id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime]
    status: GoalStatus
    created_at: datetime
    description: Optional[str] = None

    @property
    def progress_percent(self) -> float:
        """Процент выполнения цели"""
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0.0

    @property
    def remaining_amount(self) -> float:
        """Оставшаяся сумма для достижения цели"""
        return max(0, self.target_amount - self.current_amount)

    @property
    def is_completed(self) -> bool:
        """Достигнута ли цель"""
        return self.current_amount >= self.target_amount

    def add_amount(self, amount: float) -> float:
        """
        Добавить сумму к цели.

        Returns:
            float: Новая текущая сумма
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        self.current_amount += amount

        # Если цель достигнута, обновляем статус
        if self.is_completed and self.status == GoalStatus.ACTIVE:
            self.status = GoalStatus.COMPLETED

        return self.current_amount

    @classmethod
    def create(
            cls,
            user_id: int,
            name: str,
            target_amount: float,
            deadline: Optional[datetime] = None,
            description: Optional[str] = None
    ) -> "FinancialGoal":
        """Фабричный метод для создания новой цели"""
        return cls(
            id=0,
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            current_amount=0.0,
            deadline=deadline,
            status=GoalStatus.ACTIVE,
            created_at=datetime.now(),
            description=description
        )