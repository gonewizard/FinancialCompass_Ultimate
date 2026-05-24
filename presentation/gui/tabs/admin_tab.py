import customtkinter as ctk
from tkinter import messagebox


class AdminTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._store_user_ids = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(stats_frame, text="Системная статистика", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                pady=(10, 5))

        self.stats_text = ctk.CTkTextbox(stats_frame, height=150, corner_radius=8)
        self.stats_text.pack(fill="x", padx=15, pady=10)
        self.stats_text.configure(state="disabled")

        ctk.CTkButton(stats_frame, text="Обновить статистику", command=self._refresh_stats,
                      corner_radius=8, width=150).pack(pady=10)

        users_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        users_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(users_frame, text="Управление пользователями", font=("Arial", 14, "bold")).pack(anchor="w",
                                                                                                     padx=15,
                                                                                                     pady=(10, 5))

        from tkinter import ttk
        columns = ('username', 'role', 'status', 'registered')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=10)

        self.users_tree.heading('username', text='Логин')
        self.users_tree.heading('role', text='Роль')
        self.users_tree.heading('status', text='Статус')
        self.users_tree.heading('registered', text='Зарегистрирован')

        self.users_tree.column('username', width=200)
        self.users_tree.column('role', width=120)
        self.users_tree.column('status', width=100)
        self.users_tree.column('registered', width=150)

        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        self.users_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        button_frame = ctk.CTkFrame(users_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Обновить список", command=self._refresh_users,
                      width=120, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Деактивировать", command=self._deactivate_user,
                      width=120, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Активировать", command=self._activate_user,
                      width=120, corner_radius=8).pack(side="left", padx=5)

        self._refresh_stats()
        self._refresh_users()

    def _refresh_stats(self):
        try:
            from application.commands.admin_commands import GetSystemStatsCommand
            command = GetSystemStatsCommand(admin_user_id=self.current_user.id)
            stats = self.app.admin_command_handler.handle_get_system_stats(command)

            stats_text = f"Общая статистика системы:\n\n"
            stats_text += f"Пользователей: {stats['total_users']}\n"
            stats_text += f"Операций: {stats['total_operations']}\n"
            stats_text += f"Доходы: {stats['total_income']:.2f} руб.\n"
            stats_text += f"Расходы: {stats['total_expenses']:.2f} руб.\n"
            stats_text += f"Баланс: {stats['system_balance']:.2f} руб.\n"
            stats_text += f"Активных пользователей: {stats['active_users']}\n\n"
            stats_text += f"Активность за 30 дней:\n"
            stats_text += f"Операций: {stats['recent_activity']['recent_operations_count']}\n"
            stats_text += f"Доходы: {stats['recent_activity']['recent_income']:.2f} руб.\n"
            stats_text += f"Расходы: {stats['recent_activity']['recent_expenses']:.2f} руб.\n"
            stats_text += f"Баланс: {stats['recent_activity']['recent_balance']:.2f} руб."

            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text)
            self.stats_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh_users(self):
        try:
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)

            self._store_user_ids.clear()
            users = self.app.admin_service.get_all_users()

            for user in users:
                role_text = "Администратор" if user.has_admin_privileges() else "Пользователь"
                status_text = "Активен" if user.is_active else "Неактивен"

                item = self.users_tree.insert('', 'end', values=(
                    user.username,
                    role_text,
                    status_text,
                    user.created_at.strftime('%d.%m.%Y')
                ))
                self._store_user_ids[item] = user.id
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")

    def _deactivate_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя")
            return

        item = selected[0]
        user_id = self._store_user_ids.get(item)
        username = self.users_tree.item(item)['values'][0]

        if not user_id:
            messagebox.showerror("Ошибка", "Не удалось определить пользователя")
            return

        if user_id == self.current_user.id:
            messagebox.showerror("Ошибка", "Нельзя деактивировать самого себя")
            return

        if messagebox.askyesno("Подтверждение", f"Деактивировать пользователя '{username}'?"):
            try:
                from application.commands.admin_commands import DeactivateUserCommand
                command = DeactivateUserCommand(target_user_id=user_id, admin_user_id=self.current_user.id)

                if self.app.admin_command_handler.handle_deactivate_user(command):
                    messagebox.showinfo("Успех", "Пользователь деактивирован")
                    self._refresh_users()
                else:
                    messagebox.showerror("Ошибка", "Не удалось деактивировать пользователя")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def _activate_user(self):
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя")
            return

        item = selected[0]
        user_id = self._store_user_ids.get(item)
        username = self.users_tree.item(item)['values'][0]

        if not user_id:
            messagebox.showerror("Ошибка", "Не удалось определить пользователя")
            return

        if messagebox.askyesno("Подтверждение", f"Активировать пользователя '{username}'?"):
            try:
                from application.commands.admin_commands import ActivateUserCommand
                command = ActivateUserCommand(target_user_id=user_id, admin_user_id=self.current_user.id)

                if self.app.admin_command_handler.handle_activate_user(command):
                    messagebox.showinfo("Успех", "Пользователь активирован")
                    self._refresh_users()
                else:
                    messagebox.showerror("Ошибка", "Не удалось активировать пользователя")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def refresh(self):
        self._refresh_stats()
        self._refresh_users()