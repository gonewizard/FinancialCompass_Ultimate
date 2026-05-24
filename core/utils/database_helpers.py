import sqlite3
from typing import List, Tuple, Any


class DatabaseHelpers:
    @staticmethod
    def reset_autoincrement(db_path: str, table_name: str) -> None:
        """Сброс счетчика AUTOINCREMENT для таблицы"""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(f'SELECT MAX(id) FROM {table_name}')
            max_id = cursor.fetchone()[0]

            if max_id is None:
                conn.execute(f'DELETE FROM sqlite_sequence WHERE name = ?', (table_name,))

    @staticmethod
    def get_next_available_id(db_path: str, table_name: str) -> int:
        """Получить следующий доступный ID с учетом удаленных записей"""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(f'SELECT id FROM {table_name} ORDER BY id')
            existing_ids = [row[0] for row in cursor.fetchall()]

            if not existing_ids:
                return 1

            for i in range(1, max(existing_ids) + 2):
                if i not in existing_ids:
                    return i

            return max(existing_ids) + 1

    @staticmethod
    def execute_many(db_path: str, query: str, data: List[Tuple]) -> None:
        """Выполнить массовую вставку"""
        with sqlite3.connect(db_path) as conn:
            conn.executemany(query, data)
            conn.commit()

    @staticmethod
    def get_table_info(db_path: str, table_name: str) -> List[Tuple]:
        """Получить информацию о структуре таблицы"""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(f'PRAGMA table_info({table_name})')
            return cursor.fetchall()

    @staticmethod
    def vacuum_database(db_path: str) -> None:
        """Оптимизировать БД"""
        with sqlite3.connect(db_path) as conn:
            conn.execute('VACUUM')