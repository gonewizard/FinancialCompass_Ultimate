import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from typing import Dict
from core.interfaces.visualization import IPieChartGenerator

matplotlib.use('Agg')


class PieChartGenerator(IPieChartGenerator):
    """Генератор круговых диаграмм"""

    def generate(self, expense_data: Dict[str, float], **options) -> Figure:
        if not expense_data:
            raise ValueError("No expense data provided")

        filtered_data = {k: v for k, v in expense_data.items() if v > 0}
        if not filtered_data:
            raise ValueError("No non-zero expense data")

        fig = Figure(figsize=options.get('figsize', (8, 6)))
        ax = fig.add_subplot(111)

        categories = list(filtered_data.keys())
        amounts = list(filtered_data.values())

        explode = options.get('explode', [0.05] * len(amounts))
        autopct = options.get('autopct', '%1.1f%%')
        startangle = options.get('startangle', 90)

        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=categories,
            autopct=autopct,
            startangle=startangle,
            shadow=options.get('shadow', True),
            explode=explode
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.axis('equal')
        return fig