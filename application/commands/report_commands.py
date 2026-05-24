from dataclasses import dataclass
from core.interfaces.services import IReportService
from core.interfaces.visualization import IChartGenerator


@dataclass
class GenerateCategoryReportCommand:
    user_id: int
    months: int = 1


@dataclass
class GenerateTrendReportCommand:
    user_id: int
    months: int = 6


@dataclass
class GenerateBudgetReportCommand:
    user_id: int


class ReportCommandHandler:
    def __init__(self, report_service: IReportService, visualization_service: IChartGenerator):  # Аннотации типов
        self._report_service = report_service
        self._visualization_service = visualization_service

    def handle_category_report(self, command: GenerateCategoryReportCommand):
        """Обработать запрос на создание отчета по категориям"""
        report_data = self._report_service.generate_category_report(
            command.user_id, command.months
        )

        return {
            'report_data': report_data,
            'success': True
        }

    def handle_trend_report(self, command: GenerateTrendReportCommand):
        """Обработать запрос на создание трендового отчета"""
        report_data = self._report_service.generate_trend_report(
            command.user_id, command.months
        )

        return {
            'report_data': report_data,
            'success': True
        }

    def handle_budget_report(self, command: GenerateBudgetReportCommand):
        """Обработать запрос на создание отчета по бюджету"""
        return {
            'message': 'Use budget commands for budget reports',
            'success': True
        }