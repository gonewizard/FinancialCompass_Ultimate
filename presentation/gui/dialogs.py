import customtkinter as ctk
from tkinter import messagebox


class InitialBalanceDialog:
    @staticmethod
    def show(parent, user_id, user_service):
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Добро пожаловать!")
        dialog.geometry("450x300")
        dialog.transient(parent)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Добро пожаловать в Финансовый компас!",
                     font=("Arial", 18, "bold")).pack(pady=20)

        ctk.CTkLabel(frame, text="Введите ваш текущий баланс:",
                     font=("Arial", 12)).pack(pady=10)

        balance_var = ctk.StringVar(value="0")
        entry = ctk.CTkEntry(frame, textvariable=balance_var, font=("Arial", 14), width=200)
        entry.pack(pady=10)

        result = {"confirmed": False, "balance": 0.0}

        def save():
            try:
                balance = float(balance_var.get())
                if balance < 0:
                    messagebox.showerror("Ошибка", "Баланс не может быть отрицательным")
                    return
                user_service.update_initial_balance(user_id, balance)
                result["confirmed"] = True
                result["balance"] = balance
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число")

        ctk.CTkButton(frame, text="Начать", command=save, width=150, corner_radius=10).pack(pady=20)

        parent.wait_window(dialog)
        return result


class EditOperationDialog:
    @staticmethod
    def show(parent, operation, on_save):
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Редактирование операции")
        dialog.geometry("550x500")
        dialog.transient(parent)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Редактирование операции",
                     font=("Arial", 16, "bold")).pack(pady=10)

        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=20, pady=10)

        type_text = "Доход" if operation.type.value == "income" else "Расход"
        ctk.CTkLabel(info_frame, text=f"Тип: {type_text}", font=("Arial", 12)).pack(anchor="w", pady=2)
        ctk.CTkLabel(info_frame, text=f"Дата: {operation.operation_date.strftime('%d.%m.%Y %H:%M')}",
                     font=("Arial", 12)).pack(anchor="w", pady=2)

        edit_frame = ctk.CTkFrame(frame)
        edit_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(edit_frame, text="Сумма:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        amount_var = ctk.StringVar(value=str(operation.amount))
        amount_entry = ctk.CTkEntry(edit_frame, textvariable=amount_var, width=150)
        amount_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(edit_frame, text="Категория:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        category_var = ctk.StringVar(value=operation.category)
        category_entry = ctk.CTkEntry(edit_frame, textvariable=category_var, width=200)
        category_entry.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(edit_frame, text="Контрагент:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        counterparty_var = ctk.StringVar(value=operation.counterparty or "")
        counterparty_entry = ctk.CTkEntry(edit_frame, textvariable=counterparty_var, width=250)
        counterparty_entry.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(edit_frame, text="Описание:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        description_var = ctk.StringVar(value=operation.description or "")
        description_entry = ctk.CTkEntry(edit_frame, textvariable=description_var, width=250)
        description_entry.grid(row=3, column=1, padx=10, pady=5)

        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(pady=20)

        def save():
            try:
                amount = float(amount_var.get())
                category = category_var.get()
                if amount <= 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                    return
                if not category:
                    messagebox.showerror("Ошибка", "Категория обязательна")
                    return
                on_save(operation.id, amount, category, description_var.get() or None, counterparty_var.get() or None)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат суммы")

        ctk.CTkButton(button_frame, text="Сохранить", command=save, width=100, corner_radius=10).pack(side="left",
                                                                                                      padx=10)
        ctk.CTkButton(button_frame, text="Отмена", command=dialog.destroy, width=100, corner_radius=10).pack(
            side="left", padx=10)


class AddToGoalDialog:
    @staticmethod
    def show(parent, goal_name, goal_id, on_add):
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Пополнение цели")
        dialog.geometry("400x240")
        dialog.transient(parent)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text=f"Цель: {goal_name}", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Сумма пополнения (руб.):", font=("Arial", 12)).pack(pady=5)

        amount_var = ctk.StringVar()
        amount_entry = ctk.CTkEntry(frame, textvariable=amount_var, width=200, font=("Arial", 14))
        amount_entry.pack(pady=10)
        amount_entry.focus()

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=15)

        def add():
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Ошибка", "Сумма должна быть положительной")
                    return
                on_add(goal_id, amount, goal_name)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат суммы")

        btn_ok = ctk.CTkButton(button_frame, text="Пополнить", command=add, width=120, height=40, corner_radius=8,
                               fg_color="#2ecc71", hover_color="#27ae60", text_color="white",
                               font=("Arial", 13, "bold"))
        btn_ok.pack(side="left", padx=15)

        btn_cancel = ctk.CTkButton(button_frame, text="Отмена", command=dialog.destroy, width=120, height=40,
                                   corner_radius=8, fg_color="#e74c3c", hover_color="#c0392b", text_color="white",
                                   font=("Arial", 13, "bold"))
        btn_cancel.pack(side="left", padx=15)