import sqlite3
from datetime import datetime
from typing import List, Optional
from core.entities.goal import FinancialGoal, GoalStatus
from core.interfaces.repositories import IGoalRepository


class SQLiteGoalRepository(IGoalRepository):
    """SQLite реализация репозитория финансовых целей"""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_table_exists()
        self._ensure_goal_transactions_table_exists()

    def _ensure_table_exists(self):
        """Создать таблицу целей, если не существует"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL NOT NULL DEFAULT 0,
                    deadline TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()

    def _ensure_goal_transactions_table_exists(self):
        """Создать таблицу связей целей с операциями, если не существует"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS goal_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    transaction_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE CASCADE,
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id) ON DELETE CASCADE,
                    UNIQUE(goal_id, transaction_id)
                )
            ''')
            conn.commit()

    def save(self, goal: FinancialGoal) -> FinancialGoal:
        with sqlite3.connect(self._db_path) as conn:
            if goal.id == 0:
                cursor = conn.execute(
                    '''INSERT INTO goals 
                       (user_id, name, target_amount, current_amount, deadline, status, created_at, description)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (goal.user_id, goal.name, goal.target_amount, goal.current_amount,
                     goal.deadline.isoformat() if goal.deadline else None,
                     goal.status.value, goal.created_at.isoformat(), goal.description)
                )
                goal.id = cursor.lastrowid
            else:
                conn.execute(
                    '''UPDATE goals SET 
                       name = ?, target_amount = ?, current_amount = ?, deadline = ?, 
                       status = ?, description = ? WHERE id = ?''',
                    (goal.name, goal.target_amount, goal.current_amount,
                     goal.deadline.isoformat() if goal.deadline else None,
                     goal.status.value, goal.description, goal.id)
                )
            return goal

    def find_by_id(self, goal_id: int) -> Optional[FinancialGoal]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM goals WHERE id = ?',
                (goal_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_goal(row)
        return None

    def find_by_user(self, user_id: int, status: Optional[GoalStatus] = None) -> List[FinancialGoal]:
        with sqlite3.connect(self._db_path) as conn:
            if status:
                cursor = conn.execute(
                    'SELECT * FROM goals WHERE user_id = ? AND status = ? ORDER BY created_at DESC',
                    (user_id, status.value)
                )
            else:
                cursor = conn.execute(
                    'SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC',
                    (user_id,)
                )

            goals = []
            for row in cursor.fetchall():
                goals.append(self._row_to_goal(row))
            return goals

    def delete(self, goal_id: int) -> bool:
        """Удалить цель (связи в goal_transactions удалятся автоматически благодаря ON DELETE CASCADE)"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            return cursor.rowcount > 0

    def update_amount(self, goal_id: int, amount: float) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'UPDATE goals SET current_amount = ? WHERE id = ?',
                (amount, goal_id)
            )
            return cursor.rowcount > 0

    # ========== НОВЫЕ МЕТОДЫ ДЛЯ СВЯЗИ С ОПЕРАЦИЯМИ ==========

    def add_goal_transaction(self, goal_id: int, transaction_id: int, amount: float) -> None:
        """Привязать операцию дохода к цели"""
        with sqlite3.connect(self._db_path) as conn:
            try:
                conn.execute(
                    '''INSERT INTO goal_transactions (goal_id, transaction_id, amount) 
                       VALUES (?, ?, ?)''',
                    (goal_id, transaction_id, amount)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Связь уже существует - игнорируем
                pass

    def get_goal_transactions_by_transaction(self, transaction_id: int) -> List[tuple]:
        """Получить все цели, связанные с операцией"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT goal_id, amount FROM goal_transactions WHERE transaction_id = ?',
                (transaction_id,)
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def delete_goal_transactions_by_transaction(self, transaction_id: int) -> None:
        """Удалить все связи операции с целями"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                'DELETE FROM goal_transactions WHERE transaction_id = ?',
                (transaction_id,)
            )
            conn.commit()

    def get_goal_contributions_with_details(self, goal_id: int) -> List[dict]:
        """Получить историю пополнений цели с деталями операций"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    gt.transaction_id,
                    gt.amount,
                    gt.created_at,
                    t.date as operation_date,
                    t.counterparty,
                    t.description
                FROM goal_transactions gt
                LEFT JOIN transactions t ON gt.transaction_id = t.id
                WHERE gt.goal_id = ?
                ORDER BY gt.created_at DESC
            ''', (goal_id,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'transaction_id': row[0],
                    'amount': row[1],
                    'created_at': row[2],
                    'operation_date': row[3],
                    'counterparty': row[4],
                    'description': row[5]
                })
            return results

    def get_total_contributed_to_goal(self, goal_id: int) -> float:
        """Получить общую сумму, внесённую в цель через операции"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT COALESCE(SUM(amount), 0) FROM goal_transactions WHERE goal_id = ?',
                (goal_id,)
            )
            return cursor.fetchone()[0]

    def get_goals_by_transaction(self, transaction_id: int) -> List[FinancialGoal]:
        """Получить все цели, которые пополнялись данной операцией"""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('''
                SELECT g.* FROM goals g
                JOIN goal_transactions gt ON g.id = gt.goal_id
                WHERE gt.transaction_id = ?
            ''', (transaction_id,))

            goals = []
            for row in cursor.fetchall():
                goals.append(self._row_to_goal(row))
            return goals

    def _row_to_goal(self, row) -> FinancialGoal:
        return FinancialGoal(
            id=row[0],
            user_id=row[1],
            name=row[2],
            target_amount=row[3],
            current_amount=row[4],
            deadline=datetime.fromisoformat(row[5]) if row[5] else None,
            status=GoalStatus(row[6]),
            created_at=datetime.fromisoformat(row[7]),
            description=row[8] if len(row) > 8 else None
        )