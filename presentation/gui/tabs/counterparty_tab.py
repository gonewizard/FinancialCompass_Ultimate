import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class CounterpartyTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        control_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(control_frame, text="Топ-5 самых частых контрагентов", font=("Arial", 16, "bold")).pack(
            side="left", padx=15, pady=10)

        period_frame = ctk.CTkFrame(control_frame)
        period_frame.pack(side="right", padx=15)

        ctk.CTkLabel(period_frame, text="Период:").pack(side="left", padx=5)
        self.counterparty_period_var = ctk.StringVar(value="3")
        period_combo = ctk.CTkComboBox(period_frame, variable=self.counterparty_period_var,
                                       values=["1", "3", "6", "12"], width=60, state="readonly")
        period_combo.pack(side="left", padx=5)
        ctk.CTkLabel(period_frame, text="месяцев").pack(side="left", padx=5)

        ctk.CTkButton(control_frame, text="Обновить", command=self._refresh_stats,
                      corner_radius=8, width=100).pack(side="right", padx=15, pady=10)

        columns_frame = ctk.CTkFrame(main_frame)
        columns_frame.pack(fill="both", expand=True, padx=10, pady=5)

        left_frame = ctk.CTkFrame(columns_frame, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(left_frame, text="Статистика", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        from tkinter import ttk
        columns = ('name', 'count', 'total', 'avg', 'last_date', 'category')
        self.counterparty_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=10)

        self.counterparty_tree.heading('name', text='Контрагент')
        self.counterparty_tree.heading('count', text='Кол-во')
        self.counterparty_tree.heading('total', text='Всего (₽)')
        self.counterparty_tree.heading('avg', text='Средний чек (₽)')
        self.counterparty_tree.heading('last_date', text='Последний раз')
        self.counterparty_tree.heading('category', text='Категория')

        self.counterparty_tree.column('name', width=150)
        self.counterparty_tree.column('count', width=70, anchor='center')
        self.counterparty_tree.column('total', width=120, anchor='e')
        self.counterparty_tree.column('avg', width=120, anchor='e')
        self.counterparty_tree.column('last_date', width=100, anchor='center')
        self.counterparty_tree.column('category', width=120)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.counterparty_tree.yview)
        self.counterparty_tree.configure(yscrollcommand=scrollbar.set)

        self.counterparty_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        right_frame = ctk.CTkFrame(columns_frame, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(right_frame, text="Визуализация", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                        pady=(10, 5))

        self.chart_frame = ctk.CTkFrame(right_frame, corner_radius=10)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        summary_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(summary_frame, text="Сводка", font=("Arial", 14, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        self.summary_text = ctk.CTkTextbox(summary_frame, height=80, corner_radius=8)
        self.summary_text.pack(fill="x", padx=15, pady=10)
        self.summary_text.configure(state="disabled")

        self._refresh_stats()

    def _refresh_stats(self):
        try:
            months = int(self.counterparty_period_var.get())
            counterparties = self.app.operation_service.get_top_counterparties(self.current_user.id, limit=5,
                                                                               months=months)

            for item in self.counterparty_tree.get_children():
                self.counterparty_tree.delete(item)

            medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
            total_all = 0
            total_count = 0

            for i, cp in enumerate(counterparties):
                last_date = cp['last_date'].strftime('%d.%m.%Y') if cp['last_date'] else '-'
                display_name = f"{medals[i]} {cp['name']}" if i < 3 else cp['name']

                self.counterparty_tree.insert('', 'end', values=(
                    display_name, cp['count'], f"{cp['total']:.2f}", f"{cp['avg']:.2f}", last_date, cp['category']
                ))
                total_all += cp['total']
                total_count += cp['count']

            self._update_summary(counterparties, months, total_all, total_count)
            self._draw_chart(counterparties)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")

    def _update_summary(self, counterparties, months, total_all, total_count):
        summary_text = f"За последние {months} месяцев: "
        if not counterparties:
            summary_text += "нет данных по контрагентам."
        else:
            summary_text += f"в топ-5 вошли контрагенты с {total_count} покупками на сумму {total_all:.2f}₽.\n"
            if len(counterparties) > 0:
                summary_text += f"1 место: {counterparties[0]['name']} - {counterparties[0]['count']} раз"
            if len(counterparties) > 1:
                summary_text += f" | 2 место: {counterparties[1]['name']} - {counterparties[1]['count']} раз"
            if len(counterparties) > 2:
                summary_text += f" | 3 место: {counterparties[2]['name']} - {counterparties[2]['count']} раз"

        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary_text)
        self.summary_text.configure(state="disabled")

    def _draw_chart(self, counterparties):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not counterparties:
            ctk.CTkLabel(self.chart_frame, text="Нет данных для отображения", font=("Arial", 14)).pack(expand=True)
            return

        fig = Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)

        names = [cp['name'][:12] + '…' if len(cp['name']) > 12 else cp['name'] for cp in counterparties]
        counts = [cp['count'] for cp in counterparties]
        totals = [cp['total'] for cp in counterparties]

        x_pos = range(len(names))
        bars = ax.bar(x_pos, counts, color='#4CAF50', alpha=0.8, edgecolor='black')

        for i, (bar, count, total) in enumerate(zip(bars, counts, totals)):
            if count > 1:
                ax.text(bar.get_x() + bar.get_width() / 2., count * 0.2, f'{total:.0f}₽',
                        ha='center', va='center', fontsize=9, color='white', fontweight='bold')
            ax.text(bar.get_x() + bar.get_width() / 2., count - count * 0.15, f'{count} раз',
                    ha='center', va='top', fontsize=9, fontweight='bold', color='white')

        ax.set_xlabel('Контрагенты', fontsize=10, fontweight='bold')
        ax.set_ylabel('Количество покупок', fontsize=10, fontweight='bold')
        ax.set_title('Топ-5 контрагентов по частоте посещений', fontsize=12, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(names, rotation=15, ha='right', fontsize=9)
        ax.grid(True, alpha=0.2, axis='y', linestyle='--')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def refresh(self):
        self._refresh_stats()