import sqlite3
import os
from datetime import datetime
from src.core.models import Session, Message

class HistoryManager:
    DATA_DIR = os.path.expanduser("~/.local/share/aira")
    DB_FILE = os.path.join(DATA_DIR, "chat_history.db")
    _current_session_id = None

    @staticmethod
    def _get_connection():
        conn = sqlite3.connect(HistoryManager.DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def initialize():
        if not os.path.exists(HistoryManager.DATA_DIR):
            os.makedirs(HistoryManager.DATA_DIR, exist_ok=True)
            
        with HistoryManager._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)

    @staticmethod
    def start_new_session(title="New Chat"):
        HistoryManager.initialize()
        session = Session.create(title)
        with HistoryManager._get_connection() as conn:
            conn.execute(
                "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (session.id, session.title, session.created_at, session.updated_at)
            )
        HistoryManager._current_session_id = session.id
        return session

    @staticmethod
    def get_current_session():
        HistoryManager.initialize()
        if not HistoryManager._current_session_id:
            # Try to get the most recent session
            sessions = HistoryManager.list_sessions()
            if sessions:
                HistoryManager._current_session_id = sessions[0].id
            else:
                return HistoryManager.start_new_session()
        
        return HistoryManager.load_session(HistoryManager._current_session_id)

    @staticmethod
    def load_session(session_id):
        HistoryManager.initialize()
        with HistoryManager._get_connection() as conn:
            s_row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if not s_row:
                return None
            
            messages_rows = conn.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,)).fetchall()
            messages = [Message(role=m["role"], content=m["content"], timestamp=m["timestamp"]) for m in messages_rows]
            
            session = Session(
                id=s_row["id"],
                title=s_row["title"],
                created_at=s_row["created_at"],
                updated_at=s_row["updated_at"],
                messages=messages
            )
            HistoryManager._current_session_id = session_id
            return session

    @staticmethod
    def add_message(role, content):
        if not HistoryManager._current_session_id:
            HistoryManager.start_new_session()
        
        sid = HistoryManager._current_session_id
        timestamp = datetime.now().isoformat()
        
        with HistoryManager._get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (sid, role, content, timestamp)
            )
            # Update session timestamp
            conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (timestamp, sid))
            
            # Auto-update title if it's the first user message and title is default
            if role == "user":
                current_session = HistoryManager.load_session(sid)
                if current_session and len(current_session.messages) <= 2: # user msg + potentially system msg
                     # Simple title generation: first 30 chars
                     new_title = content[:30] + "..." if len(content) > 30 else content
                     conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, sid))

    @staticmethod
    def list_sessions():
        HistoryManager.initialize()
        with HistoryManager._get_connection() as conn:
            rows = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
            return [Session(id=r["id"], title=r["title"], created_at=r["created_at"], updated_at=r["updated_at"]) for r in rows]

    @staticmethod
    def delete_session(session_id):
        with HistoryManager._get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        if HistoryManager._current_session_id == session_id:
            HistoryManager._current_session_id = None

    @staticmethod
    def clear():
        if os.path.exists(HistoryManager.DB_FILE):
            os.remove(HistoryManager.DB_FILE)
        HistoryManager._current_session_id = None
