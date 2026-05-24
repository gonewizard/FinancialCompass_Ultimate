from typing import Dict, Type, Any
from dataclasses import dataclass
import inspect
import sys
import os


@dataclass
class ServiceDefinition:
    interface: Type
    implementation: Any
    singleton: bool = True
    instance: Any = None


class DIContainer:
    """Контейнер зависимостей для инверсии управления"""

    def __init__(self):
        self._services: Dict[Type, ServiceDefinition] = {}
        self._instances: Dict[Type, Any] = {}
        self._params: Dict[str, Any] = {}

    def register(self, interface: Type, implementation: Any, singleton: bool = True):
        """Зарегистрировать сервис"""
        self._services[interface] = ServiceDefinition(
            interface=interface,
            implementation=implementation,
            singleton=singleton
        )

    def register_instance(self, interface: Type, instance: Any):
        """Зарегистрировать готовый экземпляр"""
        self._instances[interface] = instance

    def register_param(self, name: str, value: Any):
        """Зарегистрировать параметр"""
        self._params[name] = value

    def get_param(self, name: str, default: Any = None) -> Any:
        """Получить параметр"""
        return self._params.get(name, default)

    def resolve(self, interface: Type) -> Any:
        """Получить экземпляр сервиса"""
        # Проверяем готовые экземпляры
        if interface in self._instances:
            return self._instances[interface]

        # Ищем зарегистрированный сервис
        if interface in self._services:
            definition = self._services[interface]

            # Синглтон - возвращаем существующий или создаем новый
            if definition.singleton:
                if definition.instance is None:
                    definition.instance = self._create_instance(definition.implementation)
                return definition.instance

            # Не синглтон - создаем новый
            return self._create_instance(definition.implementation)

        # Пытаемся создать экземпляр напрямую
        try:
            return self._create_instance(interface)
        except Exception:
            raise ValueError(f"Service {interface} not registered and cannot be instantiated")

    def _create_instance(self, target: Any) -> Any:
        """Создать экземпляр с автоматическим внедрением зависимостей"""
        # Если target - вызываемый объект (функция-фабрика)
        if callable(target) and not inspect.isclass(target):
            return self._call_with_di(target)

        # Если target - класс
        if inspect.isclass(target):
            return self._instantiate_class(target)

        # В остальных случаях возвращаем как есть
        return target

    def _instantiate_class(self, cls: Type) -> Any:
        """Создать экземпляр класса с DI"""
        import inspect

        try:
            # Получаем сигнатуру конструктора
            signature = inspect.signature(cls.__init__)

            # Собираем аргументы
            kwargs = {}
            for param_name, param in signature.parameters.items():
                if param_name == 'self':
                    continue

                # Получаем аннотацию типа
                param_type = param.annotation

                # Если тип указан
                if param_type != inspect.Parameter.empty and param_type not in (str, int, float, bool):
                    try:
                        # Пытаемся разрешить зависимость
                        kwargs[param_name] = self.resolve(param_type)
                    except (ValueError, KeyError):
                        # Если не нашли, проверяем параметры
                        if param_name in self._params:
                            kwargs[param_name] = self._params[param_name]
                        elif param.default != inspect.Parameter.empty:
                            # Используем значение по умолчанию
                            pass
                        else:
                            # Пропускаем параметры без значений по умолчанию
                            pass
                elif param_name in self._params:
                    # Используем параметр
                    kwargs[param_name] = self._params[param_name]
                elif param.default != inspect.Parameter.empty:
                    # Используем значение по умолчанию
                    pass

            return cls(**kwargs)
        except Exception as e:
            # Если не удалось создать с DI, пробуем создать без аргументов
            try:
                return cls()
            except:
                raise ValueError(f"Cannot instantiate {cls}: {e}")

    def _call_with_di(self, func):
        """Вызвать функцию с внедрением зависимостей"""
        import inspect
        signature = inspect.signature(func)

        kwargs = {}
        for param_name, param in signature.parameters.items():
            param_type = param.annotation

            if param_type != inspect.Parameter.empty and param_type not in (str, int, float, bool):
                try:
                    kwargs[param_name] = self.resolve(param_type)
                except ValueError:
                    if param_name in self._params:
                        kwargs[param_name] = self._params[param_name]

        return func(**kwargs)

    def create_scope(self) -> 'DIContainer':
        """Создать новый скоуп (для запросов)"""
        scoped_container = DIContainer()
        scoped_container._services = self._services.copy()
        scoped_container._params = self._params.copy()
        scoped_container._instances = {}
        return scoped_container

    def register_backup_services(self, db_path: str = None):
        """
        Регистрация сервисов для резервного копирования.
        """
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from application.services.backup_service import BackupService
            from application.commands.backup_commands import BackupCommandHandler
            from core.interfaces.services import IBackupService

            if db_path:
                self.register_param('db_path', db_path)

            self.register(IBackupService, BackupService, singleton=True)

            backup_service = self.resolve(IBackupService)
            backup_command_handler = BackupCommandHandler(backup_service)
            self.register_instance(BackupCommandHandler, backup_command_handler)

        except ImportError as e:
            print(f"Ошибка импорта при регистрации сервисов резервного копирования: {e}")
            raise


# Глобальный контейнер
container = DIContainer()