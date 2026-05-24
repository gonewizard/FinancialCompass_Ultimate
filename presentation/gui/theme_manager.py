import customtkinter as ctk


class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.current_color = "green"

    def apply_theme(self, theme: str = None, color: str = None):
        if theme:
            self.current_theme = theme
            ctk.set_appearance_mode(theme)
        if color:
            self.current_color = color
            ctk.set_default_color_theme(color)

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        ctk.set_appearance_mode(self.current_theme)
        return self.current_theme

    def get_theme(self):
        return self.current_theme

    def get_color(self):
        return self.current_color