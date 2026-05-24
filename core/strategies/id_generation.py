from abc import ABC, abstractmethod
from typing import List, Optional


class IIdGenerationStrategy(ABC):
    """Стратегия генерации ID"""

    @abstractmethod
    def get_next_id(self, existing_ids: List[int]) -> int:
        pass

    @abstractmethod
    def get_available_ids(self, existing_ids: List[int]) -> List[int]:
        pass


class SequentialIdStrategy(IIdGenerationStrategy):
    """Последовательная генерация (1, 2, 3...)"""

    def get_next_id(self, existing_ids: List[int]) -> int:
        if not existing_ids:
            return 1
        return max(existing_ids) + 1

    def get_available_ids(self, existing_ids: List[int]) -> List[int]:
        if not existing_ids:
            return [1]

        available = []
        max_id = max(existing_ids)
        for i in range(1, max_id + 1):
            if i not in existing_ids:
                available.append(i)

        if not available:
            available.append(max_id + 1)

        return available


class GapFillingIdStrategy(IIdGenerationStrategy):
    """Заполнение пропусков (переиспользование ID)"""

    def get_next_id(self, existing_ids: List[int]) -> int:
        if not existing_ids:
            return 1

        for i in range(1, max(existing_ids) + 2):
            if i not in existing_ids:
                return i

        return max(existing_ids) + 1

    def get_available_ids(self, existing_ids: List[int]) -> List[int]:
        if not existing_ids:
            return [1]

        available = []
        for i in range(1, max(existing_ids) + 1):
            if i not in existing_ids:
                available.append(i)

        return available


class IdGenerator:
    """Генератор ID с поддержкой стратегий"""

    def __init__(self, strategy: IIdGenerationStrategy = None):
        self._strategy = strategy or GapFillingIdStrategy()

    def set_strategy(self, strategy: IIdGenerationStrategy):
        self._strategy = strategy

    def generate_next_id(self, existing_ids: List[int]) -> int:
        return self._strategy.get_next_id(existing_ids)

    def get_all_available_ids(self, existing_ids: List[int]) -> List[int]:
        return self._strategy.get_available_ids(existing_ids)