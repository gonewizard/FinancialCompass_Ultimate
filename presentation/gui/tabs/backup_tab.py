import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from pathlib import Path
from datetime import datetime


class BackupTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self.parent, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Резервное копирование данных",
                     font=("Arial", 18, "bold")).pack(pady=20)

        info_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=10)

        info_text = "Резервное копирование позволяет сохранить ваши финансовые данные и восстановить их.\n"
        info_text += "Доступны два формата: копия базы данных и читаемый формат."

        ctk.CTkLabel(info_frame, text=info_text, wraplength=500, justify="left").pack(pady=15, padx=15)

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="📤 Экспорт данных", command=self._show_export_dialog,
                      corner_radius=10, width=180, height=40).pack(side="left", padx=15)
        ctk.CTkButton(button_frame, text="📥 Импорт данных", command=self._show_import_dialog,
                      corner_radius=10, width=180, height=40).pack(side="left", padx=15)

        stats_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(stats_frame, text="Статистика резервных копий", font=("Arial", 14, "bold")).pack(anchor="w",
                                                                                                      padx=15,
                                                                                                      pady=(10, 5))

        self.stats_text = ctk.CTkTextbox(stats_frame, height=150, corner_radius=8)
        self.stats_text.pack(fill="x", padx=15, pady=10)
        self.stats_text.configure(state="disabled")

        ctk.CTkButton(stats_frame, text="Обновить статистику", command=self._update_stats,
                      corner_radius=8, width=150).pack(pady=10)

        self._update_stats()

    def _update_stats(self):
        try:
            db_path = getattr(self.app, 'db_path', 'financial_compass.db')
            db_file = Path(db_path)

            stats_text = ""
            if db_file.exists():
                db_size = db_file.stat().st_size / 1024
                db_mtime = datetime.fromtimestamp(db_file.stat().st_mtime)
                stats_text += f"Размер базы данных: {db_size:.2f} КБ\n"
                stats_text += f"Последнее изменение: {db_mtime.strftime('%d.%m.%Y %H:%M')}\n\n"

            backup_dir = Path(".")
            backup_files = list(backup_dir.glob("backup_*.db")) + list(backup_dir.glob("backup_*.json"))

            if backup_files:
                stats_text += "Найдены резервные копии:\n"
                for file in sorted(backup_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    file_time = datetime.fromtimestamp(file.stat().st_mtime)
                    file_size = file.stat().st_size / 1024
                    stats_text += f"  • {file.name} ({file_size:.1f} КБ, {file_time.strftime('%d.%m.%Y')})\n"
            else:
                stats_text += "Резервные копии не найдены.\n"

            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", stats_text)
            self.stats_text.configure(state="disabled")
        except Exception as e:
            self.stats_text.configure(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", f"Ошибка: {e}")
            self.stats_text.configure(state="disabled")

    def _show_export_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Экспорт данных")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Экспорт данных", font=("Arial", 16, "bold")).pack(pady=10)

        tabview = ctk.CTkTabview(dialog, corner_radius=10)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)

        sqlite_tab = tabview.add("Копия базы данных")
        json_tab = tabview.add("Читаемый формат")

        self._setup_sqlite_export_tab(sqlite_tab, dialog)
        self._setup_json_export_tab(json_tab, dialog)

        ctk.CTkButton(dialog, text="Закрыть", command=dialog.destroy, corner_radius=8).pack(pady=10)

    def _setup_sqlite_export_tab(self, parent, dialog):
        ctk.CTkLabel(parent, text="Экспорт всей базы данных", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(parent, text="Сохранит полную копию базы данных.", wraplength=400).pack(pady=5)

        ctk.CTkLabel(parent, text="Папка для сохранения:").pack(anchor="w", pady=5)

        path_frame = ctk.CTkFrame(parent)
        path_frame.pack(fill="x", pady=5)

        self.backup_path_var = ctk.StringVar(value=".")
        path_entry = ctk.CTkEntry(path_frame, textvariable=self.backup_path_var)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_path():
            folder = filedialog.askdirectory(title="Выберите папку для сохранения")
            if folder:
                self.backup_path_var.set(folder)

        ctk.CTkButton(path_frame, text="Обзор...", command=browse_path, width=80).pack(side="right")

        def export_sqlite():
            try:
                from application.commands.backup_commands import ExportToSQLiteCommand
                command = ExportToSQLiteCommand(export_path=self.backup_path_var.get())
                result = self.app.backup_command_handler.handle_export_to_sqlite(command)

                if result['success']:
                    messagebox.showinfo("Успех", result['message'])
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", result['message'])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")

        ctk.CTkButton(parent, text="Экспортировать", command=export_sqlite, corner_radius=10).pack(pady=20)

    def _setup_json_export_tab(self, parent, dialog):
        ctk.CTkLabel(parent, text="Экспорт в читаемый формат", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(parent, text="Сохранит данные в читаемом формате.", wraplength=400).pack(pady=5)

        ctk.CTkLabel(parent, text="Что экспортировать:").pack(anchor="w", pady=5)

        self.export_scope_var = ctk.StringVar(value="all")
        ctk.CTkRadioButton(parent, text="Все данные", variable=self.export_scope_var, value="all").pack(anchor="w",
                                                                                                        padx=20)
        ctk.CTkRadioButton(parent, text="Только мои данные", variable=self.export_scope_var, value="user").pack(
            anchor="w", padx=20)

        ctk.CTkLabel(parent, text="Папка для сохранения:").pack(anchor="w", pady=5)

        path_frame = ctk.CTkFrame(parent)
        path_frame.pack(fill="x", pady=5)

        self.json_path_var = ctk.StringVar(value=".")
        json_path_entry = ctk.CTkEntry(path_frame, textvariable=self.json_path_var)
        json_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_json_path():
            folder = filedialog.askdirectory(title="Выберите папку для сохранения")
            if folder:
                self.json_path_var.set(folder)

        ctk.CTkButton(path_frame, text="Обзор...", command=browse_json_path, width=80).pack(side="right")

        def export_json():
            try:
                from application.commands.backup_commands import ExportToJSONCommand
                user_id = self.current_user.id if self.export_scope_var.get() == "user" else None
                command = ExportToJSONCommand(export_path=self.json_path_var.get(), user_id=user_id)
                result = self.app.backup_command_handler.handle_export_to_json(command)

                if result['success']:
                    messagebox.showinfo("Успех", result['message'])
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", result['message'])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {e}")

        ctk.CTkButton(parent, text="Экспортировать", command=export_json, corner_radius=10).pack(pady=20)

    def _show_import_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Импорт данных")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()

        self.import_file_var = ctk.StringVar()
        self.import_mode_var = ctk.StringVar(value="replace")
        self.json_import_file_var = ctk.StringVar()

        ctk.CTkLabel(dialog, text="Импорт данных", font=("Arial", 16, "bold")).pack(pady=10)

        tabview = ctk.CTkTabview(dialog, corner_radius=10)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)

        sqlite_tab = tabview.add("Копия базы данных")
        json_tab = tabview.add("Читаемый формат")

        self._setup_sqlite_import_tab(sqlite_tab, dialog)
        self._setup_json_import_tab(json_tab, dialog)

        ctk.CTkButton(dialog, text="Закрыть", command=dialog.destroy, corner_radius=8).pack(pady=10)

    def _setup_sqlite_import_tab(self, parent, dialog):
        ctk.CTkLabel(parent, text="Импорт из копии базы данных", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(parent, text="Загрузит данные из файла базы данных.", wraplength=400).pack(pady=5)

        ctk.CTkLabel(parent, text="Режим импорта:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        mode_frame = ctk.CTkFrame(parent)
        mode_frame.pack(fill="x", pady=5)

        ctk.CTkRadioButton(mode_frame, text="Заменить текущие данные", variable=self.import_mode_var,
                           value="replace").pack(anchor="w")
        ctk.CTkRadioButton(mode_frame, text="Объединить с текущими данными", variable=self.import_mode_var,
                           value="merge").pack(anchor="w")

        ctk.CTkLabel(parent, text="Файл для импорта:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", pady=5)

        file_entry = ctk.CTkEntry(file_frame, textvariable=self.import_file_var)
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_file():
            filename = filedialog.askopenfilename(
                title="Выберите файл базы данных",
                filetypes=[("База данных", "*.db"), ("База данных", "*.sqlite"), ("Все файлы", "*.*")]
            )
            if filename:
                self.import_file_var.set(filename)

        ctk.CTkButton(file_frame, text="Обзор...", command=browse_file, width=80).pack(side="right")

        ctk.CTkLabel(parent, text="ВНИМАНИЕ: Замена данных удалит текущую информацию!",
                     text_color="red", font=("Arial", 10, "bold")).pack(pady=10)

        def import_sqlite():
            if not self.import_file_var.get():
                messagebox.showwarning("Предупреждение", "Выберите файл для импорта")
                return

            if self.import_mode_var.get() == "replace":
                if not messagebox.askyesno("Подтверждение",
                                           "Вы уверены, что хотите ЗАМЕНИТЬ текущие данные?\nВсе существующие данные будут УДАЛЕНЫ!"):
                    return

            try:
                from application.commands.backup_commands import ImportFromSQLiteCommand
                command = ImportFromSQLiteCommand(import_path=self.import_file_var.get(),
                                                  mode=self.import_mode_var.get())
                result = self.app.backup_command_handler.handle_import_from_sqlite(command)

                if result.get('success'):
                    messagebox.showinfo("Успех", result['message'])
                    dialog.destroy()
                    self.parent.master._refresh_all()
                else:
                    messagebox.showerror("Ошибка", result.get('message', 'Неизвестная ошибка'))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {e}")

        ctk.CTkButton(parent, text="ИМПОРТИРОВАТЬ", command=import_sqlite, corner_radius=10).pack(pady=20)

    def _setup_json_import_tab(self, parent, dialog):
        ctk.CTkLabel(parent, text="Импорт из читаемого формата", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(parent, text="Загрузит данные из файла.", wraparound=400).pack(pady=5)

        ctk.CTkLabel(parent, text="Файл для импорта:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", pady=5)

        json_file_entry = ctk.CTkEntry(file_frame, textvariable=self.json_import_file_var)
        json_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_json_file():
            filename = filedialog.askopenfilename(
                title="Выберите файл",
                filetypes=[("JSON files", "*.json"), ("Все файлы", "*.*")]
            )
            if filename:
                self.json_import_file_var.set(filename)

        ctk.CTkButton(file_frame, text="Обзор...", command=browse_json_file, width=80).pack(side="right")

        def import_json():
            if not self.json_import_file_var.get():
                messagebox.showwarning("Предупреждение", "Выберите файл для импорта")
                return

            if not messagebox.askyesno("Подтверждение", "Импортировать данные из файла?"):
                return

            try:
                from application.commands.backup_commands import ImportFromJSONCommand
                command = ImportFromJSONCommand(import_path=self.json_import_file_var.get())
                result = self.app.backup_command_handler.handle_import_from_json(command)

                if result.get('success'):
                    messagebox.showinfo("Успех", result['message'])
                    dialog.destroy()
                    self.parent.master._refresh_all()
                else:
                    messagebox.showerror("Ошибка", result.get('message', 'Неизвестная ошибка'))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при импорте: {e}")

        ctk.CTkButton(parent, text="ИМПОРТИРОВАТЬ", command=import_json, corner_radius=10).pack(pady=20)

    def refresh(self):
        self._update_stats()