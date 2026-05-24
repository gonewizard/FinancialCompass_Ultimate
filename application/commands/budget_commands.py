from dataclasses import dataclass
from typing import Optional
from core.di.container import container
from core.factories.chart_factory import ChartFactory
from core.interfaces.visualization import IBudgetChartGenerator
from core.interfaces.services import IBudgetService


@dataclass
class SetBudgetLimitCommand:
    user_id: int
    category: str
    monthly_limit: float


@dataclass
class GetBudgetLimitsCommand:
    user_id: int


@dataclass
class CheckBudgetStatusCommand:
    user_id: int


@dataclass
class DeleteBudgetLimitCommand:
    user_id: int
    category: str


class BudgetCommandHandler:
    def __init__(self, budget_service: IBudgetService, chart_factory: ChartFactory = None):  # Аннотация типа
        self._budget_service = budget_service
        self._chart_factory = chart_factory or container.resolve(ChartFactory)

    def handle_set_limit(self, command: SetBudgetLimitCommand):
        """Обработать установку лимита"""
        return self._budget_service.set_budget_limit(
            command.user_id, command.category, command.monthly_limit
        )

    def handle_get_limits(self, command: GetBudgetLimitsCommand):
        """Обработать запрос на получение лимитов"""
        return self._budget_service.get_user_limits(command.user_id)

    def handle_check_status(self, command: CheckBudgetStatusCommand):
        """Обработать проверку статуса лимитов"""
        status = self._budget_service.check_budget_limits(command.user_id)

        chart_path: Optional[str] = None
        if status:
            chart_generator = container.resolve(IBudgetChartGenerator)
            chart = self._chart_factory.create_budget_chart(
                chart_generator,
                status,
                title='Прогресс по бюджетным лимитам',
                style='default'
            )
            chart_path = self._save_chart(chart, command.user_id)

        return {
            'status': status,
            'chart_path': chart_path
        }

    def handle_delete_limit(self, command: DeleteBudgetLimitCommand):
        """Обработать удаление лимита"""
        return self._budget_service.delete_limit(command.user_id, command.category)

    def _save_chart(self, chart, user_id: int) -> str:
        """Сохранить график в файл"""
        import os
        from datetime import datetime

        os.makedirs('reports', exist_ok=True)
        filename = f"budget_progress_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join('reports', filename)

        chart.savefig(filepath, bbox_inches='tight', dpi=100)
        return filepath