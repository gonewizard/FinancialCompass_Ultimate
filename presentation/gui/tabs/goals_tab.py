import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from presentation.gui.dialogs import AddToGoalDialog


class GoalsTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self.goal_ids = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_add_section(main_frame)
        self._setup_goals_list(main_frame)

    def _setup_add_section(self, parent):
        add_frame = ctk.CTkFrame(parent, corner_radius=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(add_frame, text="Добавить новую цель", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                             pady=(10, 5))

        input_frame = ctk.CTkFrame(add_frame)
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.goal_name_entry = ctk.CTkEntry(input_frame, width=200)
        self.goal_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Целевая сумма (₽):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.goal_target_entry = ctk.CTkEntry(input_frame, width=120)
        self.goal_target_entry.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Срок (ДД.ММ.ГГГГ):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.goal_deadline_entry = ctk.CTkEntry(input_frame, width=120)
        self.goal_deadline_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Описание:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.goal_description_entry = ctk.CTkEntry(input_frame, width=200)
        self.goal_description_entry.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkButton(add_frame, text="Создать цель", command=self._add_goal,
                      corner_radius=10, width=150).pack(pady=10)

    def _setup_goals_list(self, parent):
        list_frame = ctk.CTkFrame(parent, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(list_frame, text="Мои цели", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        from tkinter import ttk
        columns = ('name', 'target', 'current', 'progress', 'deadline', 'status')
        self.goals_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        self.goals_tree.heading('name', text='Название')
        self.goals_tree.heading('target', text='Цель (₽)')
        self.goals_tree.heading('current', text='Накоплено (₽)')
        self.goals_tree.heading('progress', text='Прогресс')
        self.goals_tree.heading('deadline', text='Срок')
        self.goals_tree.heading('status', text='Статус')

        self.goals_tree.column('name', width=200)
        self.goals_tree.column('target', width=120, anchor='e')
        self.goals_tree.column('current', width=120, anchor='e')
        self.goals_tree.column('progress', width=100, anchor='center')
        self.goals_tree.column('deadline', width=100, anchor='center')
        self.goals_tree.column('status', width=80, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=scrollbar.set)

        self.goals_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        button_frame = ctk.CTkFrame(list_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Пополнить цель", command=self._add_to_goal, width=120, corner_radius=8).pack(
            side="left", padx=5)
        ctk.CTkButton(button_frame, text="Удалить цель", command=self._delete_goal, width=120, corner_radius=8).pack(
            side="left", padx=5)
        ctk.CTkButton(button_frame, text="Обновить", command=self.refresh, width=120, corner_radius=8).pack(side="left",
                                                                                                            padx=5)

        self.refresh()

    def _add_goal(self):
        try:
            name = self.goal_name_entry.get()
            target = float(self.goal_target_entry.get())
            deadline_str = self.goal_deadline_entry.get()
            description = self.goal_description_entry.get() or None

            if not name:
                messagebox.showerror("Ошибка", "Введите название цели")
                return
            if target <= 0:
                messagebox.showerror("Ошибка", "Целевая сумма должна быть положительной")
                return

            deadline = None
            if deadline_str:
                deadline = datetime.strptime(deadline_str, '%d.%m.%Y')

            self.app.goal_service.create_goal(
                user_id=self.current_user.id,
                name=name,
                target_amount=target,
                deadline=deadline,
                description=description
            )
            messagebox.showinfo("Успех", f"Цель '{name}' создана!")

            self.goal_name_entry.delete(0, 'end')
            self.goal_target_entry.delete(0, 'end')
            self.goal_deadline_entry.delete(0, 'end')
            self.goal_description_entry.delete(0, 'end')
            self.refresh()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат суммы")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _add_to_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите цель")
            return

        item = selected[0]
        goal_id = self.goal_ids.get(item)
        goal_name = self.goals_tree.item(item)['values'][0]

        if not goal_id:
            messagebox.showerror("Ошибка", "Не удалось определить цель")
            return

        AddToGoalDialog.show(self.parent, goal_name, goal_id, self._perform_add)

    def _perform_add(self, goal_id, amount, goal_name):
        try:
            self.app.goal_service.add_to_goal(goal_id, amount)
            messagebox.showinfo("Успех", f"Добавлено {amount:.2f}₽ к цели '{goal_name}'")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_goal(self):
        selected = self.goals_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите цель")
            return

        item = selected[0]
        goal_id = self.goal_ids.get(item)
        goal_name = self.goals_tree.item(item)['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить цель '{goal_name}'?"):
            self.app.goal_service.delete_goal(goal_id)
            messagebox.showinfo("Успех", "Цель удалена")
            self.refresh()

    def refresh(self):
        try:
            for item in self.goals_tree.get_children():
                self.goals_tree.delete(item)

            self.goal_ids.clear()
            goals = self.app.goal_service.get_goals(self.current_user.id)

            for goal in goals:
                progress = f"{goal.progress_percent:.1f}%"
                status_text = "Выполнена" if goal.status.value == "completed" else "Активна"

                if goal.deadline:
                    deadline_str = goal.deadline.strftime('%d.%m.%Y')
                else:
                    deadline_str = "-"

                item = self.goals_tree.insert('', 'end', values=(
                    goal.name,
                    f"{goal.target_amount:.2f}",
                    f"{goal.current_amount:.2f}",
                    progress,
                    deadline_str,
                    status_text
                ))
                self.goal_ids[item] = goal.id

            self._refresh_operations_goal_list()

            if self.update_balance_callback:
                self.update_balance_callback()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить цели: {e}")

    def _refresh_operations_goal_list(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_tabs'):
                if 'operations' in self.parent.master._tabs:
                    self.parent.master._tabs['operations']._refresh_goals_list()
        except:
            pass