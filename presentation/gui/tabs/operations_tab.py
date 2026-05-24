import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from core.entities.operation import OperationType
from presentation.gui.dialogs import EditOperationDialog


class OperationsTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._store_operation_ids = {}
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", padx=10, pady=5)

        self._setup_add_section(top_frame)
        self._setup_filter_section(top_frame)

        self._setup_operations_list(main_frame)

    def _setup_add_section(self, parent):
        add_frame = ctk.CTkFrame(parent, corner_radius=10)
        add_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(add_frame, text="Добавить операцию", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                           pady=(10, 5))

        type_frame = ctk.CTkFrame(add_frame)
        type_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(type_frame, text="Тип:").pack(side="left", padx=5)
        self.op_type_var = ctk.StringVar(value="income")
        ctk.CTkRadioButton(type_frame, text="Доход", variable=self.op_type_var, value="income").pack(side="left",
                                                                                                     padx=10)
        ctk.CTkRadioButton(type_frame, text="Расход", variable=self.op_type_var, value="expense").pack(side="left",
                                                                                                       padx=10)

        input_frame = ctk.CTkFrame(add_frame)
        input_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.op_amount = ctk.CTkEntry(input_frame, width=120)
        self.op_amount.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.op_category = ctk.CTkEntry(input_frame, width=120)
        self.op_category.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Контрагент:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.op_counterparty = ctk.CTkEntry(input_frame, width=300)
        self.op_counterparty.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(input_frame, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.op_description = ctk.CTkEntry(input_frame, width=300)
        self.op_description.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(input_frame, text="Направить на цель:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.op_direct_to_goal = ctk.BooleanVar(value=False)
        self.op_direct_checkbox = ctk.CTkCheckBox(input_frame, text="Направлять доход на цель",
                                                  variable=self.op_direct_to_goal, command=self._toggle_goal_selection)
        self.op_direct_checkbox.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(input_frame, text="Выбрать цель:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.op_goal_var = ctk.StringVar()
        self.op_goal_combo = ctk.CTkComboBox(input_frame, variable=self.op_goal_var, width=250, state="disabled",
                                             values=[])
        self.op_goal_combo.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(input_frame, text="Сумма на цель:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.op_goal_amount = ctk.CTkEntry(input_frame, width=120, state="disabled")
        self.op_goal_amount.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.op_goal_amount.insert(0, "100")

        def on_type_change(*args):
            if self.op_type_var.get() == "income":
                self.op_direct_checkbox.configure(state="normal")
                if self.op_direct_to_goal.get():
                    self._toggle_goal_selection(enable=True)
            else:
                self.op_direct_checkbox.configure(state="disabled")
                self.op_direct_to_goal.set(False)
                self._toggle_goal_selection(enable=False)

        self.op_type_var.trace('w', on_type_change)
        on_type_change()

        ctk.CTkButton(add_frame, text="Добавить операцию", command=self._handle_add_operation,
                      corner_radius=10, width=200).pack(pady=10)

    def _toggle_goal_selection(self, enable=None):
        if enable is None:
            enable = self.op_direct_to_goal.get()

        if enable and self.op_type_var.get() == "income":
            self.op_goal_combo.configure(state="readonly")
            self.op_goal_amount.configure(state="normal")
            self._refresh_goals_list()
        else:
            self.op_goal_combo.configure(state="disabled")
            self.op_goal_amount.configure(state="disabled")
            self.op_goal_var.set("")

    def _refresh_goals_list(self):
        try:
            goals = self.app.goal_service.get_goals(self.current_user.id)
            goal_list = [f"{goal.name} (осталось {goal.remaining_amount:.0f}₽)" for goal in goals if
                         goal.status.value != "completed"]
            self.op_goal_combo.configure(values=goal_list)
        except:
            pass

    def _setup_filter_section(self, parent):
        filter_frame = ctk.CTkFrame(parent, corner_radius=10, width=350)
        filter_frame.pack(side="right", fill="y", padx=(10, 0))
        filter_frame.pack_propagate(False)

        ctk.CTkLabel(filter_frame, text="Фильтрация операций", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                                pady=(10, 5))

        filter_inner = ctk.CTkFrame(filter_frame)
        filter_inner.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(filter_inner, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_category_var = ctk.StringVar()
        self.filter_category_combo = ctk.CTkComboBox(filter_inner, variable=self.filter_category_var, width=150,
                                                     values=["Все категории"], state="readonly")
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.set("Все категории")

        ctk.CTkLabel(filter_inner, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.filter_type_var = ctk.StringVar(value="Все")
        filter_type_combo = ctk.CTkComboBox(filter_inner, variable=self.filter_type_var, width=150,
                                            values=["Все", "Доходы", "Расходы"], state="readonly")
        filter_type_combo.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_inner, text="Дата с (ДД.ММ.ГГГГ):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.filter_start_var = ctk.StringVar()
        ctk.CTkEntry(filter_inner, textvariable=self.filter_start_var, width=150).grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_inner, text="по:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.filter_end_var = ctk.StringVar()
        ctk.CTkEntry(filter_inner, textvariable=self.filter_end_var, width=150).grid(row=3, column=1, padx=5, pady=5)

        button_frame = ctk.CTkFrame(filter_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="Применить фильтр", command=self._apply_filter, width=130,
                      corner_radius=8).pack(pady=5)
        ctk.CTkButton(button_frame, text="Сбросить фильтр", command=self._reset_filter, width=130,
                      corner_radius=8).pack(pady=5)

        self.filter_status_label = ctk.CTkLabel(filter_frame, text="Фильтр не применен", text_color="gray")
        self.filter_status_label.pack(pady=5)

    def _setup_operations_list(self, parent):
        list_frame = ctk.CTkFrame(parent, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ctk.CTkLabel(list_frame, text="История операций", font=("Arial", 14, "bold")).pack(anchor="w", padx=15,
                                                                                           pady=(10, 5))

        content_frame = ctk.CTkFrame(list_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        table_container = ctk.CTkFrame(content_frame)
        table_container.pack(side="left", fill="both", expand=True)

        columns = ('date', 'type', 'category', 'amount', 'counterparty', 'description')
        self.operations_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)

        self.operations_tree.heading('date', text='Дата')
        self.operations_tree.heading('type', text='Тип')
        self.operations_tree.heading('category', text='Категория')
        self.operations_tree.heading('amount', text='Сумма')
        self.operations_tree.heading('counterparty', text='Контрагент')
        self.operations_tree.heading('description', text='Описание')

        self.operations_tree.column('date', width=100)
        self.operations_tree.column('type', width=80)
        self.operations_tree.column('category', width=120)
        self.operations_tree.column('amount', width=100)
        self.operations_tree.column('counterparty', width=150)
        self.operations_tree.column('description', width=200)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.operations_tree.yview)
        self.operations_tree.configure(yscrollcommand=scrollbar.set)

        self.operations_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        button_frame = ctk.CTkFrame(content_frame, width=120, corner_radius=10)
        button_frame.pack(side="right", fill="y", padx=(10, 0))
        button_frame.pack_propagate(False)

        ctk.CTkButton(button_frame, text="Обновить", command=self.refresh, width=100, corner_radius=8, height=35).pack(
            pady=5)
        ctk.CTkButton(button_frame, text="Удалить", command=self._delete_operation, width=100, corner_radius=8,
                      height=35).pack(pady=5)
        ctk.CTkButton(button_frame, text="Редактировать", command=self._edit_operation, width=100, corner_radius=8,
                      height=35).pack(pady=5)
        ctk.CTkButton(button_frame, text="Excel", command=self._export_to_excel, width=100, corner_radius=8).pack(
            side="left", padx=5)

        self.refresh()

    def _export_to_excel(self):
        from presentation.gui.export_excel import ExcelExporter
        exporter = ExcelExporter(self.app, self.current_user)

        selected = self.operations_tree.selection()
        if selected:
            operations = []
            for item in selected:
                operation_id = self._store_operation_ids.get(item)
                if operation_id:
                    op = self.app.operation_service.get_operation_by_id(operation_id)
                    if op:
                        operations.append(op)
            exporter.export_operations(operations)
        else:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)
            exporter.export_operations(operations)

    def refresh(self):
        try:
            operations = self.app.operation_service.get_operations_for_period(self.current_user.id, 90)
            categories = self._get_user_categories()
            self.filter_category_combo.configure(values=["Все категории"] + categories)
            self._update_table(operations)
            self.filter_status_label.configure(text="Фильтр не применен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить операции: {e}")

    def _get_user_categories(self):
        try:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)
            return sorted(set(op.category for op in operations))
        except:
            return []

    def _update_table(self, operations):
        for item in self.operations_tree.get_children():
            self.operations_tree.delete(item)

        self._store_operation_ids.clear()

        for op in operations:
            type_text = "Доход" if op.type == OperationType.INCOME else "Расход"
            type_icon = "📈" if op.type == OperationType.INCOME else "📉"
            item = self.operations_tree.insert('', 'end', values=(
                op.operation_date.strftime('%d.%m.%Y'),
                f"{type_icon} {type_text}",
                op.category,
                f"{op.amount:.2f} руб.",
                op.counterparty or "",
                op.description or ""
            ))
            self._store_operation_ids[item] = op.id

    def _apply_filter(self):
        try:
            category = None
            if self.filter_category_var.get() and self.filter_category_var.get() != "Все категории":
                category = self.filter_category_var.get()

            operation_type = None
            type_value = self.filter_type_var.get()
            if type_value == "Доходы":
                operation_type = OperationType.INCOME
            elif type_value == "Расходы":
                operation_type = OperationType.EXPENSE

            start_date = None
            end_date = None

            if self.filter_start_var.get():
                try:
                    start_date = datetime.strptime(self.filter_start_var.get(), '%d.%m.%Y')
                except:
                    messagebox.showerror("Ошибка", "Неверный формат даты 'с'")
                    return

            if self.filter_end_var.get():
                try:
                    end_date = datetime.strptime(self.filter_end_var.get(), '%d.%m.%Y')
                except:
                    messagebox.showerror("Ошибка", "Неверный формат даты 'по'")
                    return

            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            filtered = []
            for op in operations:
                if category and op.category != category:
                    continue
                if operation_type and op.type != operation_type:
                    continue
                if start_date and op.operation_date < start_date:
                    continue
                if end_date and op.operation_date > end_date:
                    continue
                filtered.append(op)

            self._update_table(filtered)

            filter_info = []
            if category:
                filter_info.append(f"Категория: {category}")
            if operation_type:
                filter_info.append(f"Тип: {'доходы' if operation_type == OperationType.INCOME else 'расходы'}")
            if start_date:
                filter_info.append(f"с {start_date.strftime('%d.%m.%Y')}")
            if end_date:
                filter_info.append(f"по {end_date.strftime('%d.%m.%Y')}")

            if filter_info:
                self.filter_status_label.configure(text=f"Фильтр: {', '.join(filter_info)} | Найдено: {len(filtered)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка фильтрации: {e}")

    def _reset_filter(self):
        self.filter_category_var.set("Все категории")
        self.filter_type_var.set("Все")
        self.filter_start_var.set("")
        self.filter_end_var.set("")
        self.refresh()

    def _handle_add_operation(self):
        try:
            amount = float(self.op_amount.get())
            category = self.op_category.get().strip()
            description = self.op_description.get() or None
            counterparty = self.op_counterparty.get() or None

            if not category and not counterparty:
                messagebox.showerror("Ошибка", "Введите категорию или контрагента")
                return

            suggested_category = None
            if counterparty and not category:
                suggested_category = self.app.auto_category_service.get_category_for_counterparty(self.current_user.id,
                                                                                                  counterparty)
                if suggested_category:
                    category = suggested_category
                    self.op_category.delete(0, 'end')
                    self.op_category.insert(0, category)

            if not category:
                messagebox.showerror("Ошибка", "Не удалось определить категорию")
                return

            op_type = OperationType.INCOME if self.op_type_var.get() == "income" else OperationType.EXPENSE

            if op_type == OperationType.INCOME and self.op_direct_to_goal.get():
                goals = self.app.goal_service.get_goals(self.current_user.id)
                active_goals = [g for g in goals if g.status.value != "completed"]

                if not active_goals:
                    result = messagebox.askyesno(
                        "Нет активных целей",
                        "У вас нет активных целей для направления дохода.\n\nХотите создать новую цель?"
                    )
                    if result:
                        self._open_goals_tab()
                    return

                goal_info = self.op_goal_var.get()
                if not goal_info or goal_info == "":
                    messagebox.showwarning("Предупреждение", "Выберите цель для направления дохода")
                    return

            operation = self.app.operation_service.create_operation(
                self.current_user.id, op_type, amount, category, description, counterparty
            )

            if counterparty and not suggested_category:
                self.app.auto_category_service.save_rule(self.current_user.id, counterparty, category)

            if op_type == OperationType.EXPENSE:
                notifications = self.app.notification_service.check_budget_limits(self.current_user.id, category,
                                                                                  amount)
                for notif in notifications:
                    if notif['type'] == 'danger':
                        messagebox.showwarning(notif['title'], notif['message'])
                    elif notif['type'] == 'warning':
                        messagebox.showinfo(notif['title'], notif['message'])

            if op_type == OperationType.INCOME and self.op_direct_to_goal.get():
                goal_info = self.op_goal_var.get()
                if goal_info and goal_info != "":
                    try:
                        goal_name = goal_info.split(" (осталось")[0]
                        goals = self.app.goal_service.get_goals(self.current_user.id)
                        goal = next((g for g in goals if g.name == goal_name and g.status.value != "completed"), None)

                        if goal:
                            goal_amount_str = self.op_goal_amount.get()
                            if goal_amount_str and goal_amount_str.strip():
                                goal_amount = float(goal_amount_str)
                                if 0 < goal_amount <= amount:
                                    self.app.goal_service.add_to_goal_with_transaction(goal.id, operation.id,
                                                                                       goal_amount)
                                    messagebox.showinfo("Успех", f"{goal_amount:.2f}₽ направлено на цель")
                                elif goal_amount > amount:
                                    messagebox.showwarning("Предупреждение", "Сумма на цель не может превышать доход")
                            else:
                                self.app.goal_service.add_to_goal_with_transaction(goal.id, operation.id, amount)
                                messagebox.showinfo("Успех", f"{amount:.2f}₽ направлено на цель")
                    except Exception as e:
                        print(f"Ошибка: {e}")

            messagebox.showinfo("Успех", "Операция добавлена!")

            self.op_amount.delete(0, 'end')
            self.op_category.delete(0, 'end')
            self.op_counterparty.delete(0, 'end')
            self.op_description.delete(0, 'end')
            self.op_goal_amount.delete(0, 'end')
            self.op_goal_amount.insert(0, "100")

            self.refresh()
            self._refresh_parent_budget()
            self._refresh_parent_goals()
            self._refresh_parent_balance()

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат суммы")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _open_goals_tab(self):
        try:
            def find_tabview(widget):
                if hasattr(widget, 'set') and hasattr(widget, '_tab_dict'):
                    return widget
                for child in widget.winfo_children():
                    result = find_tabview(child)
                    if result:
                        return result
                return None

            tabview = find_tabview(self.parent.winfo_toplevel())
            if tabview:
                for tab_name in tabview._tab_dict.keys():
                    if "Цели" in tab_name or "🎯" in tab_name:
                        tabview.set(tab_name)
                        break
        except Exception as e:
            print(f"Ошибка при переключении на вкладку целей: {e}")

    def _delete_operation(self):
        selected = self.operations_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите операции для удаления")
            return

        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить {len(selected)} операций?\nЕсли это доходы, прогресс целей будет уменьшен."):
            return

        deleted_count = 0
        for item in selected:
            operation_id = self._store_operation_ids.get(item)
            if not operation_id:
                continue

            operation = self.app.operation_service.get_operation_by_id(operation_id)
            if not operation:
                continue

            try:
                if operation.type == OperationType.INCOME:
                    self.app.goal_service.rollback_goal_by_transaction(operation_id)

                from application.commands.operation_commands import DeleteOperationCommand
                command = DeleteOperationCommand(operation_id=operation_id, user_id=self.current_user.id)
                if self.app.operation_command_handler.handle_delete_operation(command):
                    deleted_count += 1
            except Exception as e:
                print(f"Ошибка при удалении: {e}")

        if deleted_count > 0:
            messagebox.showinfo("Успех", f"Удалено {deleted_count} операций")
            self.refresh()
            self._refresh_parent_budget()
            self._refresh_parent_goals()
            self._refresh_parent_balance()

    def _edit_operation(self):
        selected = self.operations_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите операцию")
            return

        item = selected[0]
        operation_id = self._store_operation_ids.get(item)

        if not operation_id:
            messagebox.showerror("Ошибка", "Не удалось определить операцию")
            return

        operation = self.app.operation_service.get_operation_by_id(operation_id)
        if operation:
            EditOperationDialog.show(self.parent, operation, self._save_edit)

    def _save_edit(self, operation_id, amount, category, description, counterparty):
        try:
            from application.commands.operation_commands import UpdateOperationCommand
            command = UpdateOperationCommand(
                operation_id=operation_id,
                user_id=self.current_user.id,
                amount=amount,
                category=category,
                description=description,
                counterparty=counterparty
            )
            self.app.operation_command_handler.handle_update_operation(command)
            messagebox.showinfo("Успех", "Операция обновлена")
            self.refresh()
            self._refresh_parent_budget()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh_parent_budget(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_tabs'):
                if 'budget' in self.parent.master._tabs:
                    self.parent.master._tabs['budget'].refresh()
        except:
            pass

    def _refresh_parent_goals(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_tabs'):
                if 'goals' in self.parent.master._tabs:
                    self.parent.master._tabs['goals'].refresh()
        except:
            pass

    def _refresh_parent_balance(self):
        try:
            if hasattr(self.parent, 'master') and hasattr(self.parent.master, '_update_balance_display'):
                self.parent.master._update_balance_display()
        except:
            pass