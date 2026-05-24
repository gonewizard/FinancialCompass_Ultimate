import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import Dict
from core.entities.operation import OperationType


class CalendarTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(control_frame, text="Финансовая активность", font=("Arial", 16, "bold")).pack(side="left", padx=15)

        nav_frame = ctk.CTkFrame(control_frame)
        nav_frame.pack(side="right", padx=15)

        self.calendar_month_var = ctk.StringVar(value=datetime.now().strftime('%B'))
        self.calendar_year_var = ctk.IntVar(value=datetime.now().year)

        ctk.CTkButton(nav_frame, text="◀", width=30, command=self._prev_month, corner_radius=8).pack(side="left",
                                                                                                     padx=2)
        ctk.CTkLabel(nav_frame, textvariable=self.calendar_month_var, font=("Arial", 14, "bold")).pack(side="left",
                                                                                                       padx=10)
        ctk.CTkLabel(nav_frame, textvariable=self.calendar_year_var, font=("Arial", 14)).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="▶", width=30, command=self._next_month, corner_radius=8).pack(side="left",
                                                                                                     padx=2)

        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=10, pady=5)

        legend_frame = ctk.CTkFrame(info_frame)
        legend_frame.pack(side="left", padx=15, pady=5)

        ctk.CTkLabel(legend_frame, text="Легенда:", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        colors = [("Нет трат", "#ffffff"), ("До 1000₽", "#90EE90"), ("1000-5000₽", "#FFFF00"),
                  ("5000-10000₽", "#FFA500"), ("Более 10000₽", "#FF0000")]

        for text, color in colors:
            legend_item = ctk.CTkFrame(legend_frame)
            legend_item.pack(side="left", padx=10)
            color_box = ctk.CTkFrame(legend_item, width=20, height=20, fg_color=color, corner_radius=3)
            color_box.pack(side="left", padx=2)
            ctk.CTkLabel(legend_item, text=text, font=("Arial", 10)).pack(side="left")

        self.month_total_label = ctk.CTkLabel(info_frame, text="", font=("Arial", 12, "bold"))
        self.month_total_label.pack(side="right", padx=15)

        self.calendar_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkButton(main_frame, text="Обновить", command=self._refresh_calendar,
                      corner_radius=10, width=120).pack(pady=10)

        self._refresh_calendar()

    def _prev_month(self):
        current_date = datetime(self.calendar_year_var.get(),
                                datetime.strptime(self.calendar_month_var.get(), '%B').month, 1)
        prev_date = current_date - timedelta(days=1)
        self.calendar_year_var.set(prev_date.year)
        self.calendar_month_var.set(prev_date.strftime('%B'))
        self._refresh_calendar()

    def _next_month(self):
        current_date = datetime(self.calendar_year_var.get(),
                                datetime.strptime(self.calendar_month_var.get(), '%B').month, 1)
        if current_date.month == 12:
            next_date = datetime(current_date.year + 1, 1, 1)
        else:
            next_date = datetime(current_date.year, current_date.month + 1, 1)
        self.calendar_year_var.set(next_date.year)
        self.calendar_month_var.set(next_date.strftime('%B'))
        self._refresh_calendar()

    def _refresh_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        year = self.calendar_year_var.get()
        month_num = datetime.strptime(self.calendar_month_var.get(), '%B').month

        daily_data = self._get_daily_expenses(year, month_num)

        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for i, day in enumerate(days):
            bg_color = "#2d2d2d" if ctk.get_appearance_mode() == "Dark" else "#e0e0e0"
            header = ctk.CTkLabel(self.calendar_frame, text=day, font=("Arial", 12, "bold"),
                                  fg_color=bg_color, corner_radius=5, width=100, height=30)
            header.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")

        first_day = datetime(year, month_num, 1)
        start_weekday = first_day.weekday()

        if month_num == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month_num + 1, 1)
        days_in_month = (next_month - timedelta(days=1)).day

        row = 1
        day_counter = 1
        month_total = 0

        for col in range(start_weekday):
            empty_frame = ctk.CTkFrame(self.calendar_frame, width=100, height=80, corner_radius=8)
            empty_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        col = start_weekday

        while day_counter <= days_in_month:
            day_expenses = daily_data.get(day_counter, 0)
            month_total += day_expenses

            if day_expenses == 0:
                bg_color = "#ffffff"
                text_color = "#000000"
            elif day_expenses < 1000:
                bg_color = "#90EE90"
                text_color = "#000000"
            elif day_expenses < 5000:
                bg_color = "#FFFF00"
                text_color = "#000000"
            elif day_expenses < 10000:
                bg_color = "#FFA500"
                text_color = "#000000"
            else:
                bg_color = "#FF0000"
                text_color = "#FFFFFF"

            day_frame = ctk.CTkFrame(self.calendar_frame, fg_color=bg_color, corner_radius=8, width=100, height=80)
            day_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            day_frame.grid_propagate(False)

            day_label = ctk.CTkLabel(day_frame, text=str(day_counter), font=("Arial", 14, "bold"),
                                     text_color=text_color)
            day_label.pack(anchor="nw", padx=5, pady=2)

            if day_expenses > 0:
                expense_label = ctk.CTkLabel(day_frame, text=f"{day_expenses:.0f}₽",
                                             font=("Arial", 11, "bold"), text_color=text_color)
                expense_label.pack(expand=True)

            day_counter += 1
            col += 1

            if col > 6:
                col = 0
                row += 1

        while col <= 6:
            empty_frame = ctk.CTkFrame(self.calendar_frame, width=100, height=80, corner_radius=8)
            empty_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            col += 1

        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)

        avg_daily = month_total / days_in_month if days_in_month > 0 else 0
        self.month_total_label.configure(text=f"Всего: {month_total:.2f}₽ | Средний день: {avg_daily:.0f}₽")

    def _get_daily_expenses(self, year: int, month: int) -> Dict[int, float]:
        try:
            start_date = datetime(year, month, 1, 0, 0, 0)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
            else:
                end_date = datetime(year, month + 1, 1, 0, 0, 0) - timedelta(seconds=1)

            operations = self.app.operation_service._operation_repository.find_by_user_and_period(
                self.current_user.id, start_date, end_date)

            daily = {}
            for op in operations:
                if op.type == OperationType.EXPENSE:
                    day = op.operation_date.day
                    daily[day] = daily.get(day, 0) + op.amount
            return daily
        except Exception as e:
            print(f"Ошибка календаря: {e}")
            return {}

    def refresh(self):
        self._refresh_calendar()