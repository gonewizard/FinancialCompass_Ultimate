from dataclasses import dataclass
from datetime import datetime


@dataclass
class AutoCategoryRule:
    id: int
    user_id: int
    counterparty: str
    category: str
    created_at: datetime
    use_count: int = 1

    @classmethod
    def create(cls, user_id: int, counterparty: str, category: str) -> "AutoCategoryRule":
        return cls(
            id=0,
            user_id=user_id,
            counterparty=counterparty,
            category=category,
            created_at=datetime.now(),
            use_count=1
        )