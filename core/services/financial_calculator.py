from typing import List, Dict
from datetime import datetime, timedelta
from core.entities.operation import OperationType
from core.interfaces.repositories import IOperationRepository, IUserRepository


class FinancialCalculator:
    def __init__(self, operation_repository: IOperationRepository, user_repository: IUserRepository = None):
        self._operation_repository = operation_repository
        self._user_repository = user_repository

    def get_initial_balance(self, user_id: int) -> float:
        if self._user_repository:
            return self._user_repository.get_initial_balance(user_id)
        return 0.0

    def get_balance_with_initial(self, user_id: int) -> float:
        initial = self.get_initial_balance(user_id)
        transactions_balance = self._operation_repository.get_balance(user_id)
        return initial + transactions_balance

    def calculate_balance_dynamics(self, user_id: int, days: int = 30) -> List[Dict]:
        initial = self.get_initial_balance(user_id)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        operations = self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)

        daily_data = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_data[date_str] = {'income': 0.0, 'expense': 0.0}
            current_date += timedelta(days=1)

        for op in operations:
            date_str = op.operation_date.strftime('%Y-%m-%d')
            if date_str in daily_data:
                if op.type == OperationType.INCOME:
                    daily_data[date_str]['income'] += op.amount
                else:
                    daily_data[date_str]['expense'] += op.amount

        result = []
        running_balance = initial
        for date_str in sorted(daily_data.keys()):
            income = daily_data[date_str]['income']
            expense = daily_data[date_str]['expense']
            running_balance += income - expense
            result.append({
                'date': datetime.strptime(date_str, '%Y-%m-%d'),
                'date_str': date_str,
                'income': income,
                'expense': expense,
                'balance': running_balance
            })

        return result

    def calculate_spending(self, user_id: int, category: str, period_days: int) -> float:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        operations = self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)

        total = 0.0
        for op in operations:
            if op.type == OperationType.EXPENSE and op.category == category:
                total += op.amount
        return total

    def calculate_percentage(self, current: float, limit: float) -> float:
        if limit <= 0:
            return 0.0
        return (current / limit) * 100