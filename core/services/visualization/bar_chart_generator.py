import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from typing import List, Dict, Any
from core.interfaces.visualization import IBarChartGenerator

matplotlib.use('Agg')


class BarChartGenerator(IBarChartGenerator):
    """Генератор столбчатых диаграмм"""

    def generate(self, trend_data: List[Dict[str, Any]], **options) -> Figure:
        if not trend_data:
            raise ValueError("No trend data provided")

        months = [item['month'] for item in trend_data]
        incomes = [item['income'] for item in trend_data]
        expenses = [item['expense'] for item in trend_data]

        fig = Figure(figsize=options.get('figsize', (10, 6)))
        ax = fig.add_subplot(111)

        x_pos = range(len(months))
        bar_width = options.get('bar_width', 0.35)

        income_color = options.get('income_color', '#2ecc71')
        expense_color = options.get('expense_color', '#e74c3c')

        bars_income = ax.bar(
            [x - bar_width / 2 for x in x_pos],
            incomes,
            bar_width,
            label='Доходы',
            color=income_color,
            alpha=0.8,
            edgecolor='black'
        )

        bars_expense = ax.bar(
            [x + bar_width / 2 for x in x_pos],
            expenses,
            bar_width,
            label='Расходы',
            color=expense_color,
            alpha=0.8,
            edgecolor='black'
        )

        if options.get('show_values', True):
            self._add_value_labels(ax, bars_income)
            self._add_value_labels(ax, bars_expense)

        ax.set_xlabel('Месяцы', fontweight='bold')
        ax.set_ylabel('Сумма (руб.)', fontweight='bold')
        ax.set_title('Динамика доходов и расходов', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout()
        return fig

    def _add_value_labels(self, ax, bars):
        """Добавить значения на столбцы"""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + height * 0.01,
                    f'{height:.0f}',
                    ha='center',
                    va='bottom',
                    fontsize=9
                )