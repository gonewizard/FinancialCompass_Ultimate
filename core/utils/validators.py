from datetime import datetime
from core.exceptions import OperationValidationError


class Validators:
    @staticmethod
    def validate_positive(value: float, field_name: str) -> None:
        if value <= 0:
            raise OperationValidationError(f"{field_name} must be positive")

    @staticmethod
    def validate_not_empty(value: str, field_name: str) -> None:
        if not value or not value.strip():
            raise OperationValidationError(f"{field_name} cannot be empty")

    @staticmethod
    def validate_username(username: str) -> None:
        if not username or len(username) < 3:
            raise OperationValidationError("Username must be at least 3 characters long")

    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> None:
        if start_date > end_date:
            raise OperationValidationError("Start date must be before end date")