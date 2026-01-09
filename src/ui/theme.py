from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

class ThemeManager:
    THEMES = {
        "Dark": {
            "bg": "#2E3440",
            "fg": "#D8DEE9",
            "accent": "#88C0D0",
            "secondary": "#3B4252",
            "text": "#ECEFF4",
            "icon": "#ECEFF4"
        },
        "Light": {
            "bg": "#ECEFF4",
            "fg": "#2E3440",
            "accent": "#5E81AC",
            "secondary": "#D8DEE9",
            "text": "#2E3440",
            "icon": "#2E3440"
        },
        "Nord": {
            "bg": "#2E3440",
            "fg": "#D8DEE9",
            "accent": "#81A1C1",
            "secondary": "#3B4252",
            "text": "#ECEFF4",
            "icon": "#ECEFF4"
        }
    }

    @staticmethod
    def get_icon_color(theme_name):
        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Dark"])
        return theme.get("icon", "#ECEFF4")

    @staticmethod
    def apply_theme(app, theme_name):
        if theme_name == "System":
            app.setPalette(app.style().standardPalette())
            return

        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Dark"])
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["bg"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["fg"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme["secondary"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["bg"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme["text"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme["fg"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme["secondary"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["fg"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["accent"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["bg"]))
        app.setPalette(palette)

    @staticmethod
    def get_style(theme_name):
        if theme_name == "System":
            return ""
        
        theme = ThemeManager.THEMES.get(theme_name, ThemeManager.THEMES["Dark"])
        return f"""
            QMainWindow, QDialog {{
                background-color: {theme["bg"]};
                color: {theme["fg"]};
            }}
            QLabel {{
                color: {theme["fg"]};
            }}
            QLineEdit, QTextEdit, QListWidget, QComboBox, QScrollArea {{
                background-color: {theme["secondary"]};
                color: {theme["text"]};
                border: 1px solid {theme["accent"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme["secondary"]};
                color: {theme["fg"]};
                border: 1px solid {theme["accent"]};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {theme["accent"]};
                color: {theme["bg"]};
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["accent"]};
            }}
            QTabBar::tab {{
                background: {theme["secondary"]};
                color: {theme["fg"]};
                padding: 8px 20px;
            }}
            QTabBar::tab:selected {{
                background: {theme["accent"]};
                color: {theme["bg"]};
            }}
        """
