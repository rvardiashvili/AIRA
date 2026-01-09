from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QLabel, QApplication, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
import markdown

class ToolBlock(QFrame):
    def __init__(self, name, result, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 2, 10, 2)
        self.layout.setSpacing(5)
        
        icon = "🧠" if "Memory" in name else "🔍"
        self.btn = QPushButton(f"  {icon} {name}  ")
        self.btn.setCheckable(True)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.toggle_details)
        
        self.details = QLabel(str(result))
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details.setVisible(False)
        
        self.apply_styles()
        self.layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.details)

    def apply_styles(self):
        palette = QApplication.palette()
        highlight = palette.color(QPalette.ColorRole.Highlight).name()
        base = palette.color(QPalette.ColorRole.Base).name()
        text = palette.color(QPalette.ColorRole.Text).name()
        
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4C566A;
                color: #ECEFF4;
                border-radius: 12px;
                padding: 5px 15px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid {highlight};
            }}
            QPushButton:checked {{ background-color: {highlight}; color: white; }}
            QPushButton:hover {{ background-color: {highlight}; border: 1px solid white; }}
        """)
        
        self.details.setStyleSheet(f"""
            QLabel {{
                background-color: {base};
                color: {text};
                border: 1px dashed {highlight};
                border-radius: 8px;
                padding: 12px;
                font-family: monospace;
                font-size: 11px;
            }}
        """)

    def toggle_details(self):
        self.details.setVisible(self.btn.isChecked())

class MessageWidget(QWidget):
    def __init__(self, sender, text, is_markdown=False, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        palette = QApplication.palette()
        color = palette.color(QPalette.ColorRole.Highlight).name() if sender == "You" else palette.color(QPalette.ColorRole.Link).name()
        
        self.label = QLabel(f"<b style='color:{color}'>{sender}:</b>")
        self.content = QLabel()
        self.content.setWordWrap(True)
        self.content.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_markdown:
            html = markdown.markdown(text, extensions=['fenced_code', 'codehilite', 'nl2br'])
            self.content.setText(f"<div style='color:{palette.color(QPalette.ColorRole.Text).name()}'>{html}</div>")
        else:
            self.content.setText(text)
            
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.content)
