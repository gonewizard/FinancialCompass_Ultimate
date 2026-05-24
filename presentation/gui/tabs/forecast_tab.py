import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from core.entities.operation import OperationType
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ForecastTab:
    def __init__(self, parent, app, current_user, update_balance_callback=None):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self.update_balance_callback = update_balance_callback
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        main_frame = ctk.CTkScrollableFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(info_frame, text="🔮 Прогноз расходов", font=("Arial", 18, "bold")).pack(anchor="w", padx=15,
                                                                                             pady=10)

        ctk.CTkLabel(info_frame,
                     text="Прогноз основан на анализе ваших расходов за последние 3 месяца.\n"
                          "Система рассчитывает среднемесячные расходы по каждой категории\n"
                          "и прогнозирует бюджет на следующий месяц.",
                     font=("Arial", 12), justify="left").pack(anchor="w", padx=15, pady=5)

        control_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        control_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(control_frame, text="Параметры прогноза", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                pady=10)

        period_frame = ctk.CTkFrame(control_frame)
        period_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(period_frame, text="Период анализа:", font=("Arial", 12)).pack(side="left", padx=5)
        self.period_var = ctk.StringVar(value="3")
        period_combo = ctk.CTkComboBox(period_frame, variable=self.period_var,
                                       values=["3", "6", "12"], width=60, state="readonly")
        period_combo.pack(side="left", padx=5)
        ctk.CTkLabel(period_frame, text="месяцев", font=("Arial", 12)).pack(side="left", padx=5)

        ctk.CTkButton(control_frame, text="Рассчитать прогноз", command=self.refresh,
                      corner_radius=8, width=150, height=32).pack(pady=10)

        self.chart_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.info_text = ctk.CTkTextbox(main_frame, height=120, corner_radius=10)
        self.info_text.pack(fill="x", padx=20, pady=10)
        self.info_text.configure(state="disabled")

        self.refresh()

    def _calculate_forecast(self):
        months = int(self.period_var.get())

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30 * months)

        operations = self.app.operation_service.get_user_operations(self.current_user.id)

        monthly_expenses = {}
        category_averages = {}

        for op in operations:
            if op.type == OperationType.EXPENSE:
                op_date = op.operation_date.date() if hasattr(op.operation_date, 'date') else op.operation_date
                if op_date >= start_date and op_date <= end_date:
                    month_key = op_date.strftime('%Y-%m')
                    if month_key not in monthly_expenses:
                        monthly_expenses[month_key] = {}
                    monthly_expenses[month_key][op.category] = monthly_expenses[month_key].get(op.category,
                                                                                               0) + op.amount

        for month, categories in monthly_expenses.items():
            for category, amount in categories.items():
                if category not in category_averages:
                    category_averages[category] = []
                category_averages[category].append(amount)

        forecast = {}
        for category, amounts in category_averages.items():
            forecast[category] = sum(amounts) / len(amounts)

        total_forecast = sum(forecast.values())

        return forecast, total_forecast, len(monthly_expenses)

    def _draw_forecast_chart(self, forecast):
        color_theme = self.app.user_service.get_color_theme(self.current_user.id)
        chart_colors = {
            "green": "#2ecc71",
            "blue": "#3498db",
            "dark-blue": "#2980b9",
            "red": "#e74c3c"
        }
        main_color = chart_colors.get(color_theme, "#2ecc71")

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not forecast:
            label = ctk.CTkLabel(self.chart_frame,
                                 text="Недостаточно данных для прогноза\nДобавьте больше расходов за последние месяцы",
                                 font=("Arial", 14))
            label.pack(expand=True)
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        categories = list(forecast.keys())
        amounts = list(forecast.values())

        colors_list = plt.cm.Set3(range(len(categories)))
        ax1.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors_list)
        ax1.set_title('Прогноз расходов по категориям', fontsize=12, fontweight='bold')

        top_categories = sorted(forecast.items(), key=lambda x: x[1], reverse=True)[:7]
        top_names = [c[0] for c in top_categories]
        top_amounts = [c[1] for c in top_categories]

        bars = ax2.barh(top_names, top_amounts, color=main_color)
        ax2.set_xlabel('Сумма (руб.)', fontsize=10)
        ax2.set_title('Топ-7 категорий по прогнозу', fontsize=12, fontweight='bold')

        for bar, amount in zip(bars, top_amounts):
            ax2.text(bar.get_width() + 100, bar.get_y() + bar.get_height() / 2,
                     f'{amount:,.0f} ₽', va='center', fontsize=9)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_info(self, forecast, total_forecast, months_count):
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", "end")

        info = "🔮 РЕЗУЛЬТАТЫ ПРОГНОЗА\n\n"
        info += f"Период анализа: {months_count} месяцев\n"
        info += f"Прогнозируемые расходы на следующий месяц: {total_forecast:,.2f} ₽\n\n"
        info += "💡 Рекомендации:\n"

        if total_forecast > 0:
            avg_per_day = total_forecast / 30
            info += f"• Среднедневной бюджет: {avg_per_day:,.0f} ₽\n"

        high_categories = sorted(forecast.items(), key=lambda x: x[1], reverse=True)[:3]
        if high_categories:
            info += "• Основные категории расходов:\n"
            for cat, amt in high_categories:
                percent = (amt / total_forecast * 100) if total_forecast > 0 else 0
                info += f"  - {cat}: {amt:,.0f} ₽ ({percent:.0f}%)\n"

        self.info_text.insert("1.0", info)
        self.info_text.configure(state="disabled")

    def refresh(self):
        try:
            forecast, total_forecast, months_count = self._calculate_forecast()
            self._draw_forecast_chart(forecast)
            self._update_info(forecast, total_forecast, months_count)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось рассчитать прогноз: {e}")