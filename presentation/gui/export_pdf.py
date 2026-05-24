from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
import tempfile
import os

import matplotlib

matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Microsoft YaHei', 'SimHei']

try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    RUSSIAN_FONT = 'Arial'
except:
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        RUSSIAN_FONT = 'DejaVu'
    except:
        try:
            pdfmetrics.registerFont(TTFont('Helvetica', 'helvetica.ttf'))
            RUSSIAN_FONT = 'Helvetica'
        except:
            RUSSIAN_FONT = 'Helvetica'


class PDFExporter:
    def __init__(self, app, current_user):
        self.app = app
        self.current_user = current_user

    def _create_chart_image(self, fig, width=600, height=400):
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        fig.set_size_inches(width / 100, height / 100)
        fig.savefig(temp_file.name, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return temp_file.name

    def _cleanup_temp_file(self, filepath):
        try:
            if filepath and os.path.exists(filepath):
                os.unlink(filepath)
        except:
            pass

    def export_category_report(self, date_from, date_to, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Экспорт PDF отчета",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if not filename:
                return False

        try:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            expense_data = {}
            total_expense = 0

            for op in operations:
                if op.type.value == "expense":
                    op_date = op.operation_date
                    if hasattr(op_date, 'date'):
                        op_date = op_date.date()

                    from_date_val = date_from.date() if hasattr(date_from, 'date') else date_from
                    to_date_val = date_to.date() if hasattr(date_to, 'date') else date_to

                    if from_date_val <= op_date <= to_date_val:
                        expense_data[op.category] = expense_data.get(op.category, 0) + op.amount
                        total_expense += op.amount

            fig = plt.figure(figsize=(6, 5))
            ax = fig.add_subplot(111)

            if expense_data:
                categories = list(expense_data.keys())
                amounts = list(expense_data.values())
                ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title('Распределение расходов по категориям', fontsize=12, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Нет данных за выбранный период', ha='center', va='center', fontsize=12)
                ax.set_title('Расходы по категориям', fontsize=12, fontweight='bold')

            chart_path = self._create_chart_image(fig, 600, 500)

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()

            for style in styles.byName.values():
                style.fontName = RUSSIAN_FONT

            story = []

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2ecc71'),
                alignment=1,
                spaceAfter=20,
                fontName=RUSSIAN_FONT
            )

            title = Paragraph("Финансовый компас", title_style)
            story.append(title)
            story.append(Spacer(1, 12))

            from_str = date_from.strftime('%d.%m.%Y') if hasattr(date_from, 'strftime') else str(date_from)
            to_str = date_to.strftime('%d.%m.%Y') if hasattr(date_to, 'strftime') else str(date_to)

            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leading=14,
                fontName=RUSSIAN_FONT
            )

            info_text = f"""
            <b>Пользователь:</b> {self.current_user.username}<br/>
            <b>Период:</b> {from_str} - {to_str}<br/>
            <b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
            <b>Всего расходов:</b> {total_expense:,.2f} руб.
            """

            info = Paragraph(info_text, info_style)
            story.append(info)
            story.append(Spacer(1, 20))

            if chart_path:
                img = Image(chart_path, width=5 * inch, height=4 * inch)
                story.append(img)
                story.append(Spacer(1, 10))

            if expense_data:
                table_style = ParagraphStyle(
                    'TableStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    fontName=RUSSIAN_FONT
                )

                table_data = []
                table_data.append([Paragraph("Категория", table_style), Paragraph("Сумма (руб.)", table_style),
                                   Paragraph("Доля (%)", table_style)])
                for category, amount in sorted(expense_data.items(), key=lambda x: x[1], reverse=True):
                    percent = (amount / total_expense * 100) if total_expense > 0 else 0
                    table_data.append([Paragraph(category, table_style), Paragraph(f"{amount:,.2f}", table_style),
                                       Paragraph(f"{percent:.1f}%", table_style)])

                table_data.append(['', '', ''])
                table_data.append([Paragraph("ИТОГО:", table_style), Paragraph(f"{total_expense:,.2f}", table_style),
                                   Paragraph("100%", table_style)])

                table = Table(table_data, colWidths=[4 * inch, 2 * inch, 1.5 * inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), RUSSIAN_FONT),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -3), colors.HexColor('#f9f9f9')),
                    ('GRID', (0, 0), (-1, -3), 0.5, colors.HexColor('#cccccc')),
                    ('FONTNAME', (0, -1), (-1, -1), RUSSIAN_FONT),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f8f5')),
                    ('FONTSIZE', (0, -1), (-1, -1), 10),
                ]))
                story.append(table)

            doc.build(story)

            if chart_path:
                self._cleanup_temp_file(chart_path)

            messagebox.showinfo("Успех", "PDF-отчет сохранен")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {str(e)}")
            return False

    def export_trend_report(self, date_from, date_to, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Экспорт PDF отчета",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if not filename:
                return False

        try:
            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            from_date_val = date_from.date() if hasattr(date_from, 'date') else date_from
            to_date_val = date_to.date() if hasattr(date_to, 'date') else date_to

            monthly_data = {}
            for op in operations:
                op_date = op.operation_date
                if hasattr(op_date, 'date'):
                    op_date = op_date.date()

                if from_date_val <= op_date <= to_date_val:
                    key = op_date.strftime('%Y-%m')
                    if key not in monthly_data:
                        monthly_data[key] = {'income': 0, 'expense': 0, 'month_name': op_date.strftime('%B %Y')}
                    if op.type.value == "income":
                        monthly_data[key]['income'] += op.amount
                    else:
                        monthly_data[key]['expense'] += op.amount

            if not monthly_data:
                messagebox.showinfo("Информация", "Нет данных за выбранный период")
                return False

            months_labels = sorted(monthly_data.keys())
            month_names = [monthly_data[m]['month_name'] for m in months_labels]
            incomes = [monthly_data[m]['income'] for m in months_labels]
            expenses = [monthly_data[m]['expense'] for m in months_labels]

            fig, ax = plt.subplots(figsize=(10, 5))
            x_pos = range(len(months_labels))
            bar_width = 0.35

            bars1 = ax.bar([x - bar_width / 2 for x in x_pos], incomes, bar_width, label='Доходы', color='#2ecc71',
                           edgecolor='white')
            bars2 = ax.bar([x + bar_width / 2 for x in x_pos], expenses, bar_width, label='Расходы', color='#e74c3c',
                           edgecolor='white')

            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

            ax.set_xlabel('Месяцы', fontsize=10, fontweight='bold')
            ax.set_ylabel('Сумма (руб.)', fontsize=10, fontweight='bold')
            ax.set_title('Динамика доходов и расходов', fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(month_names, rotation=45, ha='right', fontsize=8)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')

            fig.tight_layout()

            chart_path = self._create_chart_image(fig, 1000, 500)

            doc = SimpleDocTemplate(filename, pagesize=landscape(A4), topMargin=1.5 * cm, bottomMargin=1.5 * cm)
            styles = getSampleStyleSheet()

            for style in styles.byName.values():
                style.fontName = RUSSIAN_FONT

            story = []

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2ecc71'),
                alignment=1,
                spaceAfter=15,
                fontName=RUSSIAN_FONT
            )

            title = Paragraph("Финансовый компас", title_style)
            story.append(title)

            from_str = date_from.strftime('%d.%m.%Y') if hasattr(date_from, 'strftime') else str(date_from)
            to_str = date_to.strftime('%d.%m.%Y') if hasattr(date_to, 'strftime') else str(date_to)

            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                leading=14,
                fontName=RUSSIAN_FONT
            )

            total_income = sum(incomes)
            total_expense = sum(expenses)
            balance = total_income - total_expense
            balance_color = '#2ecc71' if balance >= 0 else '#e74c3c'

            info_text = f"""
            <b>Пользователь:</b> {self.current_user.username}<br/>
            <b>Период:</b> {from_str} - {to_str}<br/>
            <b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
            <b>Всего доходов:</b> {total_income:,.2f} руб.<br/>
            <b>Всего расходов:</b> {total_expense:,.2f} руб.<br/>
            <b><font color='{balance_color}'>Баланс: {balance:+,.2f} руб.</font></b>
            """

            info = Paragraph(info_text, info_style)
            story.append(info)
            story.append(Spacer(1, 15))

            if chart_path:
                img = Image(chart_path, width=9 * inch, height=4.5 * inch)
                story.append(img)

            doc.build(story)

            if chart_path:
                self._cleanup_temp_file(chart_path)

            messagebox.showinfo("Успех", "PDF-отчет сохранен")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {str(e)}")
            return False

    def export_balance_report(self, date_from, date_to, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Экспорт PDF отчета",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            if not filename:
                return False

        try:
            initial = self.app.financial_calculator.get_initial_balance(self.current_user.id)
            operations = self.app.operation_service.get_user_operations(self.current_user.id)

            from_date_val = date_from.date() if hasattr(date_from, 'date') else date_from
            to_date_val = date_to.date() if hasattr(date_to, 'date') else date_to

            balance_data = []
            running_balance = initial
            current_date = from_date_val

            while current_date <= to_date_val:
                daily_income = 0
                daily_expense = 0

                for op in operations:
                    op_date = op.operation_date
                    if hasattr(op_date, 'date'):
                        op_date = op_date.date()

                    if op_date == current_date:
                        if op.type.value == "income":
                            daily_income += op.amount
                        else:
                            daily_expense += op.amount

                running_balance += daily_income - daily_expense
                balance_data.append({
                    'date': current_date,
                    'balance': running_balance
                })
                current_date += timedelta(days=1)

            if not balance_data:
                messagebox.showinfo("Информация", "Нет данных за выбранный период")
                return False

            step = max(1, len(balance_data) // 20)
            dates = [d['date'] for d in balance_data]
            balances = [d['balance'] for d in balance_data]

            fig, ax = plt.subplots(figsize=(10, 5))
            x_pos = range(len(balances))

            ax.plot(x_pos, balances, marker='o', markersize=3, linewidth=2, color='#2c3e50', label='Баланс')
            ax.fill_between(x_pos, 0, balances, where=[b >= 0 for b in balances], color='#2ecc71', alpha=0.3)
            ax.fill_between(x_pos, 0, balances, where=[b < 0 for b in balances], color='#e74c3c', alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)

            ax.set_xlabel('Дата', fontsize=10, fontweight='bold')
            ax.set_ylabel('Баланс (руб.)', fontsize=10, fontweight='bold')
            ax.set_title(
                f'Динамика остатка средств\n{from_date_val.strftime("%d.%m.%Y")} - {to_date_val.strftime("%d.%m.%Y")}',
                fontsize=11, fontweight='bold')

            visible_x = x_pos[::step]
            visible_dates = [dates[i].strftime('%d.%m') for i in range(0, len(dates), step)]
            ax.set_xticks(visible_x)
            ax.set_xticklabels(visible_dates, rotation=45, ha='right', fontsize=8)

            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper left', fontsize=9)

            fig.tight_layout()

            chart_path = self._create_chart_image(fig, 1000, 500)

            doc = SimpleDocTemplate(filename, pagesize=landscape(A4), topMargin=1.5 * cm, bottomMargin=1.5 * cm)
            styles = getSampleStyleSheet()

            for style in styles.byName.values():
                style.fontName = RUSSIAN_FONT

            story = []

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2ecc71'),
                alignment=1,
                spaceAfter=15,
                fontName=RUSSIAN_FONT
            )

            title = Paragraph("Финансовый компас", title_style)
            story.append(title)

            from_str = date_from.strftime('%d.%m.%Y') if hasattr(date_from, 'strftime') else str(date_from)
            to_str = date_to.strftime('%d.%m.%Y') if hasattr(date_to, 'strftime') else str(date_to)

            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                leading=14,
                fontName=RUSSIAN_FONT
            )

            start_balance = balances[0] if balances else 0
            end_balance = balances[-1] if balances else 0
            change = end_balance - start_balance
            change_percent = (change / abs(start_balance) * 100) if start_balance != 0 else 0
            max_balance = max(balances) if balances else 0
            min_balance = min(balances) if balances else 0

            info_text = f"""
            <b>Пользователь:</b> {self.current_user.username}<br/>
            <b>Период:</b> {from_str} - {to_str}<br/>
            <b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
            <b>Начальный баланс:</b> {start_balance:,.2f} руб.<br/>
            <b>Конечный баланс:</b> {end_balance:,.2f} руб.<br/>
            <b>Изменение:</b> {change:+,.2f} руб. ({change_percent:+.1f}%)<br/>
            <b>Максимум:</b> {max_balance:,.2f} руб.<br/>
            <b>Минимум:</b> {min_balance:,.2f} руб.
            """

            info = Paragraph(info_text, info_style)
            story.append(info)
            story.append(Spacer(1, 15))

            if chart_path:
                img = Image(chart_path, width=9 * inch, height=4.5 * inch)
                story.append(img)

            doc.build(story)

            if chart_path:
                self._cleanup_temp_file(chart_path)

            messagebox.showinfo("Успех", "PDF-отчет сохранен")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать PDF: {str(e)}")
            return False