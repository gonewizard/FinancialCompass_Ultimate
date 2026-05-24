import customtkinter as ctk
from datetime import datetime, timedelta
from core.entities.operation import OperationType


class DashboardTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self._create_widgets()
        self.refresh()
        self._start_auto_refresh()

    def _start_auto_refresh(self):
        self.refresh()
        self.after_id = self.parent.after(5000, self._start_auto_refresh)

    def _create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_balance_card(main_frame)
        self._setup_stats_cards(main_frame)
        self._setup_goals_preview(main_frame)
        self._setup_payments_preview(main_frame)
        self._setup_recent_operations(main_frame)

    def _setup_balance_card(self, parent):
        self.balance_card = ctk.CTkFrame(parent, corner_radius=15, height=120)
        self.balance_card.pack(fill="x", padx=20, pady=10)

        self.balance_label = ctk.CTkLabel(self.balance_card, text="", font=("Arial", 28, "bold"), text_color="white")
        self.balance_label.pack(expand=True)

        ctk.CTkLabel(self.balance_card, text="Текущий баланс", font=("Arial", 14), text_color="white").pack()

        self._update_balance_card_color()

    def _setup_stats_cards(self, parent):
        stats_frame = ctk.CTkFrame(parent, corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.income_label = ctk.CTkLabel(stats_frame, text="", font=("Arial", 14, "bold"), text_color="#2ecc71")
        self.income_label.pack(anchor="w", padx=15, pady=5)

        self.expense_label = ctk.CTkLabel(stats_frame, text="", font=("Arial", 14, "bold"), text_color="#e74c3c")
        self.expense_label.pack(anchor="w", padx=15, pady=5)

        self.balance_month_label = ctk.CTkLabel(stats_frame, text="", font=("Arial", 14, "bold"))
        self.balance_month_label.pack(anchor="w", padx=15, pady=5)

    def _setup_goals_preview(self, parent):
        goals_frame = ctk.CTkFrame(parent, corner_radius=10)
        goals_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(goals_frame, text="🎯 Ближайшие цели", font=("Arial", 16, "bold")).pack(anchor="w", padx=15,
                                                                                            pady=(10, 5))

        self.goals_preview_frame = ctk.CTkFrame(goals_frame, corner_radius=8)
        self.goals_preview_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(goals_frame, text="Перейти к целям", command=self._open_goals_tab,
                      corner_radius=8, width=120, height=30).pack(pady=10)

    def _setup_payments_preview(self, parent):
        payments_frame = ctk.CTkFrame(parent, corner_radius=10)
        payments_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(payments_frame, text="⏰ Ближайшие платежи", font=("Arial", 16, "bold")).pack(anchor="w", padx=15,
                                                                                                  pady=(10, 5))

        self.payments_preview_frame = ctk.CTkFrame(payments_frame, corner_radius=8)
        self.payments_preview_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(payments_frame, text="Перейти к платежам", command=self._open_payments_tab,
                      corner_radius=8, width=120, height=30).pack(pady=10)

    def _setup_recent_operations(self, parent):
        recent_frame = ctk.CTkFrame(parent, corner_radius=10)
        recent_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(recent_frame, text="📊 Последние операции", font=("Arial", 16, "bold")).pack(anchor="w", padx=15,
                                                                                                 pady=(10, 5))

        from tkinter import ttk
        columns = ('date', 'type', 'category', 'amount')
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=8)

        self.recent_tree.heading('date', text='Дата')
        self.recent_tree.heading('type', text='Тип')
        self.recent_tree.heading('category', text='Категория')
        self.recent_tree.heading('amount', text='Сумма')

        self.recent_tree.column('date', width=100)
        self.recent_tree.column('type', width=80)
        self.recent_tree.column('category', width=150)
        self.recent_tree.column('amount', width=100)

        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scrollbar.set)

        self.recent_tree.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=10)

    def refresh(self):
        try:
            balance = self.app.financial_calculator.get_balance_with_initial(self.current_user.id)
            self.balance_label.configure(text=f"{balance:,.2f} ₽")

            today = datetime.now().date()
            first_day = today.replace(day=1)

            operations = self.app.operation_service.get_operations_for_period(self.current_user.id, 30)

            income_month = 0
            expense_month = 0

            for op in operations:
                op_date = op.operation_date.date() if hasattr(op.operation_date, 'date') else op.operation_date
                if op_date >= first_day:
                    if op.type == OperationType.INCOME:
                        income_month += op.amount
                    else:
                        expense_month += op.amount

            self.income_label.configure(text=f"Доходы за месяц: {income_month:,.0f} ₽")
            self.expense_label.configure(text=f"Расходы за месяц: {expense_month:,.0f} ₽")

            balance_month = income_month - expense_month
            color = "#2ecc71" if balance_month >= 0 else "#e74c3c"
            self.balance_month_label.configure(text=f"Баланс за месяц: {balance_month:+,.0f} ₽", text_color=color)

            for widget in self.goals_preview_frame.winfo_children():
                widget.destroy()

            goals = self.app.goal_service.get_goals(self.current_user.id)
            active_goals = [g for g in goals if g.status.value != "completed"]

            if active_goals:
                for goal in active_goals[:3]:
                    percent = goal.progress_percent
                    frame = ctk.CTkFrame(self.goals_preview_frame, corner_radius=8)
                    frame.pack(fill="x", pady=3)

                    ctk.CTkLabel(frame, text=goal.name, font=("Arial", 12, "bold")).pack(anchor="w", padx=10,
                                                                                         pady=(5, 0))
                    ctk.CTkLabel(frame,
                                 text=f"{goal.current_amount:,.0f} / {goal.target_amount:,.0f} ₽ ({percent:.0f}%)",
                                 font=("Arial", 10)).pack(anchor="w", padx=10)

                    progress = ctk.CTkProgressBar(frame, width=300, height=10, corner_radius=5)
                    progress.pack(pady=5, padx=10)
                    progress.set(percent / 100)
            else:
                ctk.CTkLabel(self.goals_preview_frame, text="Нет активных целей", font=("Arial", 12)).pack(pady=10)

            for widget in self.payments_preview_frame.winfo_children():
                widget.destroy()

            payments = self.app.payment_service.get_payments(self.current_user.id, is_active=True)
            upcoming = []
            for payment in payments:
                days_until = (payment.next_due_date - datetime.now().date()).days
                if 0 <= days_until <= 7:
                    upcoming.append((payment, days_until))

            upcoming.sort(key=lambda x: x[1])

            if upcoming:
                for payment, days_until in upcoming[:3]:
                    frame = ctk.CTkFrame(self.payments_preview_frame, corner_radius=8)
                    frame.pack(fill="x", pady=3)

                    if days_until == 0:
                        when = "сегодня"
                    elif days_until == 1:
                        when = "завтра"
                    else:
                        when = f"через {days_until} дней"

                    ctk.CTkLabel(frame, text=f"{payment.name} - {payment.amount:,.0f} ₽", font=("Arial", 12)).pack(
                        anchor="w", padx=10, pady=(5, 0))
                    ctk.CTkLabel(frame, text=when, font=("Arial", 10), text_color="#e67e22").pack(anchor="w", padx=10,
                                                                                                  pady=(0, 5))
            else:
                ctk.CTkLabel(self.payments_preview_frame, text="Нет ближайших платежей", font=("Arial", 12)).pack(
                    pady=10)

            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)

            recent_ops = sorted(operations, key=lambda x: x.operation_date, reverse=True)[:10]
            for op in recent_ops:
                type_text = "Доход" if op.type == OperationType.INCOME else "Расход"
                type_icon = "📈" if op.type == OperationType.INCOME else "📉"
                self.recent_tree.insert('', 'end', values=(
                    op.operation_date.strftime('%d.%m.%Y'),
                    f"{type_icon} {type_text}",
                    op.category,
                    f"{op.amount:,.0f} ₽"
                ))

            if self.update_balance_callback:
                self.update_balance_callback()

        except Exception as e:
            print(f"Ошибка обновления дашборда: {e}")

    def _open_goals_tab(self):
        try:
            parent_widget = self.parent
            while parent_widget:
                if hasattr(parent_widget, 'set') and hasattr(parent_widget, '_tab_dict'):
                    for tab_name in parent_widget._tab_dict.keys():
                        if "Цели" in tab_name or "🎯" in tab_name:
                            parent_widget.set(tab_name)
                            return
                parent_widget = parent_widget.master if hasattr(parent_widget, 'master') else None
        except Exception as e:
            print(f"Ошибка: {e}")

    def _open_payments_tab(self):
        try:
            parent_widget = self.parent
            while parent_widget:
                if hasattr(parent_widget, 'set') and hasattr(parent_widget, '_tab_dict'):
                    for tab_name in parent_widget._tab_dict.keys():
                        if "Платежи" in tab_name or "⏰" in tab_name:
                            parent_widget.set(tab_name)
                            return
                parent_widget = parent_widget.master if hasattr(parent_widget, 'master') else None
        except Exception as e:
            print(f"Ошибка: {e}")

    def _update_balance_card_color(self):
        color_theme = self.app.user_service.get_color_theme(self.current_user.id)
        colors = {
            "green": "#2ecc71",
            "blue": "#3498db",
            "dark-blue": "#2980b9",
        }
        color = colors.get(color_theme, "#2ecc71")
        self.balance_card.configure(fg_color=color)