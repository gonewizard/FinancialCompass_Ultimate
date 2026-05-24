import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, Any, List
import os
from datetime import datetime

matplotlib.use('Agg')


class VisualizationService:
    """Сервис визуализации (для обратной совместимости)"""

    def __init__(self, output_dir: str = "reports"):
        self._output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_expense_pie_chart(self, expense_data: Dict[str, float], user_id: int) -> str:
        """Создать круговую диаграмму расходов по категориям"""
        if not expense_data:
            raise ValueError("No expense data provided")

        filtered_data = {k: v for k, v in expense_data.items() if v > 0}
        if not filtered_data:
            raise ValueError("No non-zero expense data")

        plt.figure(figsize=(10, 8))
        categories = list(filtered_data.keys())
        amounts = list(filtered_data.values())

        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title('Распределение расходов по категориям', fontsize=16, fontweight='bold')

        filename = f"expense_pie_chart_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self._output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=100)
        plt.close()

        return filepath

    def create_income_expense_trend(self, trend_data: List[Dict[str, Any]], user_id: int) -> str:
        """Создать график динамики доходов и расходов"""
        if not trend_data:
            raise ValueError("No trend data provided")

        months = [item['month'] for item in trend_data]
        incomes = [item['income'] for item in trend_data]
        expenses = [item['expense'] for item in trend_data]

        plt.figure(figsize=(12, 6))
        x_pos = range(len(months))
        bar_width = 0.35

        plt.bar([x - bar_width / 2 for x in x_pos], incomes, bar_width,
                label='Доходы', color='green', alpha=0.7)
        plt.bar([x + bar_width / 2 for x in x_pos], expenses, bar_width,
                label='Расходы', color='red', alpha=0.7)

        plt.xlabel('Месяцы')
        plt.ylabel('Сумма')
        plt.title('Динамика доходов и расходов', fontsize=16, fontweight='bold')
        plt.xticks(x_pos, months, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = f"trend_chart_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self._output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=100)
        plt.close()

        return filepath

    def create_budget_progress_chart(self, budget_data: Dict[str, Dict], user_id: int) -> str:
        """Создать график прогресса по бюджетным лимитам"""
        if not budget_data:
            raise ValueError("No budget data provided")

        categories = list(budget_data.keys())
        limits = [data['limit'] for data in budget_data.values()]
        current = [data['current'] for data in budget_data.values()]
        percentages = [data['percentage'] for data in budget_data.values()]

        plt.figure(figsize=(12, 8))
        x_pos = range(len(categories))
        bar_width = 0.35

        plt.bar([x - bar_width / 2 for x in x_pos], limits, bar_width,
                label='Лимит', color='lightblue', alpha=0.7)
        plt.bar([x + bar_width / 2 for x in x_pos], current, bar_width,
                label='Факт', color='orange', alpha=0.7)

        for i, (limit, curr, percent) in enumerate(zip(limits, current, percentages)):
            plt.text(i, max(limit, curr) + max(limit, curr) * 0.05,
                     f'{percent}%', ha='center', va='bottom', fontweight='bold')

        plt.xlabel('Категории')
        plt.ylabel('Сумма')
        plt.title('Прогресс по бюджетным лимитам', fontsize=16, fontweight='bold')
        plt.xticks(x_pos, categories, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = f"budget_progress_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self._output_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', dpi=100)
        plt.close()

        return filepath

    def cleanup_old_reports(self, max_age_hours: int = 24):
        """Очистить старые отчеты"""
        now = datetime.now()
        for filename in os.listdir(self._output_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self._output_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                if (now - file_time).total_seconds() > max_age_hours * 3600:
                    os.remove(filepath)