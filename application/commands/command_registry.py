from typing import Dict, Type


class CommandRegistry:
    """Реестр команд и их обработчиков"""

    def __init__(self):
        self._handlers: Dict[Type, Type] = {}

    def register(self, command_class: Type, handler_class: Type):
        """Зарегистрировать обработчик для команды"""
        self._handlers[command_class] = handler_class

    def get_handler(self, command_class: Type) -> Type:
        """Получить обработчик для команды"""
        return self._handlers.get(command_class)

    def get_command_type(self, command_name: str) -> Type:
        """Получить тип команды по имени"""
        for cmd_class in self._handlers.keys():
            if cmd_class.__name__ == command_name:
                return cmd_class
        raise ValueError(f"Command {command_name} not found")


# Глобальный реестр
command_registry = CommandRegistry()