from typing import Dict, List
import matplotlib.figure
from core.interfaces.visualization import IChartStyler


class DefaultChartStyler(IChartStyler):
    """Стилизатор графиков по умолчанию"""

    def __init__(self):
        self._styles = {
            'default': {
                'title_fontsize': 14,
                'title_fontweight': 'bold',
                'grid': True,
                'grid_alpha': 0.3,
                'grid_linestyle': '--',
            },
            'minimal': {
                'title_fontsize': 12,
                'grid': True,
                'grid_alpha': 0.1,
                'hide_spines': ['top', 'right'],
            },
            'presentation': {
                'title_fontsize': 16,
                'title_pad': 20,
                'grid': True,
                'grid_alpha': 0.5,
            }
        }

        self._color_palettes = {
            'default': ['#2ecc71', '#e74c3c', '#3498db', '#f39c12', '#9b59b6'],
            'pastel': ['#a8e6cf', '#dcedc1', '#ffd3b6', '#ffaaa5', '#ff8b94'],
            'corporate': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        }

    def apply_style(self, figure: matplotlib.figure.Figure, style_name: str = 'default'):
        """Применить стиль к графику"""
        style = self._styles.get(style_name, self._styles['default'])

        for ax in figure.axes:
            # Применяем настройки заголовка
            title = ax.get_title()
            if title:
                ax.set_title(
                    title,
                    fontsize=style.get('title_fontsize', 14),
                    fontweight=style.get('title_fontweight', 'bold'),
                    pad=style.get('title_pad', 20)
                )

            # Настройка сетки - ПРОСТО УСТАНАВЛИВАЕМ, не проверяем
            if style.get('grid', True):
                ax.grid(
                    True,
                    alpha=style.get('grid_alpha', 0.3),
                    linestyle=style.get('grid_linestyle', '--')
                )
            else:
                ax.grid(False)

            # Скрытие осей
            hide_spines = style.get('hide_spines', [])
            for spine in hide_spines:
                ax.spines[spine].set_visible(False)

    def get_color_palette(self, palette_name: str) -> List[str]:
        """Получить палитру цветов"""
        return self._color_palettes.get(palette_name, self._color_palettes['default'])

    def register_style(self, name: str, style_config: Dict):
        """Зарегистрировать новый стиль"""
        self._styles[name] = style_config

    def register_color_palette(self, name: str, colors: List[str]):
        """Зарегистрировать новую палитру"""
        self._color_palettes[name] = colors