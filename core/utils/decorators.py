from functools import wraps
from typing import Callable, Any
from core.exceptions import PermissionError


def admin_required(func: Callable) -> Callable:
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if args:
            command = args[0]
            if hasattr(command, 'admin_user_id'):
                admin = self._user_repository.find_by_id(command.admin_user_id)
                if not admin or not admin.has_admin_privileges():
                    raise PermissionError("Admin privileges required")
        return func(self, *args, **kwargs)
    return wrapper


def validate_command(func: Callable) -> Callable:
    """Декоратор для валидации команд"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if args:
            command = args[0]
            if hasattr(command, '__dataclass_fields__'):
                for field in command.__dataclass_fields__.values():
                    if field.name != 'admin_user_id':
                        value = getattr(command, field.name)
                        if value is None and not str(field.type).startswith('Optional'):
                            raise ValueError(f"Field '{field.name}' is required")
        return func(self, *args, **kwargs)
    return wrapper