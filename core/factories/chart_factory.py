from typing import Dict, Any
import matplotlib.figure
from core.interfaces.visualization import (
    IPieChartGenerator, IBarChartGenerator,
    IBudgetChartGenerator, IChartStyler
)


class ChartFactory:
    """Фабрика для создания графиков"""

    def __init__(self, styler: IChartStyler = None):
        self._styler = styler

    def create_pie_chart(self, generator: IPieChartGenerator,
                         data: Dict[str, float],
                         title: str = None,
                         **options) -> matplotlib.figure.Figure:
        """Создать круговую диаграмму"""
        figure = generator.generate(data, **options)

        if title:
            figure.axes[0].set_title(title)

        if self._styler:
            self._styler.apply_style(figure, options.get('style', 'default'))

        return figure

    def create_bar_chart(self, generator: IBarChartGenerator,
                         data: Any,
                         title: str = None,
                         x_label: str = None,
                         y_label: str = None,
                         **options) -> matplotlib.figure.Figure:
        """Создать столбчатую диаграмму"""
        figure = generator.generate(data, **options)

        if title:
            figure.axes[0].set_title(title)
        if x_label:
            figure.axes[0].set_xlabel(x_label)
        if y_label:
            figure.axes[0].set_ylabel(y_label)

        if self._styler:
            self._styler.apply_style(figure, options.get('style', 'default'))

        return figure

    def create_budget_chart(self, generator: IBudgetChartGenerator,
                            data: Dict[str, Dict[str, Any]],
                            title: str = None,
                            **options) -> matplotlib.figure.Figure:
        """Создать бюджетную диаграмму"""
        figure = generator.generate(data, **options)

        if title:
            figure.axes[0].set_title(title)

        if self._styler:
            self._styler.apply_style(figure, options.get('style', 'default'))

        return figure