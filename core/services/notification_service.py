from typing import List, Dict, Any
from datetime import datetime, timedelta
from core.entities.operation import OperationType
from core.interfaces.repositories import IOperationRepository, IBudgetRepository, IScheduledPaymentRepository
from core.interfaces.services import IGoalService, INotificationService


class NotificationService(INotificationService):

    def __init__(self, operation_repository: IOperationRepository,
                 budget_repository: IBudgetRepository,
                 goal_service: IGoalService,
                 payment_repository: IScheduledPaymentRepository):
        self._operation_repository = operation_repository
        self._budget_repository = budget_repository
        self._goal_service = goal_service
        self._payment_repository = payment_repository

    def check_budget_limits(self, user_id: int, category: str, new_amount: float) -> List[Dict[str, Any]]:
        notifications = []

        try:
            limits = self._budget_repository.find_all_by_user(user_id)

            for limit in limits:
                if limit.category == category:
                    current_expenses = self._operation_repository.get_expenses_by_category(user_id)
                    current = current_expenses.get(category, 0)

                    total_after = current + new_amount
                    limit_value = limit.monthly_limit

                    if total_after > limit_value:
                        overflow = total_after - limit_value

                        notifications.append({
                            'title': 'Превышение бюджета',
                            'message': f"Категория: {category}\n"
                                       f"Лимит: {limit_value:.2f} руб.\n"
                                       f"Уже потрачено: {current:.2f} руб.\n"
                                       f"Новая трата: {new_amount:.2f} руб.\n"
                                       f"Итого: {total_after:.2f} руб.\n"
                                       f"Превышение: {overflow:.2f} руб.",
                            'type': 'danger'
                        })
                    elif total_after == limit_value:
                        notifications.append({
                            'title': 'Лимит исчерпан',
                            'message': f"Категория: {category}\n"
                                       f"Лимит: {limit_value:.2f} руб.\n"
                                       f"Потрачено: {current:.2f} руб.\n"
                                       f"Новая трата: {new_amount:.2f} руб.\n"
                                       f"Лимит полностью исчерпан.",
                            'type': 'danger'
                        })
                    elif total_after > limit_value * 0.9:
                        notifications.append({
                            'title': 'Лимит почти исчерпан',
                            'message': f"Категория: {category}\n"
                                       f"Лимит: {limit_value:.2f} руб.\n"
                                       f"Потрачено: {current:.2f} руб. ({(current/limit_value*100):.0f}%)\n"
                                       f"Новая трата: {new_amount:.2f} руб.\n"
                                       f"Осталось: {limit_value - total_after:.2f} руб.",
                            'type': 'warning'
                        })
        except Exception as e:
            print(f"Ошибка при проверке лимитов: {e}")

        return notifications

    def check_goal_deadlines(self, user_id: int) -> List[Dict[str, Any]]:
        notifications = []

        goals = self._goal_service.get_goals(user_id)

        for goal in goals:
            if not goal.deadline or goal.is_completed:
                continue

            days_left = (goal.deadline - datetime.now()).days

            if days_left < 0:
                notifications.append({
                    'type': 'danger',
                    'title': f'Просрочена цель: {goal.name}',
                    'message': f'Целевая сумма: {goal.target_amount:.2f} руб.\n'
                               f'Накоплено: {goal.current_amount:.2f} руб.\n'
                               f'Осталось: {goal.remaining_amount:.2f} руб.',
                    'goal': goal
                })
            elif days_left <= 7:
                notifications.append({
                    'type': 'warning',
                    'title': f'Скоро дедлайн цели: {goal.name}',
                    'message': f'Осталось дней: {days_left}\n'
                               f'Осталось накопить: {goal.remaining_amount:.2f} руб.',
                    'goal': goal
                })

        return notifications

    def check_goal_progress(self, user_id: int) -> List[Dict[str, Any]]:
        notifications = []

        goals = self._goal_service.get_goals(user_id)

        for goal in goals:
            if goal.is_completed or goal.status.value == "cancelled":
                continue

            progress_percent = goal.progress_percent

            if 50 <= progress_percent < 51:
                notifications.append({
                    'type': 'success',
                    'title': f'Половина цели достигнута',
                    'message': f'Цель: {goal.name}\n'
                               f'Накоплено: {goal.current_amount:.2f} руб. из {goal.target_amount:.2f} руб. (50%)',
                    'goal': goal
                })
            elif 75 <= progress_percent < 76:
                notifications.append({
                    'type': 'success',
                    'title': f'Осталось немного',
                    'message': f'Цель: {goal.name}\n'
                               f'Накоплено: {goal.current_amount:.2f} руб. из {goal.target_amount:.2f} руб. (75%)',
                    'goal': goal
                })
            elif 90 <= progress_percent < 91:
                notifications.append({
                    'type': 'success',
                    'title': f'Почти у цели',
                    'message': f'Цель: {goal.name}\n'
                               f'Накоплено: {goal.current_amount:.2f} руб. из {goal.target_amount:.2f} руб. (90%)',
                    'goal': goal
                })
            elif progress_percent >= 100 and goal.status.value != "completed":
                notifications.append({
                    'type': 'success',
                    'title': f'Цель достигнута. Поздравляем!',
                    'message': f'Цель: {goal.name}\n'
                               f'Накоплено: {goal.current_amount:.2f} руб.',
                    'goal': goal
                })

        return notifications

    def check_upcoming_payments(self, user_id: int, days_ahead: int = 3) -> List[Dict[str, Any]]:
        notifications = []

        today = datetime.now().date()
        upcoming_date = today + timedelta(days=days_ahead)

        payments = self._payment_repository.find_by_user(user_id, is_active=True)

        for payment in payments:
            days_until = (payment.next_due_date - today).days

            if 0 <= days_until <= days_ahead:
                if days_until == 0:
                    title = f"Сегодня платеж: {payment.name}"
                elif days_until == 1:
                    title = f"Завтра платеж: {payment.name}"
                else:
                    title = f"Через {days_until} дня платеж: {payment.name}"

                notifications.append({
                    'type': 'warning',
                    'title': title,
                    'message': f'Сумма: {payment.amount:.2f} руб.\n'
                               f'Категория: {payment.category}\n'
                               f'Дата платежа: {payment.next_due_date.strftime("%d.%m.%Y")}',
                    'payment': payment
                })

        return notifications

    def get_startup_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        notifications = []

        limits = self._budget_repository.find_all_by_user(user_id)
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        end_date = datetime.now()

        operations = self._operation_repository.find_by_user_and_period(user_id, start_date, end_date)

        for limit in limits:
            current_expenses = sum(op.amount for op in operations
                                   if op.category == limit.category and op.type == OperationType.EXPENSE)

            if current_expenses > limit.monthly_limit:
                notifications.append({
                    'type': 'danger',
                    'title': f'Превышен лимит по категории "{limit.category}"',
                    'message': f'Лимит: {limit.monthly_limit:.2f} руб.\n'
                               f'Потрачено: {current_expenses:.2f} руб.\n'
                               f'Превышение: {current_expenses - limit.monthly_limit:.2f} руб.'
                })
            elif current_expenses == limit.monthly_limit:
                notifications.append({
                    'type': 'danger',
                    'title': f'Лимит по категории "{limit.category}" исчерпан',
                    'message': f'Лимит: {limit.monthly_limit:.2f} руб.\n'
                               f'Потрачено: {current_expenses:.2f} руб. (100%)'
                })
            elif limit.monthly_limit > 0 and (current_expenses / limit.monthly_limit) >= 0.9:
                notifications.append({
                    'type': 'warning',
                    'title': f'Лимит по категории "{limit.category}" почти исчерпан',
                    'message': f'Лимит: {limit.monthly_limit:.2f} руб.\n'
                               f'Потрачено: {current_expenses:.2f} руб. ({(current_expenses / limit.monthly_limit * 100):.0f}%)'
                })

        notifications.extend(self.check_goal_deadlines(user_id))
        notifications.extend(self.check_goal_progress(user_id))
        notifications.extend(self.check_upcoming_payments(user_id, 3))

        return notifications