from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

@dataclass
class Message:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return {"role": self.role, "content": self.content}

@dataclass
class Session:
    id: str
    title: str = "New Chat"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    messages: list[Message] = field(default_factory=list)

    @staticmethod
    def create(title="New Chat"):
        return Session(id=str(uuid.uuid4()), title=title)
    
    def add_message(self, role, content):
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = datetime.now().isoformat()
        return msg
