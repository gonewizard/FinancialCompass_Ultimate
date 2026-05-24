from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from core.entities.user import User, UserRole
from core.entities.operation import FinancialOperation, OperationType
from core.entities.budget import BudgetLimit
from datetime import datetime, date
from core.entities.auto_category import AutoCategoryRule
from core.entities.transaction import Transaction


class IAuthenticationService(ABC):
    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        pass

    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass


class IUserService(ABC):
    @abstractmethod
    def register_user(self, username: str, password: str, role: UserRole = UserRole.USER) -> User:
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass


class IOperationService(ABC):
    @abstractmethod
    def create_operation(self, user_id: int, operation_type: OperationType,
                         amount: float, category: str, description: str = None, counterparty: str = None) -> FinancialOperation:
        pass

    @abstractmethod
    def get_operations_for_period(self, user_id: int, days: int = 30) -> List[FinancialOperation]:
        pass

    @abstractmethod
    def get_operation_by_id(self, operation_id: int) -> Optional[FinancialOperation]:
        pass

    @abstractmethod
    def delete_operation(self, operation_id: int, user_id: int) -> bool:
        pass

    @abstractmethod
    def update_operation(self, operation_id: int, user_id: int, **kwargs) -> FinancialOperation:
        pass

    @abstractmethod
    def get_user_operations(self, user_id: int) -> List[FinancialOperation]:
        pass

    @abstractmethod
    def get_top_counterparties(self, user_id: int, limit: int = 5, months: int = 3) -> List[Dict]:
        pass


class IBudgetService(ABC):
    @abstractmethod
    def set_budget_limit(self, user_id: int, category: str, monthly_limit: float) -> BudgetLimit:
        pass

    @abstractmethod
    def check_budget_limits(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_limit(self, user_id: int, category: str) -> bool:
        pass


class IAdminService(ABC):
    @abstractmethod
    def get_system_statistics(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def deactivate_user(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def activate_user(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass


class IReportService(ABC):
    @abstractmethod
    def generate_category_report(self, user_id: int, months: int = 1) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_trend_report(self, user_id: int, months: int = 6) -> Dict[str, Any]:
        pass


class IFinancialCalculator(ABC):
    @abstractmethod
    def calculate_spending(self, user_id: int, category: str, period_days: int) -> float:
        pass

    @abstractmethod
    def calculate_percentage(self, current: float, limit: float) -> float:
        pass

    @abstractmethod
    def calculate_balance_dynamics(self, user_id: int, days: int = 30) -> List[Dict]:
        pass


class IBackupService(ABC):
    @abstractmethod
    def export_to_sqlite(self, export_path: str) -> str:
        pass

    @abstractmethod
    def export_to_json(self, export_path: str, user_id: int = None) -> str:
        pass

    @abstractmethod
    def import_from_sqlite(self, import_path: str, mode: str = 'replace') -> Dict[str, int]:
        pass

    @abstractmethod
    def import_from_json(self, import_path: str) -> Dict[str, int]:
        pass


class IGoalService(ABC):
    @abstractmethod
    def create_goal(self, user_id: int, name: str, target_amount: float,
                    deadline: Optional[datetime] = None,
                    description: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    def get_goals(self, user_id: int, status: Optional[Any] = None) -> List[Any]:
        pass

    @abstractmethod
    def get_goal_by_id(self, goal_id: int) -> Optional[Any]:
        pass

    @abstractmethod
    def add_to_goal(self, goal_id: int, amount: float) -> Any:
        pass

    @abstractmethod
    def add_to_goal_with_transaction(self, goal_id: int, transaction_id: int, amount: float) -> Any:
        """Добавить сумму к цели с привязкой к операции"""
        pass

    @abstractmethod
    def rollback_goal_by_transaction(self, transaction_id: int) -> List[tuple]:
        """Откатить пополнение цели при удалении операции"""
        pass

    @abstractmethod
    def delete_goal(self, goal_id: int) -> bool:
        pass

    @abstractmethod
    def cancel_goal(self, goal_id: int) -> Any:
        pass

    @abstractmethod
    def get_goal_contributions(self, goal_id: int) -> List[dict]:
        """Получить историю пополнений цели"""
        pass


class IScheduledPaymentService(ABC):
    @abstractmethod
    def create_payment(self, user_id: int, name: str, amount: float, category: str,
                       frequency: Any, start_date: date,
                       description: Optional[str] = None) -> Any:
        pass

    @abstractmethod
    def get_payments(self, user_id: int, is_active: Optional[bool] = None) -> List[Any]:
        pass

    @abstractmethod
    def get_due_payments(self, user_id: int) -> List[Any]:
        pass

    @abstractmethod
    def mark_as_paid(self, payment_id: int) -> Any:
        pass

    @abstractmethod
    def toggle_active(self, payment_id: int) -> Any:
        pass

    @abstractmethod
    def delete_payment(self, payment_id: int) -> bool:
        pass

    @abstractmethod
    def get_monthly_total(self, user_id: int) -> float:
        pass


class IAutoCategoryService(ABC):
    @abstractmethod
    def get_category_for_counterparty(self, user_id: int, counterparty: str) -> Optional[str]:
        pass

    @abstractmethod
    def save_rule(self, user_id: int, counterparty: str, category: str) -> AutoCategoryRule:
        pass

    @abstractmethod
    def update_rule(self, rule_id: int, category: str) -> AutoCategoryRule:
        pass

    @abstractmethod
    def delete_rule(self, rule_id: int) -> bool:
        pass

    @abstractmethod
    def get_all_rules(self, user_id: int) -> List[AutoCategoryRule]:
        pass


class INotificationService(ABC):
    @abstractmethod
    def check_budget_limits(self, user_id: int, category: str, amount: float) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def check_goal_deadlines(self, user_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def check_goal_progress(self, user_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def check_upcoming_payments(self, user_id: int, days: int = 3) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_startup_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        pass


class ITransactionService(ABC):
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