import os
import datetime
from pypdf import PdfReader

class DocumentParser:
    @staticmethod
    def parse_pdf(path):
        try:
            reader = PdfReader(path)
            text = "\n".join([p.extract_text() for p in reader.pages[:10]])
            return f"PDF ({path}):\n{text[:2000]}..."
        except Exception as e:
            return f"PDF failed: {str(e)}"

class FileReader:
    @staticmethod
    def read_file(path, max_lines=100):
        try:
            p = os.path.expanduser(path) if path.startswith("~") else path
            if not os.path.exists(p): return f"File not found: {path}"
            if p.lower().endswith(".pdf"): return DocumentParser.parse_pdf(p)
            with open(p, 'r', errors='replace') as f:
                content = "".join(f.readlines()[:max_lines])
            return f"File ({path}):\n{content}"
        except Exception as e:
            return f"Read failed: {str(e)}"

class CalendarReader:
    @staticmethod
    def get_agenda():
        try:
            now = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M")
            output = f"Current Time: {now}\n"
            data_dir = os.path.expanduser("~/.local/share/aira")
            agenda_path = os.path.join(data_dir, "agenda.txt")
            
            paths = [agenda_path, "agenda.txt", os.path.expanduser("~/agenda.txt")]
            for p in paths:
                if os.path.exists(p):
                    with open(p, "r") as f:
                        output += f"\nYour Agenda:\n{f.read()[:500]}"
                        return output
            return output + "(No agenda.txt found.)"
        except Exception as e:
            return f"Calendar check failed: {str(e)}"

class NoteTaker:
    @staticmethod
    def add_note(content, filename=None):
        try:
            data_dir = os.path.expanduser("~/.local/share/aira")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
            if filename is None:
                filename = os.path.join(data_dir, "agenda.txt")
                
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = f"\n- [{timestamp}] {content}"
            with open(filename, "a") as f:
                f.write(entry)
            return f"Note added to {filename}."
        except Exception as e:
            return f"Failed to add note: {e}"
