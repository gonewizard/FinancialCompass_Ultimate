import sqlite3
from typing import List, Optional
from datetime import datetime
from core.entities.user import User, UserRole
from core.entities.operation import FinancialOperation, OperationType
from core.entities.budget import BudgetLimit
from core.interfaces.repositories import IUserRepository, IOperationRepository, IBudgetRepository
from core.strategies.id_generation import IdGenerator, GapFillingIdStrategy


class SQLiteUserRepository(IUserRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self._db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    initial_balance REAL DEFAULT 0,
                    theme TEXT DEFAULT "light",
                    color_theme TEXT DEFAULT "green",
                    font_size INTEGER DEFAULT 12
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    counterparty TEXT,
                    operation_date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS budget_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    monthly_limit REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, category)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS auto_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    counterparty TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    use_count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, counterparty)
                )
            ''')

    def find_by_username(self, username: str) -> Optional[User]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT id, username, password_hash, role, created_at, is_active FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()

            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=UserRole(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    is_active=bool(row[5])
                )
            return None

    def save(self, user: User) -> User:
        with sqlite3.connect(self._db_path) as conn:
            if user.id == 0:
                created_at_str = user.created_at.isoformat() if user.created_at else datetime.now().isoformat()
                cursor = conn.execute(
                    '''INSERT INTO users (username, password_hash, role, is_active, created_at, initial_balance)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user.username, user.password_hash, user.role.value, user.is_active,
                     created_at_str, user.initial_balance)
                )
                user.id = cursor.lastrowid
            else:
                conn.execute(
                    '''UPDATE users SET username = ?, password_hash = ?, role = ?, is_active = ?, initial_balance = ?
                       WHERE id = ?''',
                    (user.username, user.password_hash, user.role.value, user.is_active,
                     user.initial_balance, user.id)
                )
            return user

    def find_by_id(self, user_id: int) -> Optional[User]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT id, username, password_hash, role, created_at, is_active FROM users WHERE id = ?',
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=UserRole(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    is_active=bool(row[5])
                )
            return None

    def find_all_users(self) -> List[User]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT id, username, password_hash, role, created_at, is_active FROM users ORDER BY username'
            )

            users = []
            for row in cursor.fetchall():
                users.append(User(
                    id=row[0],
                    username=row[1],
                    password_hash=row[2],
                    role=UserRole(row[3]),
                    created_at=datetime.fromisoformat(row[4]),
                    is_active=bool(row[5])
                ))
            return users

    def get_users_count(self) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]

    def delete(self, user_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM users WHERE id = ? AND role != ?',
                                  (user_id, UserRole.ADMIN.value))
            return cursor.rowcount > 0

    def get_initial_balance(self, user_id: int) -> float:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT initial_balance FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0.0

    def update_initial_balance(self, user_id: int, balance: float) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('UPDATE users SET initial_balance = ? WHERE id = ?', (balance, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_theme(self, user_id: int) -> str:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT theme FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else "light"

    def update_theme(self, user_id: int, theme: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('UPDATE users SET theme = ? WHERE id = ?', (theme, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_font_settings(self, user_id: int) -> dict:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT font_size, font_style, color_theme FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return {
                'font_size': row[0] if row else 12,
                'font_style': row[1] if row else "Обычный",
                'color_theme': row[2] if row else "green"
            }

    def update_font_settings(self, user_id: int, font_size: int, font_style: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('UPDATE users SET font_size = ?, font_style = ? WHERE id = ?',
                                  (font_size, font_style, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def update_color_theme(self, user_id: int, color_theme: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('UPDATE users SET color_theme = ? WHERE id = ?', (color_theme, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_color_theme(self, user_id: int) -> str:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT color_theme FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else "green"

    def get_font_size(self, user_id: int) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT font_size FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 12

    def update_font_size(self, user_id: int, font_size: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('UPDATE users SET font_size = ? WHERE id = ?', (font_size, user_id))
            conn.commit()
            return cursor.rowcount > 0

class SQLiteOperationRepository(IOperationRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._id_generator = IdGenerator(GapFillingIdStrategy())

    def save(self, operation: FinancialOperation) -> FinancialOperation:
        with sqlite3.connect(self._db_path) as conn:
            if operation.id == 0:
                cursor = conn.execute('SELECT id FROM operations ORDER BY id')
                existing_ids = [row[0] for row in cursor.fetchall()]

                next_id = self._id_generator.generate_next_id(existing_ids)

                try:
                    cursor = conn.execute(
                        '''INSERT INTO operations (id, user_id, type, amount, category, description, counterparty, operation_date) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (next_id, operation.user_id, operation.type.value, operation.amount,
                         operation.category, operation.description, operation.counterparty, operation.operation_date.isoformat())
                    )
                    operation.id = next_id
                except sqlite3.IntegrityError:
                    cursor = conn.execute(
                        '''INSERT INTO operations (user_id, type, amount, category, description, counterparty, operation_date) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (operation.user_id, operation.type.value, operation.amount,
                         operation.category, operation.description, operation.counterparty, operation.operation_date.isoformat())
                    )
                    operation.id = cursor.lastrowid
            else:
                conn.execute(
                    '''UPDATE operations SET user_id = ?, type = ?, amount = ?, category = ?, 
                       description = ?, counterparty = ?, operation_date = ? WHERE id = ?''',
                    (operation.user_id, operation.type.value, operation.amount, operation.category,
                     operation.description, operation.counterparty, operation.operation_date.isoformat(), operation.id)
                )
            return operation

    def find_by_user_and_period(self, user_id: int, start_date, end_date) -> List[FinancialOperation]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                '''SELECT id, user_id, type, amount, category, description, counterparty, operation_date 
                   FROM operations 
                   WHERE user_id = ? AND operation_date BETWEEN ? AND ? 
                   ORDER BY operation_date DESC''',
                (user_id, start_date.isoformat(), end_date.isoformat())
            )

            operations = []
            for row in cursor.fetchall():
                operations.append(FinancialOperation(
                    id=row[0],
                    user_id=row[1],
                    type=OperationType(row[2]),
                    amount=row[3],
                    category=row[4],
                    description=row[5],
                    counterparty=row[6],
                    operation_date=datetime.fromisoformat(row[7])
                ))
            return operations

    def get_operations_count(self) -> int:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM operations')
            return cursor.fetchone()[0]

    def get_total_income(self) -> float:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT SUM(amount) FROM operations WHERE type = ?',
                (OperationType.INCOME.value,)
            )
            result = cursor.fetchone()[0]
            return result if result else 0.0

    def get_total_expenses(self) -> float:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT SUM(amount) FROM operations WHERE type = ?',
                (OperationType.EXPENSE.value,)
            )
            result = cursor.fetchone()[0]
            return result if result else 0.0

    def get_all_operations(self) -> List[FinancialOperation]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                '''SELECT id, user_id, type, amount, category, description, counterparty, operation_date 
                   FROM operations ORDER BY operation_date DESC'''
            )

            operations = []
            for row in cursor.fetchall():
                operations.append(FinancialOperation(
                    id=row[0],
                    user_id=row[1],
                    type=OperationType(row[2]),
                    amount=row[3],
                    category=row[4],
                    description=row[5],
                    counterparty=row[6],
                    operation_date=datetime.fromisoformat(row[7])
                ))
            return operations

    def find_by_id(self, operation_id: int) -> Optional[FinancialOperation]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                '''SELECT id, user_id, type, amount, category, description, counterparty, operation_date 
                   FROM operations WHERE id = ?''',
                (operation_id,)
            )
            row = cursor.fetchone()

            if row:
                return FinancialOperation(
                    id=row[0],
                    user_id=row[1],
                    type=OperationType(row[2]),
                    amount=row[3],
                    category=row[4],
                    description=row[5],
                    counterparty=row[6],
                    operation_date=datetime.fromisoformat(row[7])
                )
            return None

    def delete(self, operation_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM operations WHERE id = ?', (operation_id,))
            return cursor.rowcount > 0

    def get_operations_by_user(self, user_id: int) -> List[FinancialOperation]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                '''SELECT id, user_id, type, amount, category, description, counterparty, operation_date 
                   FROM operations WHERE user_id = ? ORDER BY operation_date DESC''',
                (user_id,)
            )

            operations = []
            for row in cursor.fetchall():
                operations.append(FinancialOperation(
                    id=row[0],
                    user_id=row[1],
                    type=OperationType(row[2]),
                    amount=row[3],
                    category=row[4],
                    description=row[5],
                    counterparty=row[6],
                    operation_date=datetime.fromisoformat(row[7])
                ))
            return operations

    def get_balance(self, user_id: int) -> float:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
                FROM operations 
                WHERE user_id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            return row[0] - row[1]

class SQLiteBudgetRepository(IBudgetRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path

    def save(self, limit: BudgetLimit) -> BudgetLimit:
        with sqlite3.connect(self._db_path) as conn:
            if limit.id == 0:
                cursor = conn.execute(
                    '''INSERT INTO budget_limits (user_id, category, monthly_limit, created_at) 
                       VALUES (?, ?, ?, ?)''',
                    (limit.user_id, limit.category, limit.monthly_limit, limit.created_at.isoformat())
                )
                limit.id = cursor.lastrowid
            else:
                conn.execute(
                    'UPDATE budget_limits SET user_id = ?, category = ?, monthly_limit = ? WHERE id = ?',
                    (limit.user_id, limit.category, limit.monthly_limit, limit.id)
                )
            return limit

    def find_by_user_and_category(self, user_id: int, category: str) -> Optional[BudgetLimit]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT id, user_id, category, monthly_limit, created_at FROM budget_limits WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            row = cursor.fetchone()

            if row:
                return BudgetLimit(
                    id=row[0],
                    user_id=row[1],
                    category=row[2],
                    monthly_limit=row[3],
                    created_at=datetime.fromisoformat(row[4])
                )
            return None

    def find_all_by_user(self, user_id: int) -> List[BudgetLimit]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT id, user_id, category, monthly_limit, created_at FROM budget_limits WHERE user_id = ?',
                (user_id,)
            )

            limits = []
            for row in cursor.fetchall():
                limits.append(BudgetLimit(
                    id=row[0],
                    user_id=row[1],
                    category=row[2],
                    monthly_limit=row[3],
                    created_at=datetime.fromisoformat(row[4])
                ))
            return limits

    def delete(self, limit_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM budget_limits WHERE id = ?', (limit_id,))
            return cursor.rowcount > 0

    def delete_by_user_and_category(self, user_id: int, category: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'DELETE FROM budget_limits WHERE user_id = ? AND category = ?',
                (user_id, category)
            )
            return cursor.rowcount > 0