import sqlite3
from datetime import datetime, date
from typing import List, Optional
from core.entities.scheduled_payment import ScheduledPayment, PaymentFrequency
from core.interfaces.repositories import IScheduledPaymentRepository


class SQLiteScheduledPaymentRepository(IScheduledPaymentRepository):
    """SQLite реализация репозитория плановых платежей"""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Создать таблицу плановых платежей, если не существует"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    next_due_date TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

    def save(self, payment: ScheduledPayment) -> ScheduledPayment:
        with sqlite3.connect(self._db_path) as conn:
            if payment.id == 0:
                cursor = conn.execute(
                    '''INSERT INTO scheduled_payments 
                       (user_id, name, amount, category, frequency, next_due_date, is_active, created_at, description)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (payment.user_id, payment.name, payment.amount, payment.category,
                     payment.frequency.value, payment.next_due_date.isoformat(),
                     1 if payment.is_active else 0, payment.created_at.isoformat(), payment.description)
                )
                payment.id = cursor.lastrowid
            else:
                conn.execute(
                    '''UPDATE scheduled_payments SET 
                       name = ?, amount = ?, category = ?, frequency = ?, 
                       next_due_date = ?, is_active = ?, description = ? WHERE id = ?''',
                    (payment.name, payment.amount, payment.category, payment.frequency.value,
                     payment.next_due_date.isoformat(), 1 if payment.is_active else 0,
                     payment.description, payment.id)
                )
            return payment

    def find_by_id(self, payment_id: int) -> Optional[ScheduledPayment]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM scheduled_payments WHERE id = ?',
                (payment_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_payment(row)
        return None

    def find_by_user(self, user_id: int, is_active: Optional[bool] = None) -> List[ScheduledPayment]:
        with sqlite3.connect(self._db_path) as conn:
            if is_active is not None:
                cursor = conn.execute(
                    'SELECT * FROM scheduled_payments WHERE user_id = ? AND is_active = ? ORDER BY next_due_date',
                    (user_id, 1 if is_active else 0)
                )
            else:
                cursor = conn.execute(
                    'SELECT * FROM scheduled_payments WHERE user_id = ? ORDER BY next_due_date',
                    (user_id,)
                )

            payments = []
            for row in cursor.fetchall():
                payments.append(self._row_to_payment(row))
            return payments

    def find_due_payments(self, user_id: int, due_date: date) -> List[ScheduledPayment]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM scheduled_payments WHERE user_id = ? AND is_active = 1 AND next_due_date <= ? ORDER BY next_due_date',
                (user_id, due_date.isoformat())
            )

            payments = []
            for row in cursor.fetchall():
                payments.append(self._row_to_payment(row))
            return payments

    def delete(self, payment_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM scheduled_payments WHERE id = ?', (payment_id,))
            return cursor.rowcount > 0

    def update_next_due_date(self, payment_id: int, next_due_date: date) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'UPDATE scheduled_payments SET next_due_date = ? WHERE id = ?',
                (next_due_date.isoformat(), payment_id)
            )
            return cursor.rowcount > 0

    def _row_to_payment(self, row) -> ScheduledPayment:
        return ScheduledPayment(
            id=row[0],
            user_id=row[1],
            name=row[2],
            amount=row[3],
            category=row[4],
            frequency=PaymentFrequency(row[5]),
            next_due_date=date.fromisoformat(row[6]),
            is_active=bool(row[7]),
            created_at=datetime.fromisoformat(row[8]),
            description=row[9] if len(row) > 9 else None
        )