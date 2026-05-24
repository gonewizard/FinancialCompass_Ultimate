import sqlite3
from datetime import datetime
from typing import List, Optional
from core.entities.auto_category import AutoCategoryRule
from core.interfaces.repositories import IAutoCategoryRepository


class SQLiteAutoCategoryRepository(IAutoCategoryRepository):
    def __init__(self, db_path: str):
        self._db_path = db_path

    def save(self, rule: AutoCategoryRule) -> AutoCategoryRule:
        with sqlite3.connect(self._db_path) as conn:
            if rule.id == 0:
                cursor = conn.execute(
                    '''INSERT INTO auto_categories (user_id, counterparty, category, created_at, use_count)
                       VALUES (?, ?, ?, ?, ?)''',
                    (rule.user_id, rule.counterparty, rule.category, rule.created_at.isoformat(), rule.use_count)
                )
                rule.id = cursor.lastrowid
            else:
                conn.execute(
                    '''UPDATE auto_categories SET category = ?, use_count = ? WHERE id = ?''',
                    (rule.category, rule.use_count, rule.id)
                )
            return rule

    def find_by_user_and_counterparty(self, user_id: int, counterparty: str) -> Optional[AutoCategoryRule]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM auto_categories WHERE user_id = ? AND counterparty = ?',
                (user_id, counterparty)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_rule(row)
        return None

    def find_by_user(self, user_id: int) -> List[AutoCategoryRule]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'SELECT * FROM auto_categories WHERE user_id = ? ORDER BY use_count DESC',
                (user_id,)
            )
            rules = []
            for row in cursor.fetchall():
                rules.append(self._row_to_rule(row))
            return rules

    def delete(self, rule_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute('DELETE FROM auto_categories WHERE id = ?', (rule_id,))
            return cursor.rowcount > 0

    def increment_use_count(self, rule_id: int) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                'UPDATE auto_categories SET use_count = use_count + 1 WHERE id = ?',
                (rule_id,)
            )
            return cursor.rowcount > 0

    def _row_to_rule(self, row) -> AutoCategoryRule:
        return AutoCategoryRule(
            id=row[0],
            user_id=row[1],
            counterparty=row[2],
            category=row[3],
            created_at=datetime.fromisoformat(row[4]),
            use_count=row[5]
        )