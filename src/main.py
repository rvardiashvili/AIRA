import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from pynput import keyboard

from src.ui.window import ChatWindow
from src.ui.theme import ThemeManager
from src.core.worker import OllamaWorker
from src.tools import AppLauncher, DiskIndexer
from src.core.config import Config
from src.core.history import HistoryManager

class HotkeySignal(QObject):
    triggered = pyqtSignal()

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Config
        self.config = Config.load()
        
        # Apply Theme
        ThemeManager.apply_theme(self.app, self.config.get("theme", "System"))
        
        # GUI
        self.window = ChatWindow()
        self.window.setStyleSheet(ThemeManager.get_style(self.config.get("theme", "System")))
        
        # Workers
        self.ollama_worker = OllamaWorker(model=self.config.get("last_model", "llama3.2"))
        
        # Load History into UI
        self.window.load_history(self.ollama_worker.history)
        
        # Populate models initially
        self.fetch_models()
        
        # Signals
        self.window.submit_signal.connect(self.handle_submit)
        self.window.clear_signal.connect(self.handle_clear_session)
        self.window.model_changed.connect(self.handle_model_change)
        self.window.persona_changed.connect(self.handle_persona_change)
        self.window.session_changed.connect(self.reload_session)
        
        self.ollama_worker.response_received.connect(self.window.append_chunk)
        self.ollama_worker.finished_streaming.connect(self.handle_ollama_finished)
        self.ollama_worker.error_occurred.connect(self.handle_error)
        self.ollama_worker.command_triggered.connect(self.handle_command)
        
        # Tool Signals (including Memory Retrieval/Storage)
        self.ollama_worker.tool_started.connect(lambda name: None) 
        self.ollama_worker.tool_finished.connect(self.window.add_tool_block)
        
        # Global Hotkeys
        self.hotkey_signal = HotkeySignal()
        self.hotkey_signal.triggered.connect(self.window.toggle_visibility)
        self.setup_hotkeys()

        # System Tray
        self.setup_tray()

    def fetch_models(self):
        models = self.ollama_worker.get_available_models()
        active = self.config.get("last_model", "llama3.2")
        self.window.update_models(models, active)

    def handle_model_change(self, model_name):
        self.config["last_model"] = model_name
        Config.save(self.config)
        self.ollama_worker.set_model(model_name)
        # Refresh menu to show checkmark
        self.fetch_models()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(QIcon("icons/aira.svg"), self.app) 
        menu = QMenu()
        show_action = menu.addAction("Show/Hide")
        show_action.triggered.connect(self.window.toggle_visibility)
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.app.quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def setup_hotkeys(self):
        self.hotkey_listener = keyboard.GlobalHotKeys({'<cmd>+<space>': self.on_hotkey})
        self.hotkey_listener.start()

    def on_hotkey(self):
        self.hotkey_signal.triggered.emit()

    def handle_submit(self, text):
        if self.ollama_worker.isRunning():
            self.ollama_worker.stop()
        self.ollama_worker.set_prompt(text)
        self.ollama_worker.start()

    def handle_ollama_finished(self):
        self.window.finish_response(self.window.current_response_buffer)

    def handle_persona_change(self, prompt_text):
        if prompt_text == "DEFAULT":
            self.ollama_worker.set_system_prompt(self.ollama_worker.default_system_prompt)
            self.window.add_message("System", "Switched to Default Assistant.")
        else:
            self.ollama_worker.set_system_prompt(prompt_text)
            self.window.add_message("System", "Persona updated.")

    def handle_clear_session(self):
        self.ollama_worker.clear_history()

    def reload_session(self, session_id):
        self.ollama_worker.reload_history()
        self.window.chat_layout_clear() 
        self.window.load_history(self.ollama_worker.history)
        self.window.add_message("System", f"Resumed session {session_id[:8]}...")

    def handle_error(self, error_msg):
        self.window.add_message("Error", error_msg)

    def handle_command(self, cmd_type, value):
        if cmd_type == "OPEN":
            self.window.add_message("System", f"Opening {value}...")
            AppLauncher.open_app(value)
            self.window.hide() 
            self.window.reset_window()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()