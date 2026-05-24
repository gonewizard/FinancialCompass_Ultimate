import matplotlib
from matplotlib.figure import Figure
from typing import Dict, Any
from core.interfaces.visualization import IBudgetChartGenerator

matplotlib.use('Agg')


class BudgetChartGenerator(IBudgetChartGenerator):
    """Генератор бюджетных диаграмм"""

    def generate(self, budget_data: Dict[str, Dict[str, Any]], **options) -> Figure:
        if not budget_data:
            raise ValueError("No budget data provided")

        categories = list(budget_data.keys())
        limits = [data['limit'] for data in budget_data.values()]
        current = [data['current'] for data in budget_data.values()]
        percentages = [data['percentage'] for data in budget_data.values()]

        fig = Figure(figsize=options.get('figsize', (12, 6)))
        ax = fig.add_subplot(111)

        x_pos = range(len(categories))
        bar_width = options.get('bar_width', 0.35)

        limit_color = options.get('limit_color', '#3498db')
        current_color = options.get('current_color', '#f39c12')

        bars_limits = ax.bar(
            [x - bar_width / 2 for x in x_pos],
            limits,
            bar_width,
            label='Лимит',
            color=limit_color,
            alpha=0.7,
            edgecolor='black'
        )

        bars_current = ax.bar(
            [x + bar_width / 2 for x in x_pos],
            current,
            bar_width,
            label='Факт',
            color=current_color,
            alpha=0.7,
            edgecolor='black'
        )

        for i, (limit, curr, percent) in enumerate(zip(limits, current, percentages)):
            color = '#e74c3c' if percent > 100 else '#27ae60'
            weight = 'bold' if percent > 100 else 'normal'

            ax.text(
                i,
                max(limit, curr) + max(limit, curr) * 0.05,
                f'{percent:.1f}%',
                ha='center',
                va='bottom',
                fontweight=weight,
                color=color,
                fontsize=10
            )

            if percent > 100:
                bars_current[i].set_color('#e74c3c')
                bars_current[i].set_alpha(1.0)

        ax.set_xlabel('Категории', fontweight='bold')
        ax.set_ylabel('Сумма (руб.)', fontweight='bold')
        ax.set_title('Прогресс по бюджетным лимитам', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, linestyle='--')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout()
        return fig