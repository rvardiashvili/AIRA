import datetime
import math
import shutil
import subprocess

class DateTimer:
    @staticmethod
    def get_current_datetime():
        return datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")

class MathEvaluator:
    @staticmethod
    def calculate(expression):
        try:
            # Safe evaluation with limited scope
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            return str(eval(expression, {"__builtins__": None}, allowed_names))
        except Exception as e: return f"Math error: {e}"

class TimerTool:
    @staticmethod
    def set_timer(duration_seconds, message="Timer finished!"):
        try:
            # Use notify-send for Linux notifications
            if shutil.which("notify-send"):
                cmd = f"sleep {duration_seconds} && notify-send 'AIRA Timer' '{message}'"
                subprocess.Popen(cmd, shell=True)
                return f"Timer set for {duration_seconds} seconds."
            else:
                return "Error: 'notify-send' not found. Cannot set system timer."
        except Exception as e:
            return f"Timer failed: {e}"
