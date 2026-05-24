"""
Custom exceptions
"""
from .exceptions import (
    FinancialCompassError,
    UserAlreadyExistsError,
    AuthenticationError,
    OperationValidationError,
    OperationNotFoundError,
    BudgetLimitExceededError,
    PermissionError
)

__all__ = [
    'FinancialCompassError',
    'UserAlreadyExistsError',
    'AuthenticationError',
    'OperationValidationError',
    'OperationNotFoundError',
    'BudgetLimitExceededError',
    'PermissionError'
]