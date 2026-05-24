from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime, date
from core.entities.operation import FinancialOperation
from core.entities.user import User
from core.entities.budget import BudgetLimit
from core.entities.goal import FinancialGoal, GoalStatus
from core.entities.scheduled_payment import ScheduledPayment
from core.entities.auto_category import AutoCategoryRule
from core.entities.transaction import Transaction


class IUserRepository(ABC):
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_all_users(self) -> List[User]:
        pass

    @abstractmethod
    def get_users_count(self) -> int:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_initial_balance(self, user_id: int) -> float:
        pass

    @abstractmethod
    def update_initial_balance(self, user_id: int, balance: float) -> bool:
        pass

class IOperationRepository(ABC):
    @abstractmethod
    def save(self, operation: FinancialOperation) -> FinancialOperation:
        pass

    @abstractmethod
    def find_by_user_and_period(self, user_id: int, start_date: datetime, end_date: datetime) -> List[
        FinancialOperation]:
        pass

    @abstractmethod
    def get_operations_count(self) -> int:
        pass

    @abstractmethod
    def get_total_income(self) -> float:
        pass

    @abstractmethod
    def get_total_expenses(self) -> float:
        pass

    @abstractmethod
    def get_all_operations(self) -> List[FinancialOperation]:
        pass

    @abstractmethod
    def find_by_id(self, operation_id: int) -> Optional[FinancialOperation]:
        pass

    @abstractmethod
    def delete(self, operation_id: int) -> bool:
        pass

    @abstractmethod
    def get_operations_by_user(self, user_id: int) -> List[FinancialOperation]:
        pass

    @abstractmethod
    def get_balance(self, user_id: int) -> float:
        pass


class IBudgetRepository(ABC):
    @abstractmethod
    def save(self, limit: BudgetLimit) -> BudgetLimit:
        pass

    @abstractmethod
    def find_by_user_and_category(self, user_id: int, category: str) -> Optional[BudgetLimit]:
        pass

    @abstractmethod
    def find_all_by_user(self, user_id: int) -> List[BudgetLimit]:
        pass

    @abstractmethod
    def delete(self, limit_id: int) -> bool:
        pass

    @abstractmethod
    def delete_by_user_and_category(self, user_id: int, category: str) -> bool:
        pass


class IGoalRepository(ABC):
    """Репозиторий для финансовых целей"""

    @abstractmethod
    def save(self, goal: FinancialGoal) -> FinancialGoal:
        """Сохранить цель"""
        pass

    @abstractmethod
    def find_by_id(self, goal_id: int) -> Optional[FinancialGoal]:
        """Найти цель по ID"""
        pass

    @abstractmethod
    def find_by_user(self, user_id: int, status: Optional[GoalStatus] = None) -> List[FinancialGoal]:
        """Найти все цели пользователя"""
        pass

    @abstractmethod
    def delete(self, goal_id: int) -> bool:
        """Удалить цель"""
        pass

    @abstractmethod
    def update_amount(self, goal_id: int, amount: float) -> bool:
        """Обновить текущую сумму цели"""
        pass

    @abstractmethod
    def add_goal_transaction(self, goal_id: int, transaction_id: int, amount: float) -> None:
        """Привязать операцию дохода к цели"""
        pass

    @abstractmethod
    def get_goal_transactions_by_transaction(self, transaction_id: int) -> List[tuple]:
        """Получить все цели, связанные с операцией"""
        pass

    @abstractmethod
    def delete_goal_transactions_by_transaction(self, transaction_id: int) -> None:
        """Удалить все связи операции с целями"""
        pass

    @abstractmethod
    def get_goal_contributions_with_details(self, goal_id: int) -> List[dict]:
        """Получить историю пополнений цели с деталями операций"""
        pass


class IScheduledPaymentRepository(ABC):
    """Репозиторий для плановых платежей"""

    @abstractmethod
    def save(self, payment: ScheduledPayment) -> ScheduledPayment:
        """Сохранить плановый платеж"""
        pass

    @abstractmethod
    def find_by_id(self, payment_id: int) -> Optional[ScheduledPayment]:
        """Найти платеж по ID"""
        pass

    @abstractmethod
    def find_by_user(self, user_id: int, is_active: Optional[bool] = None) -> List[ScheduledPayment]:
        """Найти все платежи пользователя"""
        pass

    @abstractmethod
    def find_due_payments(self, user_id: int, due_date: date) -> List[ScheduledPayment]:
        """Найти платежи, подлежащие оплате в указанную дату"""
        pass

    @abstractmethod
    def delete(self, payment_id: int) -> bool:
        """Удалить плановый платеж"""
        pass

    @abstractmethod
    def update_next_due_date(self, payment_id: int, next_due_date: date) -> bool:
        """Обновить следующую дату платежа"""
        pass


class IAutoCategoryRepository(ABC):
    @abstractmethod
    def save(self, rule: AutoCategoryRule) -> AutoCategoryRule:
        pass

    @abstractmethod
    def find_by_user_and_counterparty(self, user_id: int, counterparty: str) -> Optional[AutoCategoryRule]:
        pass

    @abstractmethod
    def find_by_user(self, user_id: int) -> List[AutoCategoryRule]:
        pass

    @abstractmethod
    def delete(self, rule_id: int) -> bool:
        pass

    @abstractmethod
    def increment_use_count(self, rule_id: int) -> bool:
        pass

class ITransactionService(ABC):
    """Интерфейс сервиса операций"""

    @abstractmethod
    def create_transaction(self, user_id: int, transaction_type: str, amount: float,
                           category: str, counterparty: str = None, date: str = None,
                           description: str = None) -> int:
        pass

    @abstractmethod
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        pass

    @abstractmethod
    def get_user_transactions(self, user_id: int) -> List[Transaction]:
        pass

    @abstractmethod
    def update_transaction(self, transaction_id: int, user_id: int, **kwargs) -> bool:
        pass

    @abstractmethod
    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def search_transactions(self, user_id: int, filters: Dict) -> List[Transaction]:
        pass

    @abstractmethod
    def get_balance(self, user_id: int) -> float:
        pass

    @abstractmethod
    def get_total_income(self, user_id: int, date_from: str = None, date_to: str = None) -> float:
        pass

    @abstractmethod
    def get_total_expense(self, user_id: int, date_from: str = None, date_to: str = None) -> float:
        pass

    @abstractmethod
    def get_top_counterparties(self, user_id: int, limit: int = 5) -> List[tuple]:
        pass

    @abstractmethod
    def get_expenses_by_category(self, user_id: int, date_from: str = None, date_to: str = None) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_balance_history(self, user_id: int, days: int = 30) -> List[Dict]:
        pass

    @abstractmethod
    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        pass