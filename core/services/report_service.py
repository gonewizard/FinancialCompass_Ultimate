from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.entities.operation import FinancialOperation, OperationType
from core.interfaces.repositories import IOperationRepository
from core.interfaces.services import IReportService


class ReportService(IReportService):
    def __init__(self, operation_repository: IOperationRepository):
        self._operation_repository = operation_repository

    def generate_category_report(self, user_id: int, months: int = 1) -> Dict[str, Any]:
        """Сгенерировать отчет по категориям за указанный период"""
        end_date = datetime.now()
        start_date = self._calculate_start_date(end_date, months)

        operations = self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)

        income_by_category = self._aggregate_by_category(operations, OperationType.INCOME)
        expense_by_category = self._aggregate_by_category(operations, OperationType.EXPENSE)

        total_income = sum(income_by_category.values())
        total_expense = sum(expense_by_category.values())

        return {
            'period': {
                'start': start_date,
                'end': end_date,
                'months': months
            },
            'income_by_category': income_by_category,
            'expense_by_category': expense_by_category,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense
        }

    def generate_trend_report(self, user_id: int, months: int = 6) -> Dict[str, Any]:
        """Сгенерировать отчет по динамике доходов/расходов"""
        end_date = datetime.now().replace(day=1)
        monthly_data = []

        for i in range(months):
            month_start = self._calculate_month_start(end_date, i)
            month_end = self._calculate_month_end(month_start)

            operations = self._operation_repository.find_by_user_and_period(
                user_id, month_start, month_end
            )

            monthly_income = sum(op.amount for op in operations if op.type == OperationType.INCOME)
            monthly_expense = sum(op.amount for op in operations if op.type == OperationType.EXPENSE)

            monthly_data.append({
                'month': month_start.strftime('%Y-%m'),
                'income': monthly_income,
                'expense': monthly_expense,
                'balance': monthly_income - monthly_expense
            })

        monthly_data.reverse()

        return {
            'period_months': months,
            'monthly_data': monthly_data
        }

    def _calculate_start_date(self, end_date: datetime, months: int) -> datetime:
        """Рассчитать дату начала периода"""
        return end_date - timedelta(days=30 * months)

    def _calculate_month_start(self, base_date: datetime, months_ago: int) -> datetime:
        """Рассчитать начало месяца N месяцев назад"""
        if months_ago == 0:
            return base_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        first_day = base_date.replace(day=1)
        for _ in range(months_ago):
            first_day = (first_day - timedelta(days=28)).replace(day=1)

        return first_day

    def _calculate_month_end(self, month_start: datetime) -> datetime:
        """Рассчитать конец месяца"""
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1, day=1)

        return next_month - timedelta(seconds=1)

    def _aggregate_by_category(self, operations: List[FinancialOperation],
                               operation_type: OperationType) -> Dict[str, float]:
        """Агрегировать операции по категориям"""
        result = {}
        for operation in operations:
            if operation.type == operation_type:
                result[operation.category] = result.get(operation.category, 0) + operation.amount
        return result