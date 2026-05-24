import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import Dict, Any, List
import os
from datetime import datetime

matplotlib.use('Agg')


class ImprovedVisualizationService:
    """Улучшенный сервис визуализации (для обратной совместимости)"""

    def __init__(self, output_dir: str = "reports"):
        self._output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        plt.style.use('seaborn-v0_8')

    def create_expense_pie_chart(self, expense_data: Dict[str, float], user_id: int) -> Figure:
        """Создать круговую диаграмму расходов по категориям"""
        from core.services.visualization.pie_chart_generator import PieChartGenerator
        generator = PieChartGenerator()
        return generator.generate(expense_data)

    def create_income_expense_trend(self, trend_data: List[Dict[str, Any]], user_id: int) -> Figure:
        """Создать график динамики доходов и расходов"""
        from core.services.visualization.bar_chart_generator import BarChartGenerator
        generator = BarChartGenerator()
        return generator.generate(trend_data)

    def create_budget_progress_chart(self, budget_data: Dict[str, Dict], user_id: int) -> Figure:
        """Создать график прогресса по бюджетным лимитам"""
        from core.services.visualization.budget_chart_generator import BudgetChartGenerator
        generator = BudgetChartGenerator()
        return generator.generate(budget_data)

    def create_combined_financial_chart(self, trend_data: List[Dict], budget_data: Dict, user_id: int) -> Figure:
        """Создать комбинированный график с трендами и лимитами"""
        fig = Figure(figsize=(14, 10))

        if trend_data:
            ax1 = fig.add_subplot(211)
            months = [item['month'] for item in trend_data]
            incomes = [item['income'] for item in trend_data]
            expenses = [item['expense'] for item in trend_data]

            x_pos = range(len(months))
            ax1.plot(x_pos, incomes, 'o-', color='#2ecc71', linewidth=2, markersize=6, label='Доходы')
            ax1.plot(x_pos, expenses, 'o-', color='#e74c3c', linewidth=2, markersize=6, label='Расходы')
            ax1.fill_between(x_pos, incomes, expenses, where=[i >= e for i, e in zip(incomes, expenses)],
                             color='#2ecc71', alpha=0.2, label='Профицит')
            ax1.fill_between(x_pos, incomes, expenses, where=[i < e for i, e in zip(incomes, expenses)],
                             color='#e74c3c', alpha=0.2, label='Дефицит')

            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(months, rotation=45)
            ax1.set_title('Динамика доходов и расходов', fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        if budget_data:
            ax2 = fig.add_subplot(212)
            categories = list(budget_data.keys())
            percentages = [data['percentage'] for data in budget_data.values()]

            colors = ['#e74c3c' if p > 100 else '#27ae60' for p in percentages]
            bars = ax2.bar(categories, percentages, color=colors, alpha=0.7, edgecolor='black')

            for bar, percentage in zip(bars, percentages):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height + 2,
                         f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')

            ax2.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Лимит 100%')
            ax2.set_xticklabels(categories, rotation=45)
            ax2.set_title('Использование бюджетных лимитов (%)', fontweight='bold')
            ax2.set_ylabel('Процент использования')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        return fig

    def _add_value_labels(self, ax, bars):
        """Добавить значения на столбцы диаграммы"""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height + height * 0.01,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=9)

    def create_canvas_for_tkinter(self, fig, parent):
        """Создать canvas для отображения в tkinter"""
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        return canvas

    def cleanup_old_reports(self, max_age_hours: int = 24):
        """Очистить старые отчеты"""
        now = datetime.now()
        for filename in os.listdir(self._output_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self._output_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if (now - file_time).total_seconds() > max_age_hours * 3600:
                    os.remove(filepath)