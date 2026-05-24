import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from core.entities.operation import OperationType


class SearchTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        filter_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(filter_frame, text="Параметры поиска", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                             pady=(10, 5))

        input_frame = ctk.CTkFrame(filter_frame)
        input_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(input_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_category = ctk.CTkEntry(input_frame, width=200)
        self.search_category.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Контрагент:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_counterparty = ctk.CTkEntry(input_frame, width=200)
        self.search_counterparty.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.search_type = ctk.CTkComboBox(input_frame, values=["Все", "Доход", "Расход"], width=100, state="readonly")
        self.search_type.set("Все")
        self.search_type.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.search_date_from = ctk.CTkEntry(input_frame, width=120)
        self.search_date_from.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Дата до:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.search_date_to = ctk.CTkEntry(input_frame, width=120)
        self.search_date_to.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Сумма от:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.search_amount_min = ctk.CTkEntry(input_frame, width=120)
        self.search_amount_min.grid(row=2, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Сумма до:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.search_amount_max = ctk.CTkEntry(input_frame, width=120)
        self.search_amount_max.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Комментарий:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.search_description = ctk.CTkEntry(input_frame, width=200)
        self.search_description.grid(row=3, column=3, padx=5, pady=5)

        ctk.CTkButton(filter_frame, text="Найти", command=self._perform_search,
                      corner_radius=10, width=150).pack(pady=10)

        results_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(results_frame, text="Результаты поиска", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                               pady=(10, 5))

        from tkinter import ttk
        columns = ('date', 'type', 'category', 'counterparty', 'amount', 'description')
        self.search_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

        self.search_tree.heading('date', text='Дата')
        self.search_tree.heading('type', text='Тип')
        self.search_tree.heading('category', text='Категория')
        self.search_tree.heading('counterparty', text='Контрагент')
        self.search_tree.heading('amount', text='Сумма')
        self.search_tree.heading('description', text='Описание')

        self.search_tree.column('date', width=100)
        self.search_tree.column('type', width=80)
        self.search_tree.column('category', width=120)
        self.search_tree.column('counterparty', width=150)
        self.search_tree.column('amount', width=100)
        self.search_tree.column('description', width=200)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    def _perform_search(self):
        filters = {}

        if self.search_category.get().strip():
            filters['category'] = self.search_category.get().strip()
        if self.search_counterparty.get().strip():
            filters['counterparty'] = self.search_counterparty.get().strip()

        ttype = self.search_type.get()
        if ttype != 'Все':
            filters['type'] = 'income' if ttype == 'Доход' else 'expense'

        if self.search_date_from.get().strip():
            filters['date_from'] = self.search_date_from.get().strip()
        if self.search_date_to.get().strip():
            filters['date_to'] = self.search_date_to.get().strip()

        if self.search_amount_min.get().strip():
            filters['amount_min'] = float(self.search_amount_min.get())
        if self.search_amount_max.get().strip():
            filters['amount_max'] = float(self.search_amount_max.get())

        if self.search_description.get().strip():
            filters['description'] = self.search_description.get().strip()

        try:
            all_operations = self.app.operation_service.get_user_operations(self.current_user.id)

            results = []
            for op in all_operations:
                if filters.get('category') and filters['category'].lower() not in op.category.lower():
                    continue
                if filters.get('counterparty') and (
                        not op.counterparty or filters['counterparty'].lower() not in op.counterparty.lower()):
                    continue
                if filters.get('type'):
                    op_type = 'income' if op.type == OperationType.INCOME else 'expense'
                    if op_type != filters['type']:
                        continue
                if filters.get('date_from'):
                    if op.operation_date.strftime('%Y-%m-%d') < filters['date_from']:
                        continue
                if filters.get('date_to'):
                    if op.operation_date.strftime('%Y-%m-%d') > filters['date_to']:
                        continue
                if filters.get('amount_min') and op.amount < filters['amount_min']:
                    continue
                if filters.get('amount_max') and op.amount > filters['amount_max']:
                    continue
                if filters.get('description') and (
                        not op.description or filters['description'].lower() not in op.description.lower()):
                    continue
                results.append(op)

            for row in self.search_tree.get_children():
                self.search_tree.delete(row)

            for op in results:
                type_text = "Доход" if op.type == OperationType.INCOME else "Расход"
                type_icon = "📈" if op.type == OperationType.INCOME else "📉"
                self.search_tree.insert('', 'end', values=(
                    op.operation_date.strftime('%d.%m.%Y'),
                    f"{type_icon} {type_text}",
                    op.category,
                    op.counterparty or "",
                    f"{op.amount:.2f} руб.",
                    op.description or ""
                ))

            messagebox.showinfo("Поиск", f"Найдено {len(results)} операций")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {e}")

    def refresh(self):
        pass