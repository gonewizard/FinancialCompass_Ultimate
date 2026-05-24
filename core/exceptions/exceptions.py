class FinancialCompassError(Exception):
    """Base exception for the application"""
    pass


class UserAlreadyExistsError(FinancialCompassError):
    pass


class AuthenticationError(FinancialCompassError):
    pass


class OperationValidationError(FinancialCompassError):
    pass


class OperationNotFoundError(FinancialCompassError):
    pass


class BudgetLimitExceededError(FinancialCompassError):
    pass


class PermissionError(FinancialCompassError):
    pass