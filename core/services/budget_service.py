from datetime import datetime
from typing import List, Dict, Any
from core.entities.budget import BudgetLimit
from core.interfaces.repositories import IBudgetRepository
from core.interfaces.services import IBudgetService, IFinancialCalculator
from core.exceptions import BudgetLimitExceededError


class BudgetService(IBudgetService):
    def __init__(self, budget_repository: IBudgetRepository,
                 calculator: IFinancialCalculator):
        self._budget_repository = budget_repository
        self._calculator = calculator

    def set_budget_limit(self, user_id: int, category: str, monthly_limit: float) -> BudgetLimit:
        """Установить месячный лимит по категории"""
        from core.utils.validators import Validators
        Validators.validate_positive(monthly_limit, "Monthly limit")
        Validators.validate_not_empty(category, "Category")

        existing_limit = self._budget_repository.find_by_user_and_category(user_id, category)

        if existing_limit:
            existing_limit.monthly_limit = monthly_limit
            return self._budget_repository.save(existing_limit)
        else:
            limit = BudgetLimit(
                id=0,
                user_id=user_id,
                category=category,
                monthly_limit=monthly_limit,
                created_at=datetime.now()
            )
            return self._budget_repository.save(limit)

    def get_user_limits(self, user_id: int) -> List[BudgetLimit]:
        """Получить все лимиты пользователя"""
        return self._budget_repository.find_all_by_user(user_id)

    def check_budget_limits(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        """Проверить все лимиты пользователя и вернуть статус"""
        limits = self._budget_repository.find_all_by_user(user_id)
        result = {}

        for limit in limits:
            current_spending = self._calculator.calculate_spending(
                user_id, limit.category, 30
            )

            percentage = self._calculator.calculate_percentage(
                current_spending, limit.monthly_limit
            )

            result[limit.category] = {
                'limit': limit.monthly_limit,
                'current': current_spending,
                'percentage': round(percentage, 2),
                'exceeded': current_spending > limit.monthly_limit,
                'remaining': max(0, limit.monthly_limit - current_spending)
            }

        return result

    def delete_limit(self, user_id: int, category: str) -> bool:
        """Удалить лимит по категории"""
        from core.utils.validators import Validators
        Validators.validate_not_empty(category, "Category")

        limit = self._budget_repository.find_by_user_and_category(user_id, category)
        if limit:
            return self._budget_repository.delete(limit.id)
        return False