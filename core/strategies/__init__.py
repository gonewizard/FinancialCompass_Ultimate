"""
Strategy patterns
"""
from .id_generation import (
    IIdGenerationStrategy, SequentialIdStrategy,
    GapFillingIdStrategy, IdGenerator
)

__all__ = [
    'IIdGenerationStrategy', 'SequentialIdStrategy',
    'GapFillingIdStrategy', 'IdGenerator'
]