import subprocess
import shutil
import os
import webbrowser
import tempfile
import sys
import datetime
import requests
import psutil
import platform
import ollama
import numpy as np
import pickle
import importlib.util
import pyperclip
import socket
import math
from pypdf import PdfReader
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

class AppLauncher:
    @staticmethod
    def is_available(app_name):
        return shutil.which(app_name) is not None

    @staticmethod
    def open_app(app_name):
        if not AppLauncher.is_available(app_name):
            return False, f"Application '{app_name}' not found in PATH."
        try:
            subprocess.Popen([app_name], start_new_session=True)
            return True, f"Launching {app_name}..."
        except Exception as e:
            return False, f"Failed to launch {app_name}: {str(e)}"

class WebSearch:
    @staticmethod
    def search(query):
        try:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return True, f"Opening browser for: {query}"
        except Exception as e:
            return False, f"Failed to open browser: {str(e)}"

class DDGSearch:
    @staticmethod
    def text_search(query, max_results=3):
        try:
            results = DDGS().text(query, max_results=max_results)
            if not results: return "No results found."
            formatted = [f"- [{r.get('title')}]({r.get('href')}): {r.get('body')}" for r in results]
            return "\n".join(formatted)
        except Exception as e:
            return f"Search failed: {str(e)}"

class WeatherFetcher:
    @staticmethod
    def get_weather(location):
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url).json()
            if not geo_res.get("results"): return f"Location '{location}' not found."
            lat, lon, name = geo_res["results"][0]["latitude"], geo_res["results"][0]["longitude"], geo_res["results"][0]["name"]
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m"
            w_res = requests.get(weather_url).json()
            current = w_res.get("current", {})
            temp, wind, code = current.get("temperature_2m"), current.get("wind_speed_10m"), current.get("weather_code")
            conditions = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Rime fog", 51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense", 61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy", 71: "Snow: Slight", 73: "Snow: Moderate", 75: "Snow: Heavy", 95: "Thunderstorm"}
            return f"Weather in {name}: {temp}°C, {conditions.get(code, 'Unknown')}, Wind: {wind} km/h."
        except Exception as e:
            return f"Weather fetch failed: {str(e)}"

class DateTimer:
    @staticmethod
    def get_current_datetime():
        return datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")

class CalendarReader:
    @staticmethod
    def get_agenda():
        try:
            now = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M")
            output = f"Current Time: {now}\n"
            for p in ["agenda.txt", os.path.expanduser("~/agenda.txt")]:
                if os.path.exists(p):
                    with open(p, "r") as f:
                        output += f"\nYour Agenda:\n{f.read()[:500]}"
                        return output
            return output + "(No agenda.txt found.)"
        except Exception as e:
            return f"Calendar check failed: {str(e)}"

class SystemStats:
    @staticmethod
    def get_stats():
        try:
            cpu, ram, disk = psutil.cpu_percent(interval=0.1), psutil.virtual_memory().percent, psutil.disk_usage('/').percent
            uptime = datetime.timedelta(seconds=int(datetime.datetime.now().timestamp() - psutil.boot_time()))
            return f"OS: {platform.system()} {platform.release()}\nCPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%\nUptime: {uptime}"
        except Exception as e:
            return f"Stats failed: {str(e)}"

class ProcessManager:
    @staticmethod
    def list_processes(limit=5):
        try:
            procs = sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), key=lambda p: p.info['memory_percent'], reverse=True)[:limit]
            return "\n".join([f"PID: {p.info['pid']} | {p.info['name']} | Mem: {p.info['memory_percent']:.1f}%" for p in procs])
        except Exception as e: return f"List failed: {e}"

    @staticmethod
    def kill_process(identifier):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if str(proc.info['pid']) == str(identifier) or proc.info['name'] == identifier:
                    proc.kill()
                    return f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})"
            return f"Process '{identifier}' not found."
        except Exception as e: return f"Kill failed: {e}"

class ClipboardTool:
    @staticmethod
    def get_text():
        try: return pyperclip.paste() or "Clipboard is empty."
        except Exception as e: return f"Clipboard read error: {e}"
    
    @staticmethod
    def set_text(text):
        try: 
            pyperclip.copy(text)
            return "Text copied to clipboard."
        except Exception as e: return f"Clipboard write error: {e}"

class NetworkInfo:
    @staticmethod
    def get_ip_info():
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            public_ip = requests.get('https://api.ipify.org', timeout=3).text
            return f"Hostname: {hostname}\nLocal IP: {local_ip}\nPublic IP: {public_ip}"
        except Exception as e: return f"Network info error: {e}"

class MathEvaluator:
    @staticmethod
    def calculate(expression):
        try:
            # Safe evaluation with limited scope
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            return str(eval(expression, {"__builtins__": None}, allowed_names))
        except Exception as e: return f"Math error: {e}"

