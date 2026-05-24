import tkinter as tk
from tkinter import ttk


class AppStyles:
    @staticmethod
    def configure(style):
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Normal.TLabel', font=('Arial', 10), background='#f0f0f0')
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', font=('Arial', 10, 'bold'), foreground='green')
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'), foreground='red')

        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))