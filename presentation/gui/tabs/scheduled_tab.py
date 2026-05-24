import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from core.entities.operation import OperationType
from core.entities.scheduled_payment import PaymentFrequency


class ScheduledTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self.payment_ids = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        add_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(add_frame, text="Добавить плановый платеж", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                  pady=(10, 5))

        input_frame = ctk.CTkFrame(add_frame)
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.payment_name_entry = ctk.CTkEntry(input_frame, width=150)
        self.payment_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Сумма (₽):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.payment_amount_entry = ctk.CTkEntry(input_frame, width=100)
        self.payment_amount_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Категория:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.payment_category_entry = ctk.CTkEntry(input_frame, width=120)
        self.payment_category_entry.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Периодичность:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.payment_frequency_var = ctk.StringVar(value="Ежемесячно")
        freq_combo = ctk.CTkComboBox(input_frame, variable=self.payment_frequency_var,
                                     values=["Ежедневно", "Еженедельно", "Ежемесячно", "Ежегодно"],
                                     width=120, state="readonly")
        freq_combo.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Дата начала:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.payment_start_entry = ctk.CTkEntry(input_frame, width=100)
        self.payment_start_entry.grid(row=1, column=3, padx=5, pady=5)
        self.payment_start_entry.insert(0, datetime.now().strftime('%d.%m.%Y'))

        ctk.CTkLabel(input_frame, text="Описание:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.payment_description_entry = ctk.CTkEntry(input_frame, width=200)
        self.payment_description_entry.grid(row=1, column=5, padx=5, pady=5)

        ctk.CTkButton(add_frame, text="Добавить платеж", command=self._add_payment,
                      corner_radius=10, width=150).pack(pady=10)

        list_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(list_frame, text="Мои плановые платежи", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                               pady=(10, 5))

        from tkinter import ttk
        columns = ('name', 'amount', 'category', 'frequency', 'next_due', 'status')
        self.payments_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        self.payments_tree.heading('name', text='Название')
        self.payments_tree.heading('amount', text='Сумма (₽)')
        self.payments_tree.heading('category', text='Категория')
        self.payments_tree.heading('frequency', text='Периодичность')
        self.payments_tree.heading('next_due', text='Следующий платеж')
        self.payments_tree.heading('status', text='Статус')

        self.payments_tree.column('name', width=180)
        self.payments_tree.column('amount', width=100, anchor='e')
        self.payments_tree.column('category', width=120)
        self.payments_tree.column('frequency', width=100, anchor='center')
        self.payments_tree.column('next_due', width=110, anchor='center')
        self.payments_tree.column('status', width=80, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.payments_tree.yview)
        self.payments_tree.configure(yscrollcommand=scrollbar.set)

        self.payments_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        button_frame = ctk.CTkFrame(list_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Отметить оплаченным", command=self._mark_paid,
                      width=140, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Вкл/Выкл", command=self._toggle_payment,
                      width=100, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Удалить", command=self._delete_payment,
                      width=100, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Обновить", command=self.refresh,
                      width=100, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Excel", command=self._export_to_excel, width=100, corner_radius=8).pack(
            side="left", padx=5)

        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(info_frame, text="Информация", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        self.info_text = ctk.CTkTextbox(info_frame, height=80, corner_radius=8)
        self.info_text.pack(fill="x", padx=15, pady=10)
        self.info_text.configure(state="disabled")

        self.refresh()

    def _export_to_excel(self):
        from presentation.gui.export_excel import ExcelExporter
        exporter = ExcelExporter(self.app, self.current_user)
        exporter.export_payments()

    def _calculate_next_due_date(self, start_date, frequency):
        today = datetime.now().date()
        next_date = start_date

        if frequency == "daily":
            while next_date <= today:
                next_date += timedelta(days=1)
        elif frequency == "weekly":
            while next_date <= today:
                next_date += timedelta(days=7)
        elif frequency == "monthly":
            while next_date <= today:
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
        elif frequency == "yearly":
            while next_date <= today:
                next_date = next_date.replace(year=next_date.year + 1)

        return next_date

    def _create_missed_payments(self, payment_id, start_date, frequency, today):
        if start_date >= today:
            return 0

        payment = None
        payments = self.app.payment_service.get_payments(self.current_user.id)
        for p in payments:
            if p.id == payment_id:
                payment = p
                break

        if not payment:
            return 0

        dates = []
        current = start_date

        if frequency == "daily":
            while current <= today:
                dates.append(current)
                current += timedelta(days=1)
        elif frequency == "weekly":
            while current <= today:
                dates.append(current)
                current += timedelta(days=7)
        elif frequency == "monthly":
            while current <= today:
                dates.append(current)
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    current = current.replace(month=current.month + 1)
        elif frequency == "yearly":
            while current <= today:
                dates.append(current)
                current = current.replace(year=current.year + 1)

        added_count = 0
        for due_date in dates:
            try:
                self.app.operation_service.create_operation(
                    user_id=self.current_user.id,
                    operation_type=OperationType.EXPENSE,
                    amount=payment.amount,
                    category=payment.category,
                    description=f"Плановый платеж: {payment.name}",
                    counterparty=payment.name
                )
                added_count += 1
            except Exception as e:
                print(f"Ошибка при добавлении пропущенного платежа: {e}")

        return added_count

    def _add_payment(self):
        try:
            name = self.payment_name_entry.get()
            amount = float(self.payment_amount_entry.get())
            category = self.payment_category_entry.get()
            frequency_str = self.payment_frequency_var.get()
            start_str = self.payment_start_entry.get()
            description = self.payment_description_entry.get() or None

            if not name:
                messagebox.showerror("Ошибка", "Введите название")
                return
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                return
            if not category:
                messagebox.showerror("Ошибка", "Введите категорию")
                return

            start_date = datetime.strptime(start_str, '%d.%m.%Y').date()

            freq_map = {"Ежедневно": "daily", "Еженедельно": "weekly",
                        "Ежемесячно": "monthly", "Ежегодно": "yearly"}
            frequency = freq_map.get(frequency_str, "monthly")

            freq_enum_map = {"daily": PaymentFrequency.DAILY, "weekly": PaymentFrequency.WEEKLY,
                             "monthly": PaymentFrequency.MONTHLY, "yearly": PaymentFrequency.YEARLY}
            payment_freq = freq_enum_map.get(frequency, PaymentFrequency.MONTHLY)

            today = datetime.now().date()
            next_due_date = self._calculate_next_due_date(start_date, frequency)

            payment = self.app.payment_service.create_payment(
                user_id=self.current_user.id,
                name=name,
                amount=amount,
                category=category,
                frequency=payment_freq,
                start_date=start_date,
                description=description
            )

            self.app.payment_service.update_next_due_date(payment.id, next_due_date)

            added_count = self._create_missed_payments(payment.id, start_date, frequency, today)

            if added_count > 0:
                messagebox.showinfo("Плановые платежи",
                                    f"Платеж '{name}' добавлен.\nАвтоматически добавлено {added_count} операций в расходы")
            else:
                messagebox.showinfo("Успех", f"Платеж '{name}' добавлен")

            self.payment_name_entry.delete(0, 'end')
            self.payment_amount_entry.delete(0, 'end')
            self.payment_category_entry.delete(0, 'end')
            self.payment_description_entry.delete(0, 'end')
            self.payment_start_entry.delete(0, 'end')
            self.payment_start_entry.insert(0, datetime.now().strftime('%d.%m.%Y'))
            self.refresh()
            self._refresh_operations()
            self._refresh_budget()
            self._refresh_balance()

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат суммы или даты")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _mark_paid(self):
        selected = self.payments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите платеж")
            return

        item = selected[0]
        payment_id = self.payment_ids.get(item)

        if not payment_id:
            messagebox.showerror("Ошибка", "Не удалось определить платеж")
            return

        if not messagebox.askyesno("Подтверждение", "Отметить платеж как оплаченный?"):
            return

        try:
            payment = None
            payments = self.app.payment_service.get_payments(self.current_user.id)
            for p in payments:
                if p.id == payment_id:
                    payment = p
                    break

            if payment:
                self.app.operation_service.create_operation(
                    user_id=self.current_user.id,
                    operation_type=OperationType.EXPENSE,
                    amount=payment.amount,
                    category=payment.category,
                    description=f"Плановый платеж: {payment.name}",
                    counterparty=payment.name
                )
                self.app.payment_service.mark_as_paid(payment_id)
                messagebox.showinfo("Успех", "Платеж отмечен как оплаченный")
                self.refresh()
                self._refresh_operations()
                self._refresh_budget()
                self._refresh_balance()
            else:
                messagebox.showerror("Ошибка", "Платеж не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _toggle_payment(self):
        selected = self.payments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите платеж")
            return

        item = selected[0]
        payment_id = self.payment_ids.get(item)

        if not payment_id:
            messagebox.showerror("Ошибка", "Не удалось определить платеж")
            return

        try:
            self.app.payment_service.toggle_active(payment_id)
            messagebox.showinfo("Успех", "Статус платежа изменен")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_payment(self):
        selected = self.payments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите платежи для удаления")
            return

        if not messagebox.askyesno("Подтверждение", f"Удалить {len(selected)} платежей и все связанные расходы?"):
            return

        deleted_count = 0
        for item in selected:
            payment_id = self.payment_ids.get(item)
            payment_name = self.payments_tree.item(item)['values'][0]
            if not payment_id:
                continue

            try:
                operations = self.app.operation_service.get_user_operations(self.current_user.id)
                for op in operations:
                    if op.description and f"Плановый платеж: {payment_name}" in op.description:
                        self.app.operation_service.delete_operation(op.id, self.current_user.id)

                self.app.payment_service.delete_payment(payment_id)
                deleted_count += 1
            except Exception as e:
                print(f"Ошибка при удалении платежа: {e}")

        if deleted_count > 0:
            messagebox.showinfo("Успех", f"Удалено {deleted_count} платежей")
            self.refresh()
            self._refresh_operations()
            self._refresh_budget()
            self._refresh_balance()

    def refresh(self):
        try:
            self._process_due_payments()

            for item in self.payments_tree.get_children():
                self.payments_tree.delete(item)

            self.payment_ids.clear()
            payments = self.app.payment_service.get_payments(self.current_user.id)

            freq_display = {"daily": "Ежедневно", "weekly": "Еженедельно",
                            "monthly": "Ежемесячно", "yearly": "Ежегодно"}

            for payment in payments:
                status_text = "Активен" if payment.is_active else "Неактивен"
                freq_text = freq_display.get(payment.frequency.value, payment.frequency.value)

                item = self.payments_tree.insert('', 'end', values=(
                    payment.name,
                    f"{payment.amount:.2f}",
                    payment.category,
                    freq_text,
                    payment.next_due_date.strftime('%d.%m.%Y'),
                    status_text
                ))
                self.payment_ids[item] = payment.id

            monthly_total = self.app.payment_service.get_monthly_total(self.current_user.id)
            due_payments = self.app.payment_service.get_due_payments(self.current_user.id)

            info_text = f"Сумма плановых платежей за месяц: {monthly_total:.2f} ₽\n"
            info_text += f"Платежей к оплате сегодня: {len(due_payments)}"

            self.info_text.configure(state="normal")
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", info_text)
            self.info_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить платежи: {e}")

    def _process_due_payments(self):
        try:
            due_payments = self.app.payment_service.get_due_payments(self.current_user.id)
            added_count = 0

            for payment in due_payments:
                self.app.operation_service.create_operation(
                    user_id=self.current_user.id,
                    operation_type=OperationType.EXPENSE,
                    amount=payment.amount,
                    category=payment.category,
                    description=f"Плановый платеж: {payment.name}",
                    counterparty=payment.name
                )
                self.app.payment_service.mark_as_paid(payment.id)
                added_count += 1

            if added_count > 0:
                messagebox.showinfo("Плановые платежи", f"Автоматически добавлено {added_count} платежей в расходы")
                self._refresh_operations()
                self._refresh_budget()
                self._refresh_balance()
        except Exception as e:
            print(f"Ошибка при обработке платежей: {e}")

    def _refresh_operations(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_tabs'):
                if 'operations' in self.parent.master._tabs:
                    self.parent.master._tabs['operations'].refresh()
        except:
            pass

    def _refresh_budget(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_tabs'):
                if 'budget' in self.parent.master._tabs:
                    self.parent.master._tabs['budget'].refresh()
        except:
            pass

    def _refresh_balance(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_update_balance_display'):
                self.parent.master._update_balance_display()
        except:
            pass