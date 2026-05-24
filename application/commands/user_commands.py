from dataclasses import dataclass
from core.entities.user import UserRole
from core.interfaces.services import IUserService


@dataclass
class RegisterUserCommand:
    username: str
    password: str
    role: UserRole = UserRole.USER


@dataclass
class LoginUserCommand:
    username: str
    password: str


@dataclass
class CreateAdminCommand:
    username: str
    password: str


class UserCommandHandler:
    def __init__(self, user_service: IUserService):  # Добавляем аннотацию типа
        self._user_service = user_service

    def handle_register(self, command: RegisterUserCommand):
        return self._user_service.register_user(
            command.username,
            command.password,
            command.role
        )

    def handle_login(self, command: LoginUserCommand):
        return self._user_service.authenticate_user(
            command.username,
            command.password
        )

    def handle_create_admin(self, command: CreateAdminCommand):
        return self._user_service.register_user(
            command.username,
            command.password,
            UserRole.ADMIN
        )