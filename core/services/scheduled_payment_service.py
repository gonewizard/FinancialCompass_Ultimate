from typing import List, Optional
from datetime import date
from core.entities.scheduled_payment import ScheduledPayment, PaymentFrequency
from core.interfaces.repositories import IScheduledPaymentRepository, IOperationRepository
from core.interfaces.services import IScheduledPaymentService


class ScheduledPaymentService(IScheduledPaymentService):

    def __init__(self, payment_repository: IScheduledPaymentRepository, operation_repository: IOperationRepository):
        self._payment_repository = payment_repository
        self._operation_repository = operation_repository

    def create_payment(self, user_id: int, name: str, amount: float, category: str,
                       frequency: PaymentFrequency, start_date: date,
                       description: Optional[str] = None) -> ScheduledPayment:
        payment = ScheduledPayment.create(
            user_id=user_id,
            name=name,
            amount=amount,
            category=category,
            frequency=frequency,
            start_date=start_date,
            description=description
        )
        return self._payment_repository.save(payment)

    def create_payment_with_next_due(self, user_id: int, name: str, amount: float, category: str,
                                      frequency: PaymentFrequency, start_date: date, next_due_date: date,
                                      description: Optional[str] = None) -> ScheduledPayment:
        from datetime import datetime
        payment = ScheduledPayment(
            id=0,
            user_id=user_id,
            name=name,
            amount=amount,
            category=category,
            frequency=frequency,
            start_date=start_date,
            next_due_date=next_due_date,
            description=description,
            is_active=True,
            created_at=datetime.now()
        )
        return self._payment_repository.save(payment)

    def get_payments(self, user_id: int, is_active: Optional[bool] = None) -> List[ScheduledPayment]:
        return self._payment_repository.find_by_user(user_id, is_active)

    def get_payment_by_id(self, payment_id: int) -> Optional[ScheduledPayment]:
        return self._payment_repository.find_by_id(payment_id)

    def get_due_payments(self, user_id: int) -> List[ScheduledPayment]:
        return self._payment_repository.find_due_payments(user_id, date.today())

    def mark_as_paid(self, payment_id: int) -> ScheduledPayment:
        payment = self._payment_repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with ID {payment_id} not found")

        payment.advance()
        self._payment_repository.update_next_due_date(payment.id, payment.next_due_date)
        return payment

    def delete_payment(self, payment_id: int) -> bool:
        return self._payment_repository.delete(payment_id)

    def toggle_active(self, payment_id: int) -> ScheduledPayment:
        payment = self._payment_repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with ID {payment_id} not found")

        payment.is_active = not payment.is_active
        return self._payment_repository.save(payment)

    def get_monthly_total(self, user_id: int) -> float:
        payments = self._payment_repository.find_by_user(user_id, is_active=True)

        monthly_total = 0.0
        for payment in payments:
            if payment.frequency == PaymentFrequency.DAILY:
                monthly_total += payment.amount * 30
            elif payment.frequency == PaymentFrequency.WEEKLY:
                monthly_total += payment.amount * 4
            elif payment.frequency == PaymentFrequency.MONTHLY:
                monthly_total += payment.amount
            elif payment.frequency == PaymentFrequency.YEARLY:
                monthly_total += payment.amount / 12

        return monthly_total

    def update_next_due_date(self, payment_id: int, next_due_date: date) -> bool:
        payment = self._payment_repository.find_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with ID {payment_id} not found")
        payment.next_due_date = next_due_date
        self._payment_repository.save(payment)
        return True