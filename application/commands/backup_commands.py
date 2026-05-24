"""
Команды для работы с резервным копированием данных.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from core.interfaces.services import IBackupService


@dataclass
class ExportToSQLiteCommand:
    """Команда экспорта в SQLite файл."""
    export_path: str


@dataclass
class ExportToJSONCommand:
    """Команда экспорта в JSON файл."""
    export_path: str
    user_id: Optional[int] = None


@dataclass
class ImportFromSQLiteCommand:
    """Команда импорта из SQLite файла."""
    import_path: str
    mode: str = 'replace'  # 'replace' или 'merge'


@dataclass
class ImportFromJSONCommand:
    """Команда импорта из JSON файла."""
    import_path: str


class BackupCommandHandler:
    """Обработчик команд для резервного копирования."""

    def __init__(self, backup_service: IBackupService):
        self._backup_service = backup_service

    def handle_export_to_sqlite(self, command: ExportToSQLiteCommand) -> Dict[str, Any]:
        """
        Обработать экспорт в SQLite.

        Returns:
            Dict с информацией о результате
        """
        try:
            export_file = self._backup_service.export_to_sqlite(command.export_path)

            return {
                'success': True,
                'message': f'База данных успешно экспортирована в файл: {export_file}',
                'export_file': export_file
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка при экспорте: {e}'
            }

    def handle_export_to_json(self, command: ExportToJSONCommand) -> Dict[str, Any]:
        """
        Обработать экспорт в JSON.

        Returns:
            Dict с информацией о результате
        """
        try:
            export_file = self._backup_service.export_to_json(
                command.export_path,
                command.user_id
            )

            return {
                'success': True,
                'message': f'Данные успешно экспортированы в JSON: {export_file}',
                'export_file': export_file
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка при экспорте в JSON: {e}'
            }

    def handle_import_from_sqlite(self, command: ImportFromSQLiteCommand) -> Dict[str, Any]:
        """
        Обработать импорт из SQLite.

        Returns:
            Dict с информацией о результате
        """
        try:
            result = self._backup_service.import_from_sqlite(
                command.import_path,
                command.mode
            )

            mode_text = "заменены" if command.mode == 'replace' else "объединены"
            return {
                'success': True,
                'message': f'Данные успешно {mode_text} из файла: {command.import_path}',
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка при импорте из SQLite: {e}'
            }

    def handle_import_from_json(self, command: ImportFromJSONCommand) -> Dict[str, Any]:
        """
        Обработать импорт из JSON.

        Returns:
            Dict с информацией о результате
        """
        try:
            result = self._backup_service.import_from_json(command.import_path)

            return {
                'success': True,
                'message': f'Данные успешно импортированы из JSON: {command.import_path}',
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка при импорте из JSON: {e}'
            }