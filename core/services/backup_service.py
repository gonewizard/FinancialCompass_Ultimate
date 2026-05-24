"""
Сервис для резервного копирования и восстановления данных.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import shutil

from core.interfaces.services import IBackupService


class BackupService(IBackupService):
    """Сервис для работы с резервными копиями данных."""

    def __init__(self, db_path: str):
        """
        Инициализация сервиса.

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path

    def export_to_sqlite(self, export_path: str) -> str:
        """
        Экспорт всей базы данных как копии SQLite файла.

        Args:
            export_path: Путь для сохранения файла

        Returns:
            str: Путь к сохраненному файлу
        """
        export_file = self._generate_filename(export_path, "backup", "db")

        try:
            # Просто копируем файл базы данных
            shutil.copy2(self.db_path, export_file)
            return export_file
        except Exception as e:
            raise RuntimeError(f"Ошибка при экспорте базы данных: {e}")

    def export_to_json(self, export_path: str, user_id: int = None) -> str:
        """
        Экспорт данных в JSON формат.

        Args:
            export_path: Путь для сохранения файла
            user_id: ID пользователя (если None - все данные)

        Returns:
            str: Путь к сохраненному файлу
        """
        export_file = self._generate_filename(export_path, "backup", "json")

        try:
            data = self._collect_data_for_export(user_id)

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            return export_file
        except Exception as e:
            raise RuntimeError(f"Ошибка при экспорте в JSON: {e}")

    def import_from_sqlite(self, import_path: str, mode: str = 'replace') -> Dict[str, int]:
        """
        Импорт данных из файла SQLite.

        Args:
            import_path: Путь к файлу для импорта
            mode: Режим импорта ('replace' - замена, 'merge' - объединение)

        Returns:
            Dict[str, int]: Статистика импорта
        """
        if not Path(import_path).exists():
            raise FileNotFoundError(f"Файл не найден: {import_path}")

        if mode == 'replace':
            # Просто заменяем текущий файл базы данных
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_path, backup_path)

            try:
                shutil.copy2(import_path, self.db_path)
                return {"status": "success", "backup_created": backup_path}
            except Exception as e:
                # Восстанавливаем из бэкапа при ошибке
                if Path(backup_path).exists():
                    shutil.copy2(backup_path, self.db_path)
                raise RuntimeError(f"Ошибка при импорте: {e}. Восстановлен бэкап.")

        elif mode == 'merge':
            return self._merge_databases(import_path)
        else:
            raise ValueError(f"Неизвестный режим импорта: {mode}")

    def import_from_json(self, import_path: str) -> Dict[str, int]:
        """
        Импорт данных из JSON файла.

        Args:
            import_path: Путь к JSON файлу

        Returns:
            Dict[str, int]: Статистика импорта
        """
        if not Path(import_path).exists():
            raise FileNotFoundError(f"Файл не найден: {import_path}")

        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            stats = self._import_json_data(data)
            return stats

        except Exception as e:
            raise RuntimeError(f"Ошибка при импорте из JSON: {e}")

    def _generate_filename(self, path: str, prefix: str, extension: str) -> str:
        """Генерация имени файла с временной меткой."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.{extension}"
        return str(Path(path) / filename)

    def _collect_data_for_export(self, user_id: int = None) -> Dict[str, Any]:
        """Сбор данных для экспорта."""
        data = {
            "export_date": datetime.now().isoformat(),
            "database": "financial_compass",
            "version": "1.0",
            "users": [],
            "operations": [],
            "budget_limits": []
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Экспорт пользователей
            if user_id is None:
                users_query = "SELECT * FROM users"
                users_params = ()
            else:
                users_query = "SELECT * FROM users WHERE id = ?"
                users_params = (user_id,)

            cursor = conn.execute(users_query, users_params)
            for row in cursor.fetchall():
                data["users"].append(dict(row))

            # Экспорт операций
            if user_id is None:
                ops_query = "SELECT * FROM operations"
                ops_params = ()
            else:
                ops_query = "SELECT * FROM operations WHERE user_id = ?"
                ops_params = (user_id,)

            cursor = conn.execute(ops_query, ops_params)
            for row in cursor.fetchall():
                data["operations"].append(dict(row))

            # Экспорт лимитов бюджета
            if user_id is None:
                limits_query = "SELECT * FROM budget_limits"
                limits_params = ()
            else:
                limits_query = "SELECT * FROM budget_limits WHERE user_id = ?"
                limits_params = (user_id,)

            cursor = conn.execute(limits_query, limits_params)
            for row in cursor.fetchall():
                data["budget_limits"].append(dict(row))

        return data

    def _import_json_data(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Импорт данных из JSON."""
        stats = {
            "users_imported": 0,
            "operations_imported": 0,
            "limits_imported": 0,
            "errors": 0
        }

        with sqlite3.connect(self.db_path) as conn:
            # Импорт пользователей
            for user_data in data.get("users", []):
                try:
                    # Проверяем существование пользователя
                    cursor = conn.execute(
                        "SELECT id FROM users WHERE username = ?",
                        (user_data["username"],)
                    )
                    if cursor.fetchone() is None:
                        conn.execute(
                            """INSERT INTO users (username, password_hash, role, created_at, is_active)
                               VALUES (?, ?, ?, ?, ?)""",
                            (
                                user_data["username"],
                                user_data["password_hash"],
                                user_data["role"],
                                user_data["created_at"],
                                user_data["is_active"]
                            )
                        )
                        stats["users_imported"] += 1
                except Exception:
                    stats["errors"] += 1

            # Импорт операций
            for op_data in data.get("operations", []):
                try:
                    conn.execute(
                        """INSERT INTO operations 
                           (id, user_id, type, amount, category, description, counterparty, operation_date)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            op_data["id"],
                            op_data["user_id"],
                            op_data["type"],
                            op_data["amount"],
                            op_data["category"],
                            op_data.get("description"),
                            op_data.get("counterparty"),
                            op_data["operation_date"]
                        )
                    )
                    stats["operations_imported"] += 1
                except sqlite3.IntegrityError:
                    # Если операция уже существует, пропускаем
                    pass
                except Exception:
                    stats["errors"] += 1

            # Импорт лимитов бюджета
            for limit_data in data.get("budget_limits", []):
                try:
                    conn.execute(
                        """INSERT OR REPLACE INTO budget_limits 
                           (user_id, category, monthly_limit, created_at)
                           VALUES (?, ?, ?, ?)""",
                        (
                            limit_data["user_id"],
                            limit_data["category"],
                            limit_data["monthly_limit"],
                            limit_data["created_at"]
                        )
                    )
                    stats["limits_imported"] += 1
                except Exception:
                    stats["errors"] += 1

            conn.commit()

        return stats

    def _merge_databases(self, source_db_path: str) -> Dict[str, int]:
        """Объединение двух баз данных."""
        stats = {
            "users_merged": 0,
            "operations_merged": 0,
            "limits_merged": 0
        }

        # Создаем временную копию
        temp_db = f"{self.db_path}.temp_merge"
        shutil.copy2(self.db_path, temp_db)

        try:
            # Подключаемся к обеим базам
            main_conn = sqlite3.connect(self.db_path)
            source_conn = sqlite3.connect(source_db_path)

            # Копируем пользователей
            source_cursor = source_conn.execute("SELECT * FROM users")
            for row in source_cursor.fetchall():
                try:
                    main_conn.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role, created_at, is_active) VALUES (?, ?, ?, ?, ?)",
                        (row[1], row[2], row[3], row[4], row[5])
                    )
                    stats["users_merged"] += 1
                except Exception:
                    pass

            # Копируем операции
            source_cursor = source_conn.execute("SELECT * FROM operations")
            for row in source_cursor.fetchall():
                try:
                    main_conn.execute(
                        """INSERT OR IGNORE INTO operations 
                           (id, user_id, type, amount, category, description, counterparty, operation_date)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        row
                    )
                    stats["operations_merged"] += 1
                except Exception:
                    pass

            # Копируем лимиты
            source_cursor = source_conn.execute("SELECT * FROM budget_limits")
            for row in source_cursor.fetchall():
                try:
                    main_conn.execute(
                        "INSERT OR REPLACE INTO budget_limits (user_id, category, monthly_limit, created_at) VALUES (?, ?, ?, ?)",
                        (row[1], row[2], row[3], row[4])
                    )
                    stats["limits_merged"] += 1
                except Exception:
                    pass

            main_conn.commit()
            main_conn.close()
            source_conn.close()

        except Exception as e:
            # Восстанавливаем из временной копии при ошибке
            if Path(temp_db).exists():
                shutil.copy2(temp_db, self.db_path)
            raise RuntimeError(f"Ошибка при объединении баз: {e}")
        finally:
            # Удаляем временную копию
            if Path(temp_db).exists():
                Path(temp_db).unlink()

        return stats