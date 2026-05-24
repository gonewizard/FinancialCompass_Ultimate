from typing import Any
from .container import DIContainer


class ServiceProvider:
    """Провайдер сервисов для удобного доступа"""

    def __init__(self, container: DIContainer):
        self._container = container

    @property
    def user_service(self) -> Any:
        from core.interfaces.services import IUserService
        return self._container.resolve(IUserService)

    @property
    def operation_service(self) -> Any:
        from core.interfaces.services import IOperationService
        return self._container.resolve(IOperationService)

    @property
    def budget_service(self) -> Any:
        from core.interfaces.services import IBudgetService
        return self._container.resolve(IBudgetService)

    @property
    def admin_service(self) -> Any:
        from core.interfaces.services import IAdminService
        return self._container.resolve(IAdminService)

    @property
    def report_service(self) -> Any:
        from core.interfaces.services import IReportService
        return self._container.resolve(IReportService)

    @property
    def financial_calculator(self) -> Any:
        from core.interfaces.services import IFinancialCalculator
        return self._container.resolve(IFinancialCalculator)

    @property
    def visualization_service(self) -> Any:
        from core.interfaces.visualization import IChartGenerator
        return self._container.resolve(IChartGenerator)

    def get_command_handler(self, command_type):
        """Получить обработчик команды по типу команды"""
        from application.commands import command_registry
        handler_class = command_registry.get_handler(command_type)
        return self._container.resolve(handler_class)