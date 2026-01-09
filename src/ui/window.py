from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QLineEdit, QPushButton, QHBoxLayout, 
                             QApplication, QLabel, QScrollArea, QMenu, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QAction, QPainter, QBrush, QPalette, QDragEnterEvent, QDropEvent
import markdown
import uuid
from src.ui.widgets import ToolBlock, MessageWidget
from src.ui.settings_window import SettingsWindow
from src.ui.theme import ThemeManager
from src.core.config import Config
from src.core.models import Message

class ChatWindow(QMainWindow):
    submit_signal = pyqtSignal(str)
    voice_signal = pyqtSignal() # Kept for potential future use or signal compatibility
    clear_signal = pyqtSignal()
    model_changed = pyqtSignal(str)
    persona_changed = pyqtSignal(str)
    session_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = Config.load()
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

        self.persona_button = QPushButton()
        self.persona_button.setIcon(QIcon("icons/persona.svg"))
        self.persona_button.setIconSize(QSize(24, 24))
        self.persona_button.setFixedSize(32, 32)
        self.persona_button.setFlat(True)
        self.persona_menu = QMenu(self.persona_button)
        self.persona_button.setMenu(self.persona_menu)
        self.populate_personas()
        self.input_layout.addWidget(self.persona_button)

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon("icons/settings.svg"))
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.setFlat(True)
        self.settings_button.clicked.connect(self.open_settings)
        self.input_layout.addWidget(self.settings_button)

        self.clear_button = QPushButton()
        self.clear_button.setIcon(QIcon("icons/clear.svg"))
        self.clear_button.setIconSize(QSize(24, 24))
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

        self.settings_window = None

    def open_settings(self):
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
            self.settings_window.settings_changed.connect(self.reload_config)
            self.settings_window.session_selected.connect(self.session_changed.emit)
        self.settings_window.show()

    def reload_config(self):
        self.config = Config.load()
        self.populate_personas()
        # Apply theme style live
        self.setStyleSheet(ThemeManager.get_style(self.config.get("theme", "System")))

    def update_models(self, models, active_model):
        self.models = models # Store for menu population
        self.active_model = active_model
        self.input_field.setPlaceholderText(f"Ask AI ({active_model})...")
        self.populate_personas() # Refresh menu to include models

    def populate_personas(self):
        self.persona_menu.clear()
        
        # Personas Section
        personas = self.config.get("personas", {})
        for name, prompt in personas.items():
            action = QAction(name, self.persona_menu)
            action.triggered.connect(lambda checked, val=prompt: self.persona_changed.emit(val))
            self.persona_menu.addAction(action)
            
        self.persona_menu.addSeparator()
        
        # Models Section (Submenu)
        model_menu = self.persona_menu.addMenu("Models")
        if hasattr(self, 'models'):
            for model in self.models:
                action = QAction(model, model_menu)
                action.setCheckable(True)
                action.setChecked(model == self.active_model)
                action.triggered.connect(lambda checked, m=model: self.model_changed.emit(m))
                model_menu.addAction(action)

    def load_history(self, history):
        if not history: return
        self.scroll.setVisible(True)
        self.animate_expansion(True)
        
        # Add visual separator for new session
        # self.chat_layout.addWidget(QLabel("--- Previous Session ---"))
        
        for msg in history:
            role = msg.role
            content = msg.content
            if not content: continue
            
            if role == 'user':
                self.add_message("You", content)
            elif role == 'assistant':
                # Render full markdown for assistant messages immediately
                ui_msg = self.add_message("AI", "")
                html = markdown.markdown(content, extensions=['fenced_code', 'codehilite', 'nl2br'])
                ui_msg.content.setText(f"<div style='color:{QApplication.palette().color(QPalette.ColorRole.Text).name()}'>{html}</div>")
            elif role == 'tool':
                # Optionally restore tool outputs? For now, skip to keep cleaner
                pass

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
        self.animation.setDuration(150) # Faster animation
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuart)
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
        
        # Render Markdown incrementally
        html = markdown.markdown(self.current_response_buffer, extensions=['fenced_code', 'codehilite', 'nl2br'])
        self.current_ai_msg.content.setText(f"<div style='color:{QApplication.palette().color(QPalette.ColorRole.Text).name()}'>{html}</div>")
        
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

    def chat_layout_clear(self):
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0); 
            if item.widget(): item.widget().deleteLater()

    def handle_clear(self):
        self.chat_layout_clear()
        self.reset_window(); self.clear_signal.emit()
        self.show(); self.activateWindow(); self.input_field.setFocus()

    def reset_window(self): self.animate_expansion(False); self.scroll.setVisible(False)

    def toggle_visibility(self):
        if self.isVisible(): self.hide(); self.reset_window()
        else: self.show(); self.activateWindow(); self.input_field.setFocus(); self.center_on_screen()

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