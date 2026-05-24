import customtkinter as ctk
from tkinter import messagebox
from presentation.gui.theme_manager import ThemeManager
from presentation.gui.dialogs import InitialBalanceDialog
from presentation.gui.tabs import (
    OperationsTab, ReportsTab, BudgetTab, CalendarTab,
    CounterpartyTab, GoalsTab, ScheduledTab,
    SearchTab, ForecastTab, BackupTab, SettingsTab, AdminTab, DashboardTab
)
from core.entities.operation import OperationType


class FinancialCompassGUI:
    def __init__(self, app):
        self.app = app
        self.current_user = None
        self.theme_manager = ThemeManager()

        self.root = ctk.CTk()
        self.root.title("Финансовый компас")
        self.root.geometry("1400x900")

        self._tabs = {}
        self.show_login_screen()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        self.current_user = None

        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(main_frame, text="Финансовый компас",
                     font=("Arial", 28, "bold")).pack(pady=30)

        login_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        login_frame.pack(pady=20)

        ctk.CTkLabel(login_frame, text="Логин:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.login_username = ctk.CTkEntry(login_frame, width=250, font=("Arial", 14))
        self.login_username.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(login_frame, text="Пароль:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10,
                                                                           sticky="w")
        self.login_password = ctk.CTkEntry(login_frame, width=250, font=("Arial", 14), show="*")
        self.login_password.grid(row=1, column=1, padx=10, pady=10)

        button_frame = ctk.CTkFrame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ctk.CTkButton(button_frame, text="Войти", command=self._handle_login,
                      width=120, corner_radius=10).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Регистрация", command=self._show_registration_screen,
                      width=120, corner_radius=10).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Создать админа", command=self._show_create_admin_screen,
                      width=140, corner_radius=10).pack(side="left", padx=10)

        theme_button = ctk.CTkButton(main_frame, text="🌓 Сменить тему", command=self._toggle_theme,
                                     width=150, corner_radius=10)
        theme_button.pack(pady=20)

        self.login_password.bind('<Return>', lambda e: self._handle_login())

    def _toggle_theme(self):
        new_theme = self.theme_manager.toggle_theme()
        self.app.user_service.update_theme(self.current_user.id, new_theme)
        self._refresh_current_dashboard()


    def _refresh_current_dashboard(self):
        if self.current_user:
            if self.current_user.has_admin_privileges():
                self._show_admin_dashboard()
            else:
                self._show_user_dashboard()

    def _show_registration_screen(self):
        self.clear_window()

        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(main_frame, text="Регистрация нового пользователя",
                     font=("Arial", 24, "bold")).pack(pady=20)

        reg_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        reg_frame.pack(pady=20)

        ctk.CTkLabel(reg_frame, text="Логин:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.reg_username = ctk.CTkEntry(reg_frame, width=250, font=("Arial", 14))
        self.reg_username.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(reg_frame, text="Пароль:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.reg_password = ctk.CTkEntry(reg_frame, width=250, font=("Arial", 14), show="*")
        self.reg_password.grid(row=1, column=1, padx=10, pady=10)

        button_frame = ctk.CTkFrame(reg_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ctk.CTkButton(button_frame, text="Зарегистрировать", command=self._handle_register,
                      width=150, corner_radius=10).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Назад", command=self.show_login_screen,
                      width=100, corner_radius=10).pack(side="left", padx=10)

        self.reg_password.bind('<Return>', lambda e: self._handle_register())

    def _show_create_admin_screen(self):
        self.clear_window()

        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(main_frame, text="Создание администратора",
                     font=("Arial", 24, "bold")).pack(pady=20)

        admin_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        admin_frame.pack(pady=20)

        ctk.CTkLabel(admin_frame, text="Логин:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.admin_username = ctk.CTkEntry(admin_frame, width=250, font=("Arial", 14))
        self.admin_username.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(admin_frame, text="Пароль:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10,
                                                                           sticky="w")
        self.admin_password = ctk.CTkEntry(admin_frame, width=250, font=("Arial", 14), show="*")
        self.admin_password.grid(row=1, column=1, padx=10, pady=10)

        button_frame = ctk.CTkFrame(admin_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ctk.CTkButton(button_frame, text="Создать", command=self._handle_create_admin,
                      width=150, corner_radius=10).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Назад", command=self.show_login_screen,
                      width=100, corner_radius=10).pack(side="left", padx=10)

    def _handle_login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            from application.commands.user_commands import LoginUserCommand
            command = LoginUserCommand(username=username, password=password)
            user = self.app.user_command_handler.handle_login(command)

            if user:
                self.current_user = user

                saved_theme = self.app.user_service.get_theme(user.id)
                saved_color = self.app.user_service.get_color_theme(user.id)
                ctk.set_appearance_mode(saved_theme)
                ctk.set_default_color_theme(saved_color)

                if self.app.user_service.needs_initial_balance(self.current_user.id):
                    InitialBalanceDialog.show(self.root, self.current_user.id, self.app.user_service)

                if user.has_admin_privileges():
                    self._show_admin_dashboard()
                else:
                    self._show_user_dashboard()
            else:
                messagebox.showerror("Ошибка", "Неверные учетные данные")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _handle_register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            from application.commands.user_commands import RegisterUserCommand
            command = RegisterUserCommand(username=username, password=password)
            user = self.app.user_command_handler.handle_register(command)
            messagebox.showinfo("Успех", f"Пользователь {user.username} успешно зарегистрирован!")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _handle_create_admin(self):
        username = self.admin_username.get()
        password = self.admin_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            from application.commands.user_commands import CreateAdminCommand
            command = CreateAdminCommand(username=username, password=password)
            user = self.app.user_command_handler.handle_create_admin(command)
            messagebox.showinfo("Успех", f"Администратор {user.username} успешно создан!")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _show_user_dashboard(self):
        self.clear_window()

        self._setup_menu()

        tabview = ctk.CTkTabview(self.root, corner_radius=15)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self._tabs['dashboard'] = DashboardTab(tabview.add("🏠 Главная"), self.app, self.current_user,
                                               self._update_balance_display)
        self._tabs['operations'] = OperationsTab(tabview.add("📊 Операции"), self.app, self.current_user)
        self._tabs['forecast'] = ForecastTab(tabview.add("🔮 Прогноз"), self.app, self.current_user,
                                             self._update_balance_display)
        self._tabs['reports'] = ReportsTab(tabview.add("📈 Отчеты"), self.app, self.current_user)
        self._tabs['budget'] = BudgetTab(tabview.add("💰 Бюджет"), self.app, self.current_user)
        self._tabs['calendar'] = CalendarTab(tabview.add("📅 Календарь"), self.app, self.current_user)
        self._tabs['counterparty'] = CounterpartyTab(tabview.add("🏪 Контрагенты"), self.app, self.current_user)
        self._tabs['goals'] = GoalsTab(tabview.add("🎯 Цели"), self.app, self.current_user)
        self._tabs['scheduled'] = ScheduledTab(tabview.add("⏰ Платежи"), self.app, self.current_user)
        self._tabs['search'] = SearchTab(tabview.add("🔍 Поиск"), self.app, self.current_user)
        self._tabs['backup'] = BackupTab(tabview.add("💾 Резервная копия"), self.app, self.current_user)
        self._tabs['settings'] = SettingsTab(tabview.add("⚙️ Настройки"), self.app, self.current_user,
                                             self._update_balance_display, self._toggle_theme)

        self._check_startup_notifications()
        self._process_due_payments()

    def _show_admin_dashboard(self):
        self.clear_window()

        self._setup_menu()

        tabview = ctk.CTkTabview(self.root, corner_radius=15)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self._tabs['dashboard'] = DashboardTab(tabview.add("🏠 Главная"), self.app, self.current_user,
                                               self._update_balance_display)
        self._tabs['operations'] = OperationsTab(tabview.add("📊 Операции"), self.app, self.current_user)
        self._tabs['forecast'] = ForecastTab(tabview.add("🔮 Прогноз"), self.app, self.current_user,
                                             self._update_balance_display)
        self._tabs['reports'] = ReportsTab(tabview.add("📈 Отчеты"), self.app, self.current_user)
        self._tabs['budget'] = BudgetTab(tabview.add("💰 Бюджет"), self.app, self.current_user)
        self._tabs['calendar'] = CalendarTab(tabview.add("📅 Календарь"), self.app, self.current_user)
        self._tabs['counterparty'] = CounterpartyTab(tabview.add("🏪 Контрагенты"), self.app, self.current_user)
        self._tabs['goals'] = GoalsTab(tabview.add("🎯 Цели"), self.app, self.current_user)
        self._tabs['scheduled'] = ScheduledTab(tabview.add("⏰ Платежи"), self.app, self.current_user)
        self._tabs['search'] = SearchTab(tabview.add("🔍 Поиск"), self.app, self.current_user)
        self._tabs['backup'] = BackupTab(tabview.add("💾 Резервная копия"), self.app, self.current_user)
        self._tabs['admin'] = AdminTab(tabview.add("👑 Администрирование"), self.app, self.current_user)
        self._tabs['settings'] = SettingsTab(tabview.add("⚙️ Настройки"), self.app, self.current_user,
                                             self._update_balance_display, self._toggle_theme)

        self._check_startup_notifications()
        self._process_due_payments()

    def _setup_menu(self):
        menu_frame = ctk.CTkFrame(self.root, corner_radius=10, height=50)
        menu_frame.pack(fill="x", padx=10, pady=(10, 0))

        role_text = "АДМИНИСТРАТОР" if self.current_user.has_admin_privileges() else "Пользователь"
        ctk.CTkLabel(menu_frame, text=f"{role_text}: {self.current_user.username}",
                     font=("Arial", 14, "bold")).pack(side="left", padx=20)

        ctk.CTkButton(menu_frame, text="Выйти", command=self.show_login_screen,
                      width=80, corner_radius=8).pack(side="right", padx=5)

    def _show_export_dialog(self):
        if 'backup' in self._tabs:
            self._tabs['backup']._show_export_dialog()

    def _show_import_dialog(self):
        if 'backup' in self._tabs:
            self._tabs['backup']._show_import_dialog()

    def _check_startup_notifications(self):
        try:
            notifications = self.app.notification_service.get_startup_notifications(self.current_user.id)
            if notifications:
                notif_text = "\n\n".join([f"{n['title']}\n{n['message']}" for n in notifications])
                messagebox.showwarning("Внимание", notif_text)
        except Exception as e:
            print(f"Ошибка при проверке уведомлений: {e}")

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
                for tab in self._tabs.values():
                    if hasattr(tab, 'refresh'):
                        tab.refresh()
        except Exception as e:
            print(f"Ошибка при обработке платежей: {e}")

    def _refresh_all(self):
        for tab_name, tab in self._tabs.items():
            if hasattr(tab, 'refresh'):
                tab.refresh()

    def _update_balance_display(self):
        pass

    def run(self):
        self.root.mainloop()