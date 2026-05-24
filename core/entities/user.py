from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = None
    initial_balance: float = 0.0

    def has_admin_privileges(self) -> bool:
        return self.role == UserRole.ADMIN