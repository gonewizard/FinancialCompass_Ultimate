from typing import List, Optional
from datetime import datetime
from core.entities.goal import FinancialGoal, GoalStatus
from core.interfaces.repositories import IGoalRepository, IOperationRepository
from core.interfaces.services import IGoalService


class GoalService(IGoalService):
    """Сервис для работы с финансовыми целями"""

    def __init__(self, goal_repository: IGoalRepository, operation_repository: IOperationRepository):
        self._goal_repository = goal_repository
        self._operation_repository = operation_repository

    def create_goal(self, user_id: int, name: str, target_amount: float,
                    deadline: Optional[datetime] = None,
                    description: Optional[str] = None) -> FinancialGoal:
        """Создать новую финансовую цель"""
        goal = FinancialGoal.create(
            user_id=user_id,
            name=name,
            target_amount=target_amount,
            deadline=deadline,
            description=description
        )
        return self._goal_repository.save(goal)

    def get_goals(self, user_id: int, status: Optional[GoalStatus] = None) -> List[FinancialGoal]:
        """Получить цели пользователя"""
        return self._goal_repository.find_by_user(user_id, status)

    def get_goal_by_id(self, goal_id: int) -> Optional[FinancialGoal]:
        """Получить цель по ID"""
        return self._goal_repository.find_by_id(goal_id)

    def add_to_goal(self, goal_id: int, amount: float) -> FinancialGoal:
        """Добавить сумму к цели"""
        goal = self._goal_repository.find_by_id(goal_id)
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")

        goal.add_amount(amount)
        return self._goal_repository.save(goal)

    # ========== НОВЫЕ МЕТОДЫ ДЛЯ СВЯЗИ С ОПЕРАЦИЯМИ ==========

    def add_to_goal_with_transaction(self, goal_id: int, transaction_id: int, amount: float) -> FinancialGoal:
        goal = self._goal_repository.find_by_id(goal_id)
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")

        remaining = goal.target_amount - goal.current_amount
        if amount > remaining:
            amount = remaining

        if amount <= 0:
            return goal

        goal.add_amount(amount)
        updated_goal = self._goal_repository.save(goal)

        self._goal_repository.add_goal_transaction(goal_id, transaction_id, amount)

        return updated_goal

    def rollback_goal_by_transaction(self, transaction_id: int) -> List[tuple]:
        """
        Откатить пополнение цели при удалении операции дохода
        Возвращает список (goal_id, amount) для обновлённых целей
        """
        # Получаем все связи этой операции с целями
        goal_transactions = self._goal_repository.get_goal_transactions_by_transaction(transaction_id)

        results = []
        for goal_id, amount in goal_transactions:
            goal = self._goal_repository.find_by_id(goal_id)
            if goal:
                # Уменьшаем текущую сумму цели
                new_amount = max(0, goal.current_amount - amount)
                goal.current_amount = new_amount

                # Если цель была достигнута, обновляем статус
                if goal.status == GoalStatus.COMPLETED and new_amount < goal.target_amount:
                    goal.status = GoalStatus.ACTIVE

                self._goal_repository.save(goal)
                results.append((goal_id, amount))

        # Удаляем связи
        self._goal_repository.delete_goal_transactions_by_transaction(transaction_id)

        return results

    def get_goal_contributions(self, goal_id: int) -> List[dict]:
        """
        Получить историю пополнений цели с деталями операций
        """
        return self._goal_repository.get_goal_contributions_with_details(goal_id)

    # ========== ОСТАВШИЕСЯ МЕТОДЫ БЕЗ ИЗМЕНЕНИЙ ==========

    def delete_goal(self, goal_id: int) -> bool:
        """Удалить цель"""
        return self._goal_repository.delete(goal_id)

    def cancel_goal(self, goal_id: int) -> FinancialGoal:
        """Отменить цель"""
        goal = self._goal_repository.find_by_id(goal_id)
        if not goal:
            raise ValueError(f"Goal with ID {goal_id} not found")

        goal.status = GoalStatus.CANCELLED
        return self._goal_repository.save(goal)