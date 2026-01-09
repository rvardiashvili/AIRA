from PyQt6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QTextEdit, QPushButton, QListWidget, 
                             QTabWidget, QComboBox, QMessageBox, QFormLayout, QFrame, QApplication, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor
from src.core.config import Config
from src.core.memory import KnowledgeBase
from src.core.history import HistoryManager
from src.ui.theme import ThemeManager
import getpass

class SettingsWindow(QDialog):
    settings_changed = pyqtSignal()
    session_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Control Panel")
        self.setFixedSize(700, 550)
        self.setWindowIcon(QIcon("icons/aira.svg"))
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.config = Config.load()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Title
        title_lbl = QLabel("AIRA Settings")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(title_lbl)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.init_general_tab()
        self.init_personas_tab()
        self.init_profile_tab()
        self.init_chat_history_tab()
        self.init_memory_tab()
        
        # Footer
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        
        self.save_btn = QPushButton("Save & Apply")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("background-color: #5E81AC; color: white; border: none;")
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)

        # Apply current theme style
        self.update_style()

    def update_style(self):
        self.setStyleSheet(ThemeManager.get_style(self.config.get("theme", "System")))

    def init_general_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Dark", "Light", "Nord"])
        self.theme_combo.setCurrentText(self.config.get("theme", "System"))
        
        lbl = QLabel("Theme:")
        layout.addRow(lbl, self.theme_combo)
        
        self.tabs.addTab(tab, "General")

    def init_personas_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Left: List
        left_layout = QVBoxLayout()
        self.persona_list = QListWidget()
        self.persona_list.addItems(self.config.get("personas", {}).keys())
        self.persona_list.currentItemChanged.connect(self.load_persona)
        left_layout.addWidget(QLabel("Available Personas:"))
        left_layout.addWidget(self.persona_list)
        
        # Right: Edit
        right_layout = QVBoxLayout()
        self.p_name = QLineEdit()
        self.p_name.setPlaceholderText("Persona Name (e.g. 'Coder')")
        
        self.p_prompt = QTextEdit()
        self.p_prompt.setPlaceholderText("System Prompt (e.g. 'You are an expert...')")
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Update / Add")
        add_btn.clicked.connect(self.add_persona)
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background-color: #BF616A;")
        del_btn.clicked.connect(self.delete_persona)
        btn_layout.addWidget(del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(add_btn)
        
        right_layout.addWidget(QLabel("Name:"))
        right_layout.addWidget(self.p_name)
        right_layout.addWidget(QLabel("System Prompt:"))
        right_layout.addWidget(self.p_prompt)
        right_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        self.tabs.addTab(tab, "Personas")

    def init_profile_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        profile = self.config.get("user_profile", {})
        if not profile.get("name"): profile["name"] = getpass.getuser()
        
        self.u_name = QLineEdit(profile.get("name", ""))
        self.u_role = QLineEdit(profile.get("role", ""))
        self.u_role.setPlaceholderText("e.g. Senior Developer")
        self.u_interests = QTextEdit(profile.get("interests", ""))
        self.u_interests.setPlaceholderText("e.g. Python, AI, Sci-Fi")
        self.u_interests.setMaximumHeight(100)
        
        layout.addRow("Your Name:", self.u_name)
        layout.addRow("Role / Job:", self.u_role)
        layout.addRow("Interests:", self.u_interests)
        
        self.tabs.addTab(tab, "User Profile")

    def init_chat_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.refresh_history_list()
        
        btn_layout = QHBoxLayout()
        resume_btn = QPushButton("Resume Chat")
        resume_btn.setStyleSheet("background-color: #A3BE8C; color: #2E3440;")
        resume_btn.clicked.connect(self.resume_selected_session)
        
        del_hist_btn = QPushButton("Delete Chat")
        del_hist_btn.setStyleSheet("background-color: #BF616A;")
        del_hist_btn.clicked.connect(self.delete_selected_session)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_history_list)
        
        btn_layout.addWidget(del_hist_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(resume_btn)
        
        layout.addWidget(QLabel("Previous Conversations:"))
        layout.addWidget(self.history_list)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "History")

    def init_memory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        top_bar = QHBoxLayout()
        self.mem_count_lbl = QLabel("Total Memories: 0")
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_memory_list)
        top_bar.addWidget(self.mem_count_lbl)
        top_bar.addStretch()
        top_bar.addWidget(refresh_btn)
        
        self.mem_list = QListWidget()
        self.mem_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        
        btn_layout = QHBoxLayout()
        del_mem_btn = QPushButton("Delete Selected")
        del_mem_btn.clicked.connect(self.delete_memory)
        clear_all_btn = QPushButton("Wipe Database")
        clear_all_btn.setStyleSheet("background-color: #BF616A; color: white;")
        clear_all_btn.clicked.connect(self.clear_all_memory)
        
        btn_layout.addWidget(del_mem_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_all_btn)
        
        layout.addLayout(top_bar)
        layout.addWidget(self.mem_list)
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "RAG Memory")
        self.refresh_memory_list()

    # --- Personas Logic ---
    def load_persona(self, item):
        if not item: return
        name = item.text()
        prompt = self.config["personas"].get(name, "")
        self.p_name.setText(name)
        self.p_prompt.setText(prompt)

    def add_persona(self):
        name = self.p_name.text().strip()
        prompt = self.p_prompt.toPlainText().strip()
        if not name or not prompt:
            QMessageBox.warning(self, "Error", "Name and Prompt cannot be empty.")
            return

        self.config["personas"][name] = prompt
        
        # Update list if new
        items = self.persona_list.findItems(name, Qt.MatchFlag.MatchExactly)
        if not items:
            self.persona_list.addItem(name)
        
        self.p_name.clear()
        self.p_prompt.clear()
        QMessageBox.information(self, "Success", f"Persona '{name}' saved.")

    def delete_persona(self):
        item = self.persona_list.currentItem()
        if not item: return
        
        name = item.text()
        if name == "Default":
            QMessageBox.warning(self, "Error", "Cannot delete the Default persona.")
            return

        confirm = QMessageBox.question(self, "Confirm", f"Delete persona '{name}'?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            del self.config["personas"][name]
            self.persona_list.takeItem(self.persona_list.row(item))
            self.p_name.clear()
            self.p_prompt.clear()

    # --- History Logic ---
    def refresh_history_list(self):
        self.history_list.clear()
        sessions = HistoryManager.list_sessions()
        for sess in sessions:
            # Format: [timestamp] title
            timestamp = sess.updated_at[:16].replace('T', ' ')
            item_text = f"[{timestamp}] {sess.title}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, sess.id)
            self.history_list.addItem(item)

    def resume_selected_session(self):
        item = self.history_list.currentItem()
        if not item: return
        sid = item.data(Qt.ItemDataRole.UserRole)
        if HistoryManager.load_session(sid):
            self.session_selected.emit(sid)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to load session.")

    def delete_selected_session(self):
        item = self.history_list.currentItem()
        if not item: return
        sid = item.data(Qt.ItemDataRole.UserRole)
        
        if QMessageBox.question(self, "Confirm", "Delete this conversation history?", 
                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            HistoryManager.delete_session(sid)
            self.refresh_history_list()

    # --- Memory Logic ---
    def refresh_memory_list(self):
        self.mem_list.clear()
        memories = KnowledgeBase.get_all_memories()
        self.mem_count_lbl.setText(f"Total Memories: {len(memories)}")
        for i, mem in enumerate(memories):
            snippet = (mem[:80] + '...') if len(mem) > 80 else mem
            self.mem_list.addItem(f"[{i}] {snippet}")

    def delete_memory(self):
        selected_items = self.mem_list.selectedItems()
        if not selected_items: return
        
        indices = []
        for item in selected_items:
            try:
                idx = int(item.text().split(']')[0].replace('[', ''))
                indices.append(idx)
            except:
                pass
        
        indices.sort(reverse=True)
        for idx in indices:
            KnowledgeBase.delete_memory(idx)
            
        self.refresh_memory_list()

    def clear_all_memory(self):
        confirm = QMessageBox.question(self, "Danger", "Are you sure you want to permanently wipe ALL long-term memory?\nThis cannot be undone.", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            KnowledgeBase.clear()
            self.refresh_memory_list()

    def save_settings(self):
        # General
        self.config["theme"] = self.theme_combo.currentText()
        
        # Profile
        self.config["user_profile"] = {
            "name": self.u_name.text(),
            "role": self.u_role.text(),
            "interests": self.u_interests.toPlainText()
        }
        
        Config.save(self.config)
        
        # Apply theme immediately to the whole app
        ThemeManager.apply_theme(QApplication.instance(), self.config["theme"])
        
        # Notify main controller
        self.settings_changed.emit()
        self.accept()