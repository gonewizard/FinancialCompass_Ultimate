from abc import ABC, abstractmethod
from typing import Dict, Any, List
import matplotlib.figure


class IChartGenerator(ABC):
    """Базовый интерфейс для генерации графиков"""

    @abstractmethod
    def generate(self, data: Any, **options) -> matplotlib.figure.Figure:
        pass


class IPieChartGenerator(IChartGenerator):
    """Интерфейс для круговых диаграмм"""

    @abstractmethod
    def generate(self, expense_data: Dict[str, float], **options) -> matplotlib.figure.Figure:
        pass


class IBarChartGenerator(IChartGenerator):
    """Интерфейс для столбчатых диаграмм"""

    @abstractmethod
    def generate(self, trend_data: List[Dict[str, Any]], **options) -> matplotlib.figure.Figure:
        pass


class IBudgetChartGenerator(IChartGenerator):
    """Интерфейс для бюджетных диаграмм"""

    @abstractmethod
    def generate(self, budget_data: Dict[str, Dict[str, Any]], **options) -> matplotlib.figure.Figure:
        pass


class IChartStyler(ABC):
    """Интерфейс для стилизации графиков"""

    @abstractmethod
    def apply_style(self, figure: matplotlib.figure.Figure, style_name: str = 'default'):
        pass

    @abstractmethod
    def get_color_palette(self, palette_name: str) -> List[str]:
        pass