import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta


class ReportsTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(control_frame, text="Настройки отчета", font=("Arial", 12, "bold")).pack(anchor="w", padx=15,
                                                                                              pady=(5, 2))

        input_frame = ctk.CTkFrame(control_frame)
        input_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(input_frame, text="Тип:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.report_type_var = ctk.StringVar(value="Расходы по категориям")
        report_combo = ctk.CTkComboBox(input_frame, variable=self.report_type_var,
                                       values=["Расходы по категориям", "Динамика доходов и расходов",
                                               "Динамика остатка средств", "Бюджетные лимиты", "Прогресс целей"],
                                       width=200, state="readonly")
        report_combo.grid(row=0, column=1, padx=5, pady=3)

        ctk.CTkLabel(input_frame, text="Период:", font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.period_type_var = ctk.StringVar(value="6 месяцев")
        period_combo = ctk.CTkComboBox(input_frame, variable=self.period_type_var,
                                       values=["1 месяц", "3 месяца", "6 месяцев", "12 месяцев", "Произвольный"],
                                       width=100, state="readonly")
        period_combo.grid(row=0, column=3, padx=5, pady=3)

        self.date_frame = ctk.CTkFrame(input_frame)
        self.date_frame.grid(row=0, column=4, padx=5, pady=3)

        ctk.CTkLabel(self.date_frame, text="с:").pack(side="left", padx=2)
        self.date_from_var = ctk.StringVar()
        self.date_from_entry = ctk.CTkEntry(self.date_frame, textvariable=self.date_from_var, width=90,
                                            state="disabled")
        self.date_from_entry.pack(side="left", padx=2)

        ctk.CTkLabel(self.date_frame, text="по:").pack(side="left", padx=2)
        self.date_to_var = ctk.StringVar()
        self.date_to_entry = ctk.CTkEntry(self.date_frame, textvariable=self.date_to_var, width=90, state="disabled")
        self.date_to_entry.pack(side="left", padx=2)

        def on_period_change(*args):
            if self.period_type_var.get() == "Произвольный":
                self.date_from_entry.configure(state="normal")
                self.date_to_entry.configure(state="normal")
            else:
                self.date_from_entry.configure(state="disabled")
                self.date_to_entry.configure(state="disabled")
                self.date_from_var.set("")
                self.date_to_var.set("")

        self.period_type_var.trace('w', on_period_change)

        ctk.CTkButton(control_frame, text="Сформировать", command=self._generate_report,
                      corner_radius=8, width=100, height=28).pack(pady=5)
        export_frame = ctk.CTkFrame(control_frame)
        export_frame.pack(pady=5)

        ctk.CTkButton(export_frame, text="Экспорт операций в Excel", command=self._export_operations,
                      corner_radius=8, width=180, height=28).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="Экспорт статистики в Excel", command=self._export_stats,
                      corner_radius=8, width=180, height=28).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="PDF (Расходы)", command=self._export_pdf_category,
                      corner_radius=8, width=150, height=28).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="PDF (Динамика)", command=self._export_pdf_trend,
                      corner_radius=8, width=150, height=28).pack(side="left", padx=5)
        ctk.CTkButton(export_frame, text="PDF (Баланс)", command=self._export_pdf_balance,
                      corner_radius=8, width=140, height=28).pack(side="left", padx=5)

        self.chart_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.info_text = ctk.CTkTextbox(main_frame, height=80, corner_radius=10)
        self.info_text.pack(fill="x", padx=10, pady=5)
        self.info_text.configure(state="disabled")

        self._generate_report()

    def _export_operations(self):
        from presentation.gui.export_excel import ExcelExporter
        exporter = ExcelExporter(self.app, self.current_user)
        operations = self.app.operation_service.get_user_operations(self.current_user.id)
        exporter.export_operations(operations)

    def _export_stats(self):
        from presentation.gui.export_excel import ExcelExporter
        exporter = ExcelExporter(self.app, self.current_user)
        date_from, date_to = self._get_date_range()
        if date_from:
            exporter.export_category_stats(date_from, date_to)

    def _export_pdf_category(self):
        from presentation.gui.export_pdf import PDFExporter
        exporter = PDFExporter(self.app, self.current_user)
        date_from, date_to = self._get_date_range()
        if date_from:
            exporter.export_category_report(date_from, date_to)

    def _export_pdf_trend(self):
        from presentation.gui.export_pdf import PDFExporter
        exporter = PDFExporter(self.app, self.current_user)
        date_from, date_to = self._get_date_range()
        if date_from:
            exporter.export_trend_report(date_from, date_to)

    def _export_pdf_balance(self):
        try:
            from presentation.gui.export_pdf import PDFExporter
            exporter = PDFExporter(self.app, self.current_user)
            date_from, date_to = self._get_date_range()
            if date_from:
                exporter.export_balance_report(date_from, date_to)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта PDF: {e}")

    def _get_date_range(self):
        period = self.period_type_var.get()

        if period == "Произвольный":
            if not self.date_from_var.get() or not self.date_to_var.get():
                messagebox.showwarning("Предупреждение", "Выберите даты начала и окончания")
                return None, None

            try:
                date_from = datetime.strptime(self.date_from_var.get(), '%d.%m.%Y')
                date_to = datetime.strptime(self.date_to_var.get(), '%d.%m.%Y')
                return date_from, date_to
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
                return None, None

        date_to = datetime.now().replace(hour=23, minute=59, second=59)

        if period == "1 месяц":
            date_from = date_to - timedelta(days=30)
        elif period == "3 месяца":
            date_from = date_to - timedelta(days=90)
        elif period == "6 месяцев":
            date_from = date_to - timedelta(days=180)
        elif period == "12 месяцев":
            date_from = date_to - timedelta(days=365)
        else:
            date_from = date_to - timedelta(days=180)

        return date_from, date_to

    def _generate_report(self):
        report_type = self.report_type_var.get()
        date_from, date_to = self._get_date_range()

        if date_from is None:
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if report_type == "Расходы по категориям":
            self._show_category_chart(date_from, date_to)
        elif report_type == "Динамика доходов и расходов":
            self._show_trend_chart(date_from, date_to)
        elif report_type == "Динамика остатка средств":
            self._show_balance_chart(date_from, date_to)
        elif report_type == "Бюджетные лимиты":
            self._show_budget_chart()
        elif report_type == "Прогресс целей":
            self._show_goals_chart()

    def _show_category_chart(self, date_from, date_to):
        try:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            expense_data = {}
            for op in operations:
                if op.type.value == "expense" and date_from <= op.operation_date <= date_to:
                    expense_data[op.category] = expense_data.get(op.category, 0) + op.amount

            if not expense_data:
                self._show_empty_message("Нет данных о расходах за выбранный период")
                return

            fig = Figure(figsize=(11, 7))
            ax = fig.add_subplot(111)
            categories = list(expense_data.keys())
            amounts = list(expense_data.values())
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title(
                f'Распределение расходов по категориям\n{date_from.strftime("%d.%m.%Y")} - {date_to.strftime("%d.%m.%Y")}',
                fontsize=12)

            self._draw_chart(fig)
            self._update_info(
                f"Период: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}\nРасходы по категориям. Всего: {sum(amounts):.2f} руб.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_trend_chart(self, date_from, date_to):
        try:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            monthly_data = {}
            for op in operations:
                if date_from <= op.operation_date <= date_to:
                    key = op.operation_date.strftime('%Y-%m')
                    if key not in monthly_data:
                        monthly_data[key] = {'income': 0, 'expense': 0}
                    if op.type.value == "income":
                        monthly_data[key]['income'] += op.amount
                    else:
                        monthly_data[key]['expense'] += op.amount

            if not monthly_data:
                self._show_empty_message("Нет данных за выбранный период")
                return

            months_labels = sorted(monthly_data.keys())
            incomes = [monthly_data[m]['income'] for m in months_labels]
            expenses = [monthly_data[m]['expense'] for m in months_labels]

            fig = Figure(figsize=(13, 7))
            ax = fig.add_subplot(111)

            x_pos = range(len(months_labels))
            ax.bar([x - 0.2 for x in x_pos], incomes, width=0.4, label='Доходы', color='#2ecc71')
            ax.bar([x + 0.2 for x in x_pos], expenses, width=0.4, label='Расходы', color='#e74c3c')
            ax.set_xlabel('Месяцы', fontsize=12)
            ax.set_ylabel('Сумма (руб.)', fontsize=12)
            ax.set_title(
                f'Динамика доходов и расходов\n{date_from.strftime("%d.%m.%Y")} - {date_to.strftime("%d.%m.%Y")}',
                fontsize=12)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(months_labels, rotation=45)
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3)

            self._draw_chart(fig)
            total_income = sum(incomes)
            total_expense = sum(expenses)
            self._update_info(
                f"Период: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}\nДоходы: {total_income:.2f} руб., Расходы: {total_expense:.2f} руб., Баланс: {total_income - total_expense:.2f} руб.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_balance_chart(self, date_from, date_to):
        try:
            initial = self.app.financial_calculator.get_initial_balance(self.current_user.id)

            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            days = (date_to - date_from).days
            if days > 90:
                interval = (days // 30) + 1
            else:
                interval = 1

            current_date = date_from
            balance_data = []
            running_balance = initial

            while current_date <= date_to:
                daily_income = 0
                daily_expense = 0

                for op in operations:
                    if op.operation_date.date() == current_date.date():
                        if op.type.value == "income":
                            daily_income += op.amount
                        else:
                            daily_expense += op.amount

                running_balance += daily_income - daily_expense
                balance_data.append({
                    'date': current_date,
                    'balance': running_balance
                })
                current_date += timedelta(days=1)

            if not balance_data:
                self._show_empty_message("Нет данных за выбранный период")
                return

            step = max(1, len(balance_data) // 15)
            x_pos = range(len(balance_data))
            dates = [d['date'] for d in balance_data]
            balances = [d['balance'] for d in balance_data]

            fig = Figure(figsize=(13, 7))
            ax = fig.add_subplot(111)

            ax.plot(x_pos, balances, marker='o', markersize=3, linewidth=2, color='#2c3e50', label='Баланс')
            ax.fill_between(x_pos, 0, balances, where=[b >= 0 for b in balances], color='#2ecc71', alpha=0.3)
            ax.fill_between(x_pos, 0, balances, where=[b < 0 for b in balances], color='#e74c3c', alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)

            ax.set_xlabel('Дата', fontsize=12)
            ax.set_ylabel('Баланс (руб.)', fontsize=12)
            ax.set_title(f'Динамика остатка средств\n{date_from.strftime("%d.%m.%Y")} - {date_to.strftime("%d.%m.%Y")}',
                         fontsize=12)

            visible_x = x_pos[::step]
            visible_dates = [dates[i].strftime('%d.%m') for i in range(0, len(dates), step)]
            ax.set_xticks(visible_x)
            ax.set_xticklabels(visible_dates, rotation=45, ha='right', fontsize=8)

            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper left', fontsize=10)

            self._draw_chart(fig)

            start_balance = balances[0] if balances else 0
            end_balance = balances[-1] if balances else 0
            change = end_balance - start_balance
            change_percent = (change / abs(start_balance) * 100) if start_balance != 0 else 0
            max_balance = max(balances) if balances else 0
            min_balance = min(balances) if balances else 0

            self._update_info(
                f"Период: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}\nНачальный баланс: {start_balance:.2f} руб., Конечный баланс: {end_balance:.2f} руб., Изменение: {change:+.2f} руб. ({change_percent:+.1f}%)\nМаксимум: {max_balance:.2f} руб., Минимум: {min_balance:.2f} руб.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_budget_chart(self):
        try:
            from application.commands.budget_commands import CheckBudgetStatusCommand
            command = CheckBudgetStatusCommand(user_id=self.current_user.id)
            result = self.app.budget_command_handler.handle_check_status(command)
            budget_data = result['status']

            if not budget_data:
                self._show_empty_message("Нет установленных лимитов бюджета")
                return

            fig = Figure(figsize=(13, 7))
            ax = fig.add_subplot(111)

            categories = list(budget_data.keys())
            limits = [data['limit'] for data in budget_data.values()]
            current = [data['current'] for data in budget_data.values()]

            x_pos = range(len(categories))
            ax.bar([x - 0.2 for x in x_pos], limits, width=0.4, label='Лимит', color='#3498db')
            ax.bar([x + 0.2 for x in x_pos], current, width=0.4, label='Факт', color='#e67e22')

            for i, (limit, curr) in enumerate(zip(limits, current)):
                percent = (curr / limit * 100) if limit > 0 else 0
                color = '#e74c3c' if percent > 100 else '#27ae60'
                ax.text(i, max(limit, curr) + max(limit, curr) * 0.05, f'{percent:.0f}%', ha='center', fontsize=10,
                        color=color, fontweight='bold')

            ax.set_xlabel('Категории', fontsize=12)
            ax.set_ylabel('Сумма (руб.)', fontsize=12)
            ax.set_title('Бюджетные лимиты', fontsize=14)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(categories, rotation=45)
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3)

            self._draw_chart(fig)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_goals_chart(self):
        try:
            goals = self.app.goal_service.get_goals(self.current_user.id)

            if not goals:
                self._show_empty_message("Нет созданных финансовых целей")
                return

            fig = Figure(figsize=(13, 7))
            ax = fig.add_subplot(111)

            names = [goal.name[:15] for goal in goals]
            target = [goal.target_amount for goal in goals]
            current = [goal.current_amount for goal in goals]

            x_pos = range(len(names))
            ax.bar(x_pos, target, width=0.4, label='Цель', color='#3498db', alpha=0.7)
            ax.bar(x_pos, current, width=0.4, label='Накоплено', color='#2ecc71')

            for i, (target_val, current_val) in enumerate(zip(target, current)):
                percent = (current_val / target_val * 100) if target_val > 0 else 0
                ax.text(i, target_val + target_val * 0.05, f'{percent:.0f}%', ha='center', fontsize=10,
                        fontweight='bold')

            ax.set_xlabel('Цели', fontsize=12)
            ax.set_ylabel('Сумма (руб.)', fontsize=12)
            ax.set_title('Прогресс финансовых целей', fontsize=14)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(names, rotation=45)
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3)

            self._draw_chart(fig)
            completed = sum(1 for g in goals if g.progress_percent >= 100)
            self._update_info(f"Всего целей: {len(goals)}, выполнено: {completed}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _draw_chart(self, fig):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig.set_size_inches(13, 7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _show_empty_message(self, message="Нет данных для отображения"):
        label = ctk.CTkLabel(self.chart_frame, text=message, font=("Arial", 16))
        label.pack(expand=True)
        self._update_info(message)

    def _update_info(self, text):
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", text)
        self.info_text.configure(state="disabled")

    def refresh(self):
        self._generate_report()