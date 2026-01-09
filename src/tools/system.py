import shutil
import subprocess
import tempfile
import sys
import os
import psutil
import datetime
import platform
import pyperclip
import requests
import socket
import math

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

class UserInfo:
    @staticmethod
    def get_info():
        return f"User: {os.getlogin()}\nHost: {platform.node()}\nSystem: {platform.system()} {platform.release()} ({platform.machine()})"
