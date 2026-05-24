from dataclasses import dataclass
from core.utils.decorators import admin_required, validate_command
from core.interfaces.services import IAdminService
from core.interfaces.repositories import IUserRepository


@dataclass
class DeactivateUserCommand:
    target_user_id: int
    admin_user_id: int


@dataclass
class ActivateUserCommand:
    target_user_id: int
    admin_user_id: int


@dataclass
class GetSystemStatsCommand:
    admin_user_id: int


class AdminCommandHandler:
    def __init__(self, admin_service: IAdminService, user_repository: IUserRepository):  # Аннотации типов
        self._admin_service = admin_service
        self._user_repository = user_repository

    @admin_required
    @validate_command
    def handle_deactivate_user(self, command: DeactivateUserCommand):
        return self._admin_service.deactivate_user(command.target_user_id)

    @admin_required
    @validate_command
    def handle_activate_user(self, command: ActivateUserCommand):
        return self._admin_service.activate_user(command.target_user_id)

    @admin_required
    @validate_command
    def handle_get_system_stats(self, command: GetSystemStatsCommand):
        return self._admin_service.get_system_statistics()