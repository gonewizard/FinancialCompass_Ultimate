from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.entities.operation import FinancialOperation, OperationType
from core.interfaces.repositories import IOperationRepository
from core.interfaces.services import IOperationService
from core.exceptions import OperationValidationError, OperationNotFoundError
from core.utils.validators import Validators


class OperationService(IOperationService):
    def __init__(self, operation_repository: IOperationRepository):
        self._operation_repository = operation_repository

    def create_operation(self, user_id: int, operation_type: OperationType,
                         amount: float, category: str, description: str = None,
                         counterparty: str = None) -> FinancialOperation:
        Validators.validate_positive(amount, "Amount")
        Validators.validate_not_empty(category, "Category")

        operation = FinancialOperation.create(
            user_id=user_id,
            type=operation_type,
            amount=amount,
            category=category,
            description=description,
            counterparty=counterparty
        )

        return self._operation_repository.save(operation)

    def get_operations_for_period(self, user_id: int, days: int = 30) -> List[FinancialOperation]:
        Validators.validate_positive(days, "Days")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)

    def get_operation_by_id(self, operation_id: int) -> Optional[FinancialOperation]:
        return self._operation_repository.find_by_id(operation_id)

    def get_filtered_operations(
            self,
            user_id: int,
            category: str = None,
            start_date: datetime = None,
            end_date: datetime = None,
            operation_type: OperationType = None
    ) -> List[FinancialOperation]:
        """
        Получить отфильтрованные операции пользователя.

        Args:
            user_id: ID пользователя
            category: Категория для фильтрации (опционально)
            start_date: Начальная дата (опционально)
            end_date: Конечная дата (опционально)
            operation_type: Тип операции (доход/расход, опционально)

        Returns:
            List[FinancialOperation]: Отфильтрованные операции
        """
        # Получаем все операции пользователя
        all_operations = self.get_user_operations(user_id)

        filtered_operations = []

        for operation in all_operations:
            # Фильтрация по категории
            if category and operation.category != category:
                continue

            # Фильтрация по типу операции
            if operation_type and operation.type != operation_type:
                continue

            # Фильтрация по дате
            if start_date and operation.operation_date < start_date:
                continue

            if end_date and operation.operation_date > end_date:
                continue

            filtered_operations.append(operation)

        # Сортируем по дате (сначала новые)
        filtered_operations.sort(key=lambda x: x.operation_date, reverse=True)

        return filtered_operations

    def get_user_categories(self, user_id: int, operation_type: OperationType = None) -> List[str]:
        """
        Получить уникальные категории пользователя.

        Args:
            user_id: ID пользователя
            operation_type: Тип операции (опционально)

        Returns:
            List[str]: Список уникальных категорий
        """
        operations = self.get_user_operations(user_id)

        categories = set()
        for operation in operations:
            if operation_type and operation.type != operation_type:
                continue
            categories.add(operation.category)

        return sorted(list(categories))

    def delete_operation(self, operation_id: int, user_id: int) -> bool:
        operation = self.get_operation_by_id(operation_id)
        if not operation:
            raise OperationNotFoundError(f"Operation with ID {operation_id} not found")

        if operation.user_id != user_id:
            raise OperationValidationError("You can only delete your own operations")

        return self._operation_repository.delete(operation_id)

    def update_operation(self, operation_id: int, user_id: int, **kwargs) -> FinancialOperation:
        operation = self.get_operation_by_id(operation_id)
        if not operation:
            raise OperationNotFoundError(f"Operation with ID {operation_id} not found")

        if operation.user_id != user_id:
            raise OperationValidationError("You can only update your own operations")

        if 'amount' in kwargs:
            Validators.validate_positive(kwargs['amount'], "Amount")

        if 'category' in kwargs:
            Validators.validate_not_empty(kwargs['category'], "Category")

        for key, value in kwargs.items():
            if hasattr(operation, key) and value is not None:
                setattr(operation, key, value)

        return self._operation_repository.save(operation)

    def get_user_operations(self, user_id: int) -> List[FinancialOperation]:
        operations = self._operation_repository.get_all_operations()
        return [op for op in operations if op.user_id == user_id]


    def get_top_counterparties(self, user_id: int, limit: int = 5, months: int = 3) -> List[Dict[str, Any]]:
        """
        Получить топ N самых частых контрагентов (только расходы).

        Args:
            user_id: ID пользователя
            limit: Количество контрагентов в топе
            months: За сколько месяцев анализировать

        Returns:
            List[Dict]: Список с данными по контрагентам
        """
        # Определяем период
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        # Получаем операции за период
        operations = self._operation_repository.find_by_user_and_period(
            user_id, start_date, end_date
        )

        # Собираем статистику по контрагентам (только расходы)
        counterparty_stats = {}

        for op in operations:
            # Пропускаем операции без контрагента И доходы
            if not op.counterparty or op.type != OperationType.EXPENSE:
                continue

            if op.counterparty not in counterparty_stats:
                counterparty_stats[op.counterparty] = {
                    'name': op.counterparty,
                    'count': 0,
                    'total': 0.0,
                    'avg': 0.0,
                    'last_date': op.operation_date,
                    'category': op.category
                }

            stats = counterparty_stats[op.counterparty]
            stats['count'] += 1
            stats['total'] += op.amount
            if op.operation_date > stats['last_date']:
                stats['last_date'] = op.operation_date
                stats['category'] = op.category

        # Рассчитываем средний чек
        for stats in counterparty_stats.values():
            stats['avg'] = stats['total'] / stats['count'] if stats['count'] > 0 else 0

        # Сортируем: сначала по количеству (по убыванию), потом по сумме (по убыванию)
        sorted_stats = sorted(
            counterparty_stats.values(),
            key=lambda x: (x['count'], x['total']),
            reverse=True
        )[:limit]

        return sorted_stats