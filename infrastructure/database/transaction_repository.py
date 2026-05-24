# infrastructure/database/transaction_repository.py
import sqlite3
from typing import List, Optional, Dict
from core.entities.transaction import Transaction


class TransactionRepository:
    """Репозиторий для работы с операциями в SQLite"""

    def __init__(self, db_path: str = "financial_compass.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """Преобразовать строку БД в объект Transaction"""
        return Transaction(
            id=row['id'],
            user_id=row['user_id'],
            type=row['type'],
            amount=row['amount'],
            category=row['category'],
            counterparty=row['counterparty'],
            date=row['date'],
            description=row['description'],
            created_at=row['created_at']
        )

    def create_table(self):
        """Создать таблицу транзакций, если её нет"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    counterparty TEXT,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            # Создать индексы для ускорения поиска
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_transactions_counterparty ON transactions(counterparty)')
            conn.commit()

    def create(self, transaction: Transaction) -> int:
        """Создать новую операцию"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO transactions (user_id, type, amount, category, counterparty, date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction.user_id,
                transaction.type,
                transaction.amount,
                transaction.category,
                transaction.counterparty,
                transaction.date,
                transaction.description
            ))
            conn.commit()
            return cursor.lastrowid

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Получить операцию по ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM transactions WHERE id = ?',
                (transaction_id,)
            )
            row = cursor.fetchone()
            return self._row_to_transaction(row) if row else None

    def get_by_user_id(self, user_id: int) -> List[Transaction]:
        """Получить все операции пользователя"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC',
                (user_id,)
            )
            return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def get_by_user_id_and_date_range(
            self,
            user_id: int,
            date_from: str,
            date_to: str
    ) -> List[Transaction]:
        """Получить операции пользователя за период"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM transactions 
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (user_id, date_from, date_to))
            return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def get_by_user_id_and_type(
            self,
            user_id: int,
            transaction_type: str
    ) -> List[Transaction]:
        """Получить операции пользователя по типу (income/expense)"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM transactions 
                WHERE user_id = ? AND type = ?
                ORDER BY date DESC
            ''', (user_id, transaction_type))
            return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def update(self, transaction: Transaction) -> bool:
        """Обновить операцию"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                UPDATE transactions 
                SET type = ?, amount = ?, category = ?, counterparty = ?, 
                    date = ?, description = ?
                WHERE id = ? AND user_id = ?
            ''', (
                transaction.type,
                transaction.amount,
                transaction.category,
                transaction.counterparty,
                transaction.date,
                transaction.description,
                transaction.id,
                transaction.user_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, transaction_id: int, user_id: int) -> bool:
        """Удалить операцию"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'DELETE FROM transactions WHERE id = ? AND user_id = ?',
                (transaction_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def search_transactions(self, user_id: int, filters: Dict) -> List[Transaction]:
        """
        Расширенный поиск операций по фильтрам

        filters может содержать:
        - category: str - частичное совпадение категории
        - counterparty: str - частичное совпадение контрагента
        - transaction_type: str - 'income' или 'expense'
        - date_from: str - дата начала (ГГГГ-ММ-ДД)
        - date_to: str - дата конца (ГГГГ-ММ-ДД)
        - amount_min: float - минимальная сумма
        - amount_max: float - максимальная сумма
        - description: str - частичное совпадение описания
        """
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

        if filters.get('category'):
            query += " AND category LIKE ?"
            params.append(f'%{filters["category"]}%')

        if filters.get('counterparty'):
            query += " AND counterparty LIKE ?"
            params.append(f'%{filters["counterparty"]}%')

        if filters.get('transaction_type'):
            query += " AND type = ?"
            params.append(filters['transaction_type'])

        if filters.get('date_from'):
            query += " AND date >= ?"
            params.append(filters['date_from'])

        if filters.get('date_to'):
            query += " AND date <= ?"
            params.append(filters['date_to'])

        if filters.get('amount_min'):
            query += " AND amount >= ?"
            params.append(filters['amount_min'])

        if filters.get('amount_max'):
            query += " AND amount <= ?"
            params.append(filters['amount_max'])

        if filters.get('description'):
            query += " AND description LIKE ?"
            params.append(f'%{filters["description"]}%')

        query += " ORDER BY date DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_transaction(row) for row in cursor.fetchall()]

    def get_balance(self, user_id: int) -> float:
        """Получить текущий баланс пользователя (доходы - расходы)"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
                FROM transactions 
                WHERE user_id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            return row['total_income'] - row['total_expense']

    def get_balance_by_date_range(
            self,
            user_id: int,
            date_from: str,
            date_to: str
    ) -> float:
        """Получить баланс пользователя за период"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
                FROM transactions 
                WHERE user_id = ? AND date BETWEEN ? AND ?
            ''', (user_id, date_from, date_to))
            row = cursor.fetchone()
            return row['total_income'] - row['total_expense']

    def get_balance_by_date(self, user_id: int, up_to_date: str) -> float:
        """Получить баланс пользователя на определённую дату"""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
                FROM transactions 
                WHERE user_id = ? AND date <= ?
            ''', (user_id, up_to_date))
            row = cursor.fetchone()
            return row['total_income'] - row['total_expense']

    def get_top_counterparties(self, user_id: int, limit: int = 5) -> List[tuple]:
        """
        Получить топ-N самых частых контрагентов
        Возвращает список (counterparty, count)
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT counterparty, COUNT(*) as count
                FROM transactions
                WHERE user_id = ? AND counterparty IS NOT NULL AND counterparty != ''
                GROUP BY counterparty
                ORDER BY count DESC
                LIMIT ?
            ''', (user_id, limit))
            return [(row['counterparty'], row['count']) for row in cursor.fetchall()]

    def get_expenses_by_category(self, user_id: int, date_from: str = None, date_to: str = None) -> Dict[str, float]:
        """Получить расходы по категориям"""
        query = '''
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type = 'expense'
        '''
        params = [user_id]

        if date_from and date_to:
            query += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])

        query += " GROUP BY category ORDER BY total DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return {row['category']: row['total'] for row in cursor.fetchall()}

    def get_income_by_category(self, user_id: int, date_from: str = None, date_to: str = None) -> Dict[str, float]:
        """Получить доходы по категориям"""
        query = '''
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type = 'income'
        '''
        params = [user_id]

        if date_from and date_to:
            query += " AND date BETWEEN ? AND ?"
            params.extend([date_from, date_to])

        query += " GROUP BY category ORDER BY total DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return {row['category']: row['total'] for row in cursor.fetchall()}

    def delete_by_user_id(self, user_id: int) -> int:
        """Удалить все операции пользователя"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'DELETE FROM transactions WHERE user_id = ?',
                (user_id,)
            )
            conn.commit()
            return cursor.rowcount