class UserInfo:
    @staticmethod
    def get_info():
        return f"User: {os.getlogin()}\nHost: {platform.node()}\nSystem: {platform.system()} {platform.release()} ({platform.machine()})"

class SystemControl:
    @staticmethod
    def execute_control(command):
        cmd = command.lower()
        if "volume" in cmd:
            if "+" in cmd or "up" in cmd: subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%+"], capture_output=True)
            elif "-" in cmd or "down" in cmd: subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "5%-"], capture_output=True)
            elif "mute" in cmd: subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"], capture_output=True)
            return f"Volume adjusted: {command}"
        if "brightness" in cmd:
            if "+" in cmd or "up" in cmd: subprocess.run(["brightnessctl", "s", "+10%"], capture_output=True)
            elif "-" in cmd or "down" in cmd: subprocess.run(["brightnessctl", "s", "10%-"], capture_output=True)
            return f"Brightness adjusted: {command}"
        return f"Command '{command}' not recognized."

class MediaController:
    @staticmethod
    def control(action):
        if not shutil.which("playerctl"): return "Error: 'playerctl' missing."
        try:
            if action.lower() in ["play", "pause", "play-pause", "next", "previous", "stop"]:
                subprocess.run(["playerctl", action.lower()], check=True)
                return f"Media: {action}"
            return f"Unknown action: {action}"
        except Exception as e:
            return f"Media failed: {str(e)}"

class ShellExecutor:
    @staticmethod
    def run_command(command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            return result.stdout + (f"\nError:\n{result.stderr}" if result.stderr else "")
        except Exception as e:
            return f"Shell failed: {str(e)}"

class CodeExecutor:
    @staticmethod
    def execute(code):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                tmp.write(code)
                path = tmp.name
            result = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=10)
            os.remove(path)
            return True, result.stdout + (f"\n[Stderr]:\n{result.stderr}" if result.stderr else "")
        except Exception as e:
            return False, f"Code failed: {str(e)}"

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

class WebScraper:
    @staticmethod
    def scrape(url):
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for s in soup(["script", "style"]): s.decompose()
            text = "\n".join([l.strip() for l in soup.get_text(separator='\n').splitlines() if l.strip()])
            return f"Scraped {url}:\n{text[:2000]}..."
        except Exception as e:
            return f"Scrape failed: {str(e)}"

class ScreenReader:
    @staticmethod
    def take_screenshot():
        tmp_fd, path = tempfile.mkstemp(suffix='.png'); os.close(tmp_fd)
        for cmd in [["grim", path], ["spectacle", "-b", "-n", "-o", path], ["gnome-screenshot", "-f", path], ["scrot", path]]:
            if shutil.which(cmd[0]):
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    if os.path.exists(path) and os.path.getsize(path) > 0: return path
                except: continue
        return "ERROR: No screenshot tool."

class VectorStore:
    DB = "knowledge_base/vector_db.pkl"
    MODEL = "all-minilm"
    def __init__(self):
        self.data = []
        if os.path.exists(self.DB):
            try:
                with open(self.DB, 'rb') as f: self.data = pickle.load(f)
            except: pass
    def save(self):
        os.makedirs("knowledge_base", exist_ok=True)
        with open(self.DB, 'wb') as f: pickle.dump(self.data, f)
    def add_text(self, text):
        if not text.strip(): return
        try:
            v = np.array(ollama.embeddings(model=self.MODEL, prompt=text)['embedding'])
            self.data.append({'text': text, 'vector': v}); self.save()
        except: pass
    def query(self, text, top_k=3):
        if not self.data: return []
        try:
            qv = np.array(ollama.embeddings(model=self.MODEL, prompt=text)['embedding'])
            sims = [np.dot(qv, i['vector'])/(np.linalg.norm(qv)*np.linalg.norm(i['vector'])) for i in self.data]
            idx = np.argsort(sims)[-top_k:][::-1]
            return [self.data[i]['text'] for i in idx if sims[i] > 0.4]
        except: return []

    def clear(self):
        """Clears the entire database."""
        self.data = []
        if os.path.exists(self.DB):
            os.remove(self.DB)

class KnowledgeBase:
    _store = None
    @staticmethod
    def get_store():
        if not KnowledgeBase._store: KnowledgeBase._store = VectorStore()
        return KnowledgeBase._store
    @staticmethod
    def auto_index(text): KnowledgeBase.get_store().add_text(text)
    @staticmethod
    def get_context(query):
        results = KnowledgeBase.get_store().query(query)
        if not results: return ""
        return "\n--- RELEVANT CONTEXT ---\n" + "\n".join(results) + "\n------------------------\n"
    @staticmethod
    def clear():
        """Public method to clear memory."""
        KnowledgeBase.get_store().clear()

class PluginManager:
    @staticmethod
    def load_plugins():
        """Placeholder for dynamic plugin loading logic."""
        return []
