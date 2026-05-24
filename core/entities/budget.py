from dataclasses import dataclass
from datetime import datetime
from core.utils.validators import Validators


@dataclass
class BudgetLimit:
    id: int
    user_id: int
    category: str
    monthly_limit: float
    created_at: datetime

    def __post_init__(self):
        Validators.validate_positive(self.monthly_limit, "Monthly limit")