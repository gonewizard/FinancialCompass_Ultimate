# core/services/transaction_service.py
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from core.entities.transaction import Transaction
from infrastructure.database.transaction_repository import TransactionRepository


class TransactionService:
    """Сервис для работы с финансовыми операциями"""

    def __init__(self, repository: TransactionRepository):
        self.repository = repository
        # Убедимся, что таблица существует
        self.repository.create_table()

    def create_transaction(
            self,
            user_id: int,
            transaction_type: str,
            amount: float,
            category: str,
            counterparty: str = None,
            date: str = None,
            description: str = None
    ) -> int:
        """
        Создать новую операцию

        Returns:
            int: ID созданной операции
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            category=category,
            counterparty=counterparty,
            date=date,
            description=description
        )

        return self.repository.create(transaction)

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Получить операцию по ID"""
        return self.repository.get_by_id(transaction_id)

    def get_user_transactions(self, user_id: int) -> List[Transaction]:
        """Получить все операции пользователя"""
        return self.repository.get_by_user_id(user_id)

    def get_transactions_by_date_range(
            self,
            user_id: int,
            date_from: str,
            date_to: str
    ) -> List[Transaction]:
        """Получить операции за период"""
        return self.repository.get_by_user_id_and_date_range(user_id, date_from, date_to)

    def get_transactions_by_type(
            self,
            user_id: int,
            transaction_type: str
    ) -> List[Transaction]:
        """Получить операции по типу (income/expense)"""
        return self.repository.get_by_user_id_and_type(user_id, transaction_type)

    def update_transaction(
            self,
            transaction_id: int,
            user_id: int,
            transaction_type: str = None,
            amount: float = None,
            category: str = None,
            counterparty: str = None,
            date: str = None,
            description: str = None
    ) -> bool:
        """Обновить операцию"""
        existing = self.repository.get_by_id(transaction_id)
        if not existing or existing.user_id != user_id:
            return False

        # Обновляем только переданные поля
        updated = Transaction(
            id=existing.id,
            user_id=existing.user_id,
            type=transaction_type or existing.type,
            amount=amount or existing.amount,
            category=category or existing.category,
            counterparty=counterparty if counterparty is not None else existing.counterparty,
            date=date or existing.date,
            description=description if description is not None else existing.description,
            created_at=existing.created_at
        )

        return self.repository.update(updated)

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Удалить операцию"""
        return self.repository.delete(transaction_id, user_id)

    def search_transactions(self, user_id: int, filters: Dict) -> List[Transaction]:
        """
        Расширенный поиск операций

        filters может содержать:
        - category: str
        - counterparty: str
        - transaction_type: str ('income' или 'expense')
        - date_from: str (ГГГГ-ММ-ДД)
        - date_to: str (ГГГГ-ММ-ДД)
        - amount_min: float
        - amount_max: float
        - description: str
        """
        return self.repository.search_transactions(user_id, filters)

    def get_balance(self, user_id: int) -> float:
        """Получить текущий баланс пользователя"""
        return self.repository.get_balance(user_id)

    def get_balance_by_date_range(
            self,
            user_id: int,
            date_from: str,
            date_to: str
    ) -> float:
        """Получить баланс за период"""
        return self.repository.get_balance_by_date_range(user_id, date_from, date_to)

    def get_balance_by_date(self, user_id: int, date: str) -> float:
        """Получить баланс на конкретную дату"""
        return self.repository.get_balance_by_date(user_id, date)

    def get_total_income(self, user_id: int, date_from: str = None, date_to: str = None) -> float:
        """Получить сумму доходов"""
        transactions = self.repository.get_by_user_id(user_id)

        if date_from and date_to:
            transactions = [t for t in transactions if date_from <= t.date <= date_to]

        return sum(t.amount for t in transactions if t.type == 'income')

    def get_total_expense(self, user_id: int, date_from: str = None, date_to: str = None) -> float:
        """Получить сумму расходов"""
        transactions = self.repository.get_by_user_id(user_id)

        if date_from and date_to:
            transactions = [t for t in transactions if date_from <= t.date <= date_to]

        return sum(t.amount for t in transactions if t.type == 'expense')

    def get_top_counterparties(self, user_id: int, limit: int = 5) -> List[tuple]:
        """Получить топ самых частых контрагентов"""
        return self.repository.get_top_counterparties(user_id, limit)

    def get_expenses_by_category(
            self,
            user_id: int,
            date_from: str = None,
            date_to: str = None
    ) -> Dict[str, float]:
        """Получить расходы по категориям"""
        return self.repository.get_expenses_by_category(user_id, date_from, date_to)

    def get_income_by_category(
            self,
            user_id: int,
            date_from: str = None,
            date_to: str = None
    ) -> Dict[str, float]:
        """Получить доходы по категориям"""
        return self.repository.get_income_by_category(user_id, date_from, date_to)

    def get_balance_history(
            self,
            user_id: int,
            days: int = 30
    ) -> List[Dict]:
        """
        Получить историю баланса для графика

        Returns:
            List[Dict]: список словарей с датами и балансом
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        history = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            balance = self.get_balance_by_date(user_id, date_str)
            history.append({
                'date': date_str,
                'balance': balance
            })
            current_date += timedelta(days=1)

        return history

    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """
        Получить сводку за месяц

        Returns:
            Dict: доходы, расходы, баланс, топ категории
        """
        date_from = f"{year}-{month:02d}-01"

        # Определяем последний день месяца
        if month == 12:
            date_to = f"{year + 1}-01-01"
        else:
            date_to = f"{year}-{month + 1:02d}-01"

        # Вычитаем один день
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') - timedelta(days=1)
        date_to = date_to_obj.strftime('%Y-%m-%d')

        transactions = self.get_transactions_by_date_range(user_id, date_from, date_to)

        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')

        expenses_by_category = {}
        for t in transactions:
            if t.type == 'expense':
                expenses_by_category[t.category] = expenses_by_category.get(t.category, 0) + t.amount

        # Сортируем категории по сумме
        top_categories = sorted(
            expenses_by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'year': year,
            'month': month,
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'top_categories': top_categories,
            'transaction_count': len(transactions)
        }

    def get_calendar_data(self, user_id: int, year: int, month: int) -> Dict[str, float]:
        """
        Получить данные для календаря финансовой активности

        Returns:
            Dict: {день_месяца: сумма_операций}
        """
        date_from = f"{year}-{month:02d}-01"

        if month == 12:
            date_to = f"{year + 1}-01-01"
        else:
            date_to = f"{year}-{month + 1:02d}-01"

        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') - timedelta(days=1)
        date_to = date_to_obj.strftime('%Y-%m-%d')

        transactions = self.get_transactions_by_date_range(user_id, date_from, date_to)

        calendar_data = {}
        for t in transactions:
            day = int(t.date.split('-')[2])
            calendar_data[day] = calendar_data.get(day, 0) + t.amount

        return calendar_data

    def delete_all_user_transactions(self, user_id: int) -> int:
        """Удалить все операции пользователя (осторожно!)"""
        return self.repository.delete_by_user_id(user_id)