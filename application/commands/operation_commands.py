from dataclasses import dataclass
from core.interfaces.services import IOperationService


@dataclass
class DeleteOperationCommand:
    operation_id: int
    user_id: int


@dataclass
class UpdateOperationCommand:
    operation_id: int
    user_id: int
    amount: float = None
    category: str = None
    description: str = None
    counterparty: str = None


class OperationCommandHandler:
    def __init__(self, operation_service: IOperationService):
        self._operation_service = operation_service

    def handle_delete_operation(self, command: DeleteOperationCommand):
        return self._operation_service.delete_operation(
            command.operation_id, command.user_id
        )

    def handle_update_operation(self, command: UpdateOperationCommand):
        update_data = {}
        if command.amount is not None:
            update_data['amount'] = command.amount
        if command.category is not None:
            update_data['category'] = command.category
        if command.description is not None:
            update_data['description'] = command.description
        if command.counterparty is not None:
            update_data['counterparty'] = command.counterparty

        return self._operation_service.update_operation(
            command.operation_id, command.user_id, **update_data
        )