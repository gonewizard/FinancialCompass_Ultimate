import customtkinter as ctk
from tkinter import messagebox


class SettingsTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None, toggle_theme_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self.toggle_theme_callback = toggle_theme_callback
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self._setup_theme_section(main_frame)
        self._setup_color_section(main_frame)
        self._setup_info_section(main_frame)

    def _setup_theme_section(self, parent):
        theme_frame = ctk.CTkFrame(parent, corner_radius=10)
        theme_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(theme_frame, text="Режим оформления", font=("Arial", 16, "bold")).pack(anchor="w", padx=15,
                                                                                            pady=10)

        current_theme = self.app.user_service.get_theme(self.current_user.id)
        self.theme_var = ctk.StringVar(value="Светлая" if current_theme == "light" else "Тёмная")

        theme_combo = ctk.CTkComboBox(theme_frame, variable=self.theme_var,
                                      values=["Светлая", "Тёмная"], width=150, state="readonly")
        theme_combo.pack(anchor="w", padx=15, pady=5)

        def apply_theme():
            new_theme = "light" if self.theme_var.get() == "Светлая" else "dark"
            self.app.user_service.update_theme(self.current_user.id, new_theme)
            ctk.set_appearance_mode(new_theme)
            messagebox.showinfo("Успех", "Тема оформления изменена")

        ctk.CTkButton(theme_frame, text="Применить тему", command=apply_theme,
                      corner_radius=8, width=150, height=32).pack(anchor="w", padx=15, pady=10)

    def _setup_color_section(self, parent):
        color_frame = ctk.CTkFrame(parent, corner_radius=10)
        color_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(color_frame, text="Акцентный цвет", font=("Arial", 16, "bold")).pack(anchor="w", padx=15, pady=10)

        current_color = self.app.user_service.get_color_theme(self.current_user.id)
        self.color_var = ctk.StringVar(value=current_color)

        color_combo = ctk.CTkComboBox(color_frame, variable=self.color_var,
                                      values=["green", "blue", "dark-blue"], width=120, state="readonly")
        color_combo.pack(anchor="w", padx=15, pady=5)

        def apply_color():
            new_color = self.color_var.get()
            self.app.user_service.update_color_theme(self.current_user.id, new_color)
            ctk.set_default_color_theme(new_color)
            messagebox.showinfo("Успех", f"Акцентный цвет изменён на {new_color}")

        ctk.CTkButton(color_frame, text="Применить цвет", command=apply_color,
                      corner_radius=8, width=150, height=32).pack(anchor="w", padx=15, pady=10)

    def _setup_info_section(self, parent):
        info_frame = ctk.CTkFrame(parent, corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(info_frame, text="О программе", font=("Arial", 16, "bold")).pack(anchor="w", padx=15, pady=10)

        info_text = f"""
        Финансовый компас v1.0.0

        Пользователь: {self.current_user.username}
        Роль: {"Администратор" if self.current_user.has_admin_privileges() else "Пользователь"}

        Функционал:
        • Управление операциями (доходы/расходы)
        • Бюджетные лимиты
        • Финансовые цели
        • Плановые платежи
        • Отчёты и аналитика
        • Резервное копирование
        • Прогноз расходов
        • Дашборд с виджетами
        """

        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 11), justify="left").pack(anchor="w", padx=15, pady=5)

    def refresh(self):
        pass