from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QLineEdit, QPushButton, QHBoxLayout, 
                             QApplication, QLabel, QScrollArea, QMenu, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QAction, QPainter, QBrush, QPalette, QDragEnterEvent, QDropEvent
import markdown
import uuid

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

class ChatWindow(QMainWindow):
    submit_signal = pyqtSignal(str)
    voice_signal = pyqtSignal()
    clear_signal = pyqtSignal()
    model_changed = pyqtSignal(str)
    persona_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIRA")
        self.setWindowIcon(QIcon("icons/aira.svg"))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedWidth(700)
        self.setFixedHeight(60)
        self.setAcceptDrops(True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)

        # Bar
        self.bar_widget = QWidget()
        self.input_layout = QHBoxLayout(self.bar_widget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("icons/aira.svg").pixmap(48, 48))
        self.input_layout.addWidget(self.icon_label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI...")
        self.input_field.returnPressed.connect(self.handle_submit)
        font = self.input_field.font()
        font.setPointSize(14)
        self.input_field.setFont(font)
        self.input_layout.addWidget(self.input_field)

        self.persona_button = QPushButton("👤")
        self.persona_button.setFixedSize(32, 32)
        self.persona_button.setFlat(True)
        self.persona_menu = QMenu(self.persona_button)
        self.persona_button.setMenu(self.persona_menu)
        self.populate_personas()
        self.input_layout.addWidget(self.persona_button)

        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.setFlat(True)
        self.settings_menu = QMenu(self.settings_button)
        self.settings_button.setMenu(self.settings_menu)
        self.input_layout.addWidget(self.settings_button)

        self.clear_button = QPushButton("⟳")
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setFlat(True)
        self.clear_button.clicked.connect(self.handle_clear)
        self.input_layout.addWidget(self.clear_button)

        self.main_layout.addWidget(self.bar_widget)

        # Scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVisible(False)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_container)
        self.main_layout.addWidget(self.scroll)

        self.current_ai_msg = None
        self.current_response_buffer = ""
        self.apply_styles()
        self.center_on_screen()

    def populate_personas(self):
        personas = {"Default": "DEFAULT", "Code Expert": "You are a code expert...", "Writer": "You are a creative writer...", "Concise": "Be extremely concise.", "Tutor": "Explain like I'm five."}
        for name, p in personas.items():
            action = QAction(name, self.persona_menu)
            action.triggered.connect(lambda checked, val=p: self.persona_changed.emit(val))
            self.persona_menu.addAction(action)

    def update_models(self, models, active_model):
        self.settings_menu.clear()
        for model in models:
            action = QAction(model, self.settings_menu)
            action.setCheckable(True); action.setChecked(model == active_model)
            action.triggered.connect(lambda checked, m=model: self.model_changed.emit(m))
            self.settings_menu.addAction(action)
        self.input_field.setPlaceholderText(f"Ask AI ({active_model})...")

    def handle_submit(self):
        text = self.input_field.text().strip()
        if text:
            self.scroll.setVisible(True); self.animate_expansion(True)
            self.add_message("You", text)
            self.submit_signal.emit(text); self.input_field.clear()
            self.current_ai_msg = None; self.current_response_buffer = ""

    def animate_expansion(self, expand):
        target = 550 if expand else 60
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(400); self.animation.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.animation.setStartValue(self.height()); self.animation.setEndValue(target)
        self.animation.valueChanged.connect(lambda val: self.setFixedHeight(val))
        self.animation.start()

    def add_message(self, sender, text, is_markdown=False):
        msg = MessageWidget(sender, text, is_markdown)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)
        self.scroll_to_bottom(); return msg

    def add_tool_block(self, name, result):
        block = ToolBlock(name, result)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, block)
        self.scroll_to_bottom()

    def append_chunk(self, text):
        if not self.current_ai_msg:
            line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("background-color: #4C566A; margin: 10px 0;")
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, line)
            self.current_ai_msg = self.add_message("AI", "")
        self.current_response_buffer += text
        self.current_ai_msg.content.setText(self.current_response_buffer)
        self.scroll_to_bottom()

    def finish_response(self, full_text):
        if self.current_ai_msg:
            html = markdown.markdown(full_text, extensions=['fenced_code', 'codehilite', 'nl2br'])
            self.current_ai_msg.content.setText(f"<div style='color:{QApplication.palette().color(QPalette.ColorRole.Text).name()}'>{html}</div>")
        self.current_ai_msg = None; self.current_response_buffer = ""
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        QApplication.processEvents()
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def handle_clear(self):
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0); 
            if item.widget(): item.widget().deleteLater()
        self.reset_window(); self.clear_signal.emit()
        self.show(); self.activateWindow(); self.input_field.setFocus()

    def reset_window(self): self.animate_expansion(False); self.scroll.setVisible(False)

    def toggle_visibility(self):
        if self.isVisible(): self.hide(); self.reset_window()
        else: self.show(); self.activateWindow(); self.input_field.setFocus(); self.center_on_screen()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
            self.reset_window()
        else:
            self.show()
            self.activateWindow()
            self.input_field.setFocus()
            self.center_on_screen()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.input_field.setText(f"Summarize this file: {path}")
            self.handle_submit()

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QApplication.palette().color(QPalette.ColorRole.Window); bg.setAlpha(240)
        painter.setBrush(QBrush(bg)); painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def apply_styles(self):
        self.setStyleSheet(f"QLineEdit {{ background: transparent; color: {QApplication.palette().color(QPalette.ColorRole.Text).name()}; border: none; }}")

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() // 3) - (self.height() // 2))

    def focusOutEvent(self, event): self.hide(); self.reset_window(); super().focusOutEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.hide(); self.reset_window()
        else: super().keyPressEvent(event)
