import customtkinter as ctk
from tkinter import messagebox


class BudgetTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        limit_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        limit_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(limit_frame, text="Установить лимит", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                            pady=(10, 5))

        input_frame = ctk.CTkFrame(limit_frame)
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.limit_category = ctk.CTkEntry(input_frame, width=150)
        self.limit_category.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Лимит в месяц (руб.):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.limit_amount = ctk.CTkEntry(input_frame, width=120)
        self.limit_amount.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(limit_frame, text="Установить лимит", command=self._set_limit,
                      corner_radius=10, width=150).pack(pady=10)

        status_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(status_frame, text="Статус лимитов", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                           pady=(10, 5))

        from tkinter import ttk
        columns = ('category', 'limit', 'current', 'percentage', 'status')
        self.limits_tree = ttk.Treeview(status_frame, columns=columns, show='headings', height=10)

        self.limits_tree.heading('category', text='Категория')
        self.limits_tree.heading('limit', text='Лимит (руб.)')
        self.limits_tree.heading('current', text='Расходы (руб.)')
        self.limits_tree.heading('percentage', text='Использовано %')
        self.limits_tree.heading('status', text='Статус')

        self.limits_tree.column('category', width=150)
        self.limits_tree.column('limit', width=100)
        self.limits_tree.column('current', width=120)
        self.limits_tree.column('percentage', width=100)
        self.limits_tree.column('status', width=100)

        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.limits_tree.yview)
        self.limits_tree.configure(yscrollcommand=scrollbar.set)

        self.limits_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        button_frame = ctk.CTkFrame(status_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Обновить", command=self.refresh, width=120, corner_radius=8).pack(side="left",
                                                                                                            padx=5)
        ctk.CTkButton(button_frame, text="Удалить лимит", command=self._delete_limit, width=120, corner_radius=8).pack(
            side="left", padx=5)

        self.refresh()

    def _set_limit(self):
        try:
            category = self.limit_category.get()
            monthly_limit = float(self.limit_amount.get())

            if not category:
                messagebox.showerror("Ошибка", "Введите категорию")
                return

            from application.commands.budget_commands import SetBudgetLimitCommand
            command = SetBudgetLimitCommand(user_id=self.current_user.id, category=category,
                                            monthly_limit=monthly_limit)
            self.app.budget_command_handler.handle_set_limit(command)

            messagebox.showinfo("Успех", f"Лимит для '{category}' установлен: {monthly_limit} руб./мес.")
            self.limit_category.delete(0, 'end')
            self.limit_amount.delete(0, 'end')
            self.refresh()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат суммы")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_limit(self):
        selected = self.limits_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите лимит")
            return

        category = self.limits_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить лимит для категории '{category}'?"):
            try:
                from application.commands.budget_commands import DeleteBudgetLimitCommand
                command = DeleteBudgetLimitCommand(user_id=self.current_user.id, category=category)
                self.app.budget_command_handler.handle_delete_limit(command)
                messagebox.showinfo("Успех", "Лимит удалён")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def refresh(self):
        try:
            for item in self.limits_tree.get_children():
                self.limits_tree.delete(item)

            from application.commands.budget_commands import CheckBudgetStatusCommand
            command = CheckBudgetStatusCommand(user_id=self.current_user.id)
            result = self.app.budget_command_handler.handle_check_status(command)

            for category, data in result['status'].items():
                if data['exceeded']:
                    status_text = "Превышен"
                elif data['percentage'] >= 90:
                    status_text = "Почти исчерпан"
                else:
                    status_text = "Норма"

                self.limits_tree.insert('', 'end', values=(
                    category,
                    f"{data['limit']:.2f}",
                    f"{data['current']:.2f}",
                    f"{data['percentage']}%",
                    status_text
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить лимиты: {e}")