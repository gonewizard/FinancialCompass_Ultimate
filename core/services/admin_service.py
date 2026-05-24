from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.entities.user import User, UserRole
from core.entities.operation import OperationType
from core.interfaces.repositories import IUserRepository, IOperationRepository
from core.interfaces.services import IAdminService


class AdminService(IAdminService):
    def __init__(self, user_repository: IUserRepository, operation_repository: IOperationRepository):
        self._user_repository = user_repository
        self._operation_repository = operation_repository

    def get_all_users(self) -> List[User]:
        """Получить список всех пользователей"""
        return self._user_repository.find_all_users()

    def get_system_statistics(self) -> Dict[str, Any]:
        """Получить системную статистику"""
        total_users = self._user_repository.get_users_count()
        total_operations = self._operation_repository.get_operations_count()
        total_income = self._operation_repository.get_total_income()
        total_expenses = self._operation_repository.get_total_expenses()

        active_users = self._get_active_users_count()
        recent_operations = self._get_recent_operations_stats()

        return {
            "total_users": total_users,
            "total_operations": total_operations,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "system_balance": total_income - total_expenses,
            "active_users": active_users,
            "recent_activity": recent_operations
        }

    def _get_active_users_count(self) -> int:
        """Получить количество активных пользователей (с операциями за 30 дней)"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        all_operations = self._operation_repository.get_all_operations()

        active_user_ids = set()
        for operation in all_operations:
            if operation.operation_date >= thirty_days_ago:
                active_user_ids.add(operation.user_id)

        return len(active_user_ids)

    def _get_recent_operations_stats(self) -> Dict[str, Any]:
        """Получить статистику по последним операциям"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_operations = self._get_operations_since(thirty_days_ago)

        recent_income = sum(op.amount for op in recent_operations if op.type == OperationType.INCOME)
        recent_expenses = sum(op.amount for op in recent_operations if op.type == OperationType.EXPENSE)

        return {
            "recent_operations_count": len(recent_operations),
            "recent_income": recent_income,
            "recent_expenses": recent_expenses,
            "recent_balance": recent_income - recent_expenses
        }

    def _get_operations_since(self, start_date: datetime) -> List:
        """Вспомогательный метод для получения операций с даты"""
        all_operations = self._operation_repository.get_all_operations()
        return [op for op in all_operations if op.operation_date >= start_date]

    def deactivate_user(self, user_id: int) -> bool:
        """Деактивировать пользователя"""
        user = self._user_repository.find_by_id(user_id)
        if user and user.role != UserRole.ADMIN:
            user.is_active = False
            self._user_repository.save(user)
            return True
        return False

    def activate_user(self, user_id: int) -> bool:
        """Активировать пользователя"""
        user = self._user_repository.find_by_id(user_id)
        if user:
            user.is_active = True
            self._user_repository.save(user)
            return True
        return False

    def get_user_detailed_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить детальную статистику по пользователю"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return {}

        user_operations = self._get_user_operations_last_year(user_id)

        total_income = sum(op.amount for op in user_operations if op.type == OperationType.INCOME)
        total_expenses = sum(op.amount for op in user_operations if op.type == OperationType.EXPENSE)

        return {
            "user_id": user_id,
            "username": user.username,
            "registration_date": user.created_at,
            "total_operations": len(user_operations),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses,
            "is_active": user.is_active
        }

    def _get_user_operations_last_year(self, user_id: int) -> List:
        """Получить операции пользователя за последний год"""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        return self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)