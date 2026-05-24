from typing import Optional
from core.entities.user import User, UserRole
from core.interfaces.repositories import IUserRepository
from core.interfaces.services import IUserService, IAuthenticationService


class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository, auth_service: IAuthenticationService):
        self._user_repository = user_repository
        self._auth_service = auth_service

    def register_user(self, username: str, password: str, role: UserRole = UserRole.USER) -> User:
        existing = self._user_repository.find_by_username(username)
        if existing:
            raise ValueError(f"Пользователь с именем '{username}' уже существует")

        password_hash = self._auth_service.hash_password(password)
        user = User(
            id=0,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        return self._user_repository.save(user)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self._user_repository.find_by_username(username)
        if not user:
            return None
        if not user.is_active:
            return None
        if self._auth_service.verify_password(password, user.password_hash):
            return user
        return None

    def update_initial_balance(self, user_id: int, balance: float) -> bool:
        return self._user_repository.update_initial_balance(user_id, balance)

    def needs_initial_balance(self, user_id: int) -> bool:
        return self._user_repository.get_initial_balance(user_id) == 0

    def get_theme(self, user_id: int) -> str:
        return self._user_repository.get_theme(user_id)

    def update_theme(self, user_id: int, theme: str) -> bool:
        return self._user_repository.update_theme(user_id, theme)

    def get_color_theme(self, user_id: int) -> str:
        return self._user_repository.get_color_theme(user_id)

    def update_color_theme(self, user_id: int, color_theme: str) -> bool:
        return self._user_repository.update_color_theme(user_id, color_theme)

    def get_font_size(self, user_id: int) -> int:
        return self._user_repository.get_font_size(user_id)

    def update_font_size(self, user_id: int, font_size: int) -> bool:
        return self._user_repository.update_font_size(user_id, font_size)