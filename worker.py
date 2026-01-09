import ollama
import re
import json
from PyQt6.QtCore import QThread, pyqtSignal
from tools import (DDGSearch, WeatherFetcher, CalendarReader, 
                   FileReader, ScreenReader, SystemStats, SystemControl, ShellExecutor, 
                   AppLauncher, CodeExecutor, WebScraper, MediaController, KnowledgeBase,
                   ClipboardTool, ProcessManager, NetworkInfo, MathEvaluator, UserInfo, DateTimer)

class OllamaWorker(QThread):
    response_received = pyqtSignal(str)
    finished_streaming = pyqtSignal()
    error_occurred = pyqtSignal(str)
    command_triggered = pyqtSignal(str, str) # type, value
    tool_started = pyqtSignal(str) # name
    tool_finished = pyqtSignal(str, str) # name, result

    def __init__(self, model="llama3.2"):
        super().__init__()
        self.model = model
        self.prompt = ""
        self.history = []
        self._abort = False 
        self.default_system_prompt = (
            "You are AIRA, a smart desktop assistant running locally. Your actual toolkit includes:\n"
            "🔧 System: App Launcher, Volume/Brightness Control, System Stats (CPU/RAM), Process Manager (List/Kill), Clipboard Access, Network Info, and Terminal/Python execution.\n"
            "🤖 Smart Features: Semantic Memory (RAG) and Vision (Screenshots).\n"
            "🔗 Web & Info: DuckDuckGo Search, Weather, Web Scraping, Agenda reading, Date & Time, and Safe Math.\n\n"
            "IMPORTANT: You do NOT have built-in integrations for Email, Cloud Storage, VPNs, or Browser Extensions. "
            "You also do NOT have Voice or TTS capabilities. "
            "Do not claim to have these features. Stick to your actual tools."
        )
        self.system_prompt = self.default_system_prompt
        
        self.tools = [
            {'type': 'function', 'function': {'name': 'search_web', 'description': 'Search the web.', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}},
            {'type': 'function', 'function': {'name': 'get_weather', 'description': 'Get weather.', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string'}}, 'required': ['location']}}},
            {'type': 'function', 'function': {'name': 'check_calendar', 'description': 'Check agenda.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'get_current_datetime', 'description': 'Get current date and time.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'read_local_file', 'description': 'Read file (supports PDF/Txt).', 'parameters': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}}},
            {'type': 'function', 'function': {'name': 'take_screenshot', 'description': 'Capture screen.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'get_system_stats', 'description': 'System usage.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'control_system', 'description': 'Volume/Brightness control.', 'parameters': {'type': 'object', 'properties': {'command': {'type': 'string'}}, 'required': ['command']}}},
            {'type': 'function', 'function': {'name': 'run_shell_command', 'description': 'Run bash command.', 'parameters': {'type': 'object', 'properties': {'command': {'type': 'string'}}, 'required': ['command']}}},
            {'type': 'function', 'function': {'name': 'open_application', 'description': 'Launch app.', 'parameters': {'type': 'object', 'properties': {'app_name': {'type': 'string'}}, 'required': ['app_name']}}},
            {'type': 'function', 'function': {'name': 'execute_python_code', 'description': 'Run Python code.', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string'}}, 'required': ['code']}}},
            {'type': 'function', 'function': {'name': 'scrape_web', 'description': 'Extract text from a website URL.', 'parameters': {'type': 'object', 'properties': {'url': {'type': 'string'}}, 'required': ['url']}}},
            {'type': 'function', 'function': {'name': 'media_control', 'description': 'Control music/video.', 'parameters': {'type': 'object', 'properties': {'action': {'type': 'string'}}, 'required': ['action']}}},
            {'type': 'function', 'function': {'name': 'forget_all_memories', 'description': 'Completely wipe the long-term semantic memory (RAG).', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'get_clipboard', 'description': 'Get text from clipboard.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'set_clipboard', 'description': 'Copy text to clipboard.', 'parameters': {'type': 'object', 'properties': {'text': {'type': 'string'}}, 'required': ['text']}}},
            {'type': 'function', 'function': {'name': 'list_processes', 'description': 'List top resource-consuming processes.', 'parameters': {'type': 'object', 'properties': {'limit': {'type': 'integer'}}, 'required': []}}},
            {'type': 'function', 'function': {'name': 'kill_process', 'description': 'Kill a process by PID or Name.', 'parameters': {'type': 'object', 'properties': {'identifier': {'type': 'string'}}, 'required': ['identifier']}}},
            {'type': 'function', 'function': {'name': 'get_ip_info', 'description': 'Get local and public IP address.', 'parameters': {'type': 'object', 'properties': {}}}},
            {'type': 'function', 'function': {'name': 'calculate_math', 'description': 'Evaluate a math expression safely.', 'parameters': {'type': 'object', 'properties': {'expression': {'type': 'string'}}, 'required': ['expression']}}},
            {'type': 'function', 'function': {'name': 'get_user_info', 'description': 'Get current user and system info.', 'parameters': {'type': 'object', 'properties': {}}}},
        ]

    def set_prompt(self, prompt, history=None):
        self.prompt = prompt
        if history is not None: self.history = history
        self._abort = False

    def set_model(self, model_name):
        self.model = model_name

    def get_available_models(self):
        try:
            response = ollama.list()
            return [m.model for m in response.models]
        except Exception as e:
            return []

    def clear_history(self):
        self.history = []

    def stop(self):
        self._abort = True

    def run(self):
        try:
            # 1. Automatic RAG: Fetch relevant context with UI feedback
            if self._abort: return
            self.tool_started.emit("Memory Retrieval")
            semantic_context = KnowledgeBase.get_context(self.prompt)
            self.tool_finished.emit("Memory Retrieval", semantic_context if semantic_context else "Searching knowledge base... (No relevant snippets found)")
            
            current_messages = [{'role': 'system', 'content': self.system_prompt + semantic_context}]
            current_messages.extend(self.history)
            current_messages.append({'role': 'user', 'content': self.prompt})

            max_turns = 10
            turn = 0
            
            while turn < max_turns:
                if self._abort: return
                turn += 1
                
                response = ollama.chat(
                    model=self.model,
                    messages=current_messages,
                    tools=self.tools
                )
                
                if self._abort: return

                message = response.get('message', {})
                tool_calls = message.get('tool_calls', [])
                
                if tool_calls:
                    current_messages.append(message)
                    for tool in tool_calls:
                        if self._abort: return
                        name = tool['function']['name']
                        args = tool['function'].get('arguments', {})
                        self.tool_started.emit(name)
                        
                        result = ""
                        if name == 'search_web': result = DDGSearch.text_search(args.get('query', ''))
                        elif name == 'get_weather': result = WeatherFetcher.get_weather(args.get('location', ''))
                        elif name == 'check_calendar': result = CalendarReader.get_agenda()
                        elif name == 'get_current_datetime': result = DateTimer.get_current_datetime()
                        elif name == 'read_local_file': result = FileReader.read_file(args.get('path', ''))
                        elif name == 'take_screenshot':
                            path = ScreenReader.take_screenshot()
                            if not path.startswith("ERROR"):
                                self.response_received.emit(f"\n*(Screenshot saved: {path})*\n")
                                current_messages.append({'role': 'user', 'content': 'Analyze this.', 'images': [path]})
                                result = f"Screenshot saved: {path}"
                            else: result = path
                        elif name == 'get_system_stats': result = SystemStats.get_stats()
                        elif name == 'control_system': result = SystemControl.execute_control(args.get('command', ''))
                        elif name == 'run_shell_command': result = ShellExecutor.run_command(args.get('command', ''))
                        elif name == 'open_application':
                            success, msg = AppLauncher.open_app(args.get('app_name', ''))
                            result = msg
                            self.command_triggered.emit("OPEN", args.get('app_name', ''))
                        elif name == 'execute_python_code':
                            success, output = CodeExecutor.execute(args.get('code', ''))
                            result = output
                            self.command_triggered.emit("CODE", args.get('code', ''))
                        elif name == 'scrape_web': result = WebScraper.scrape(args.get('url', ''))
                        elif name == 'media_control': result = MediaController.control(args.get('action', ''))
                        elif name == 'forget_all_memories':
                            KnowledgeBase.clear()
                            result = "All long-term semantic memories have been wiped."
                        elif name == 'get_clipboard': result = ClipboardTool.get_text()
                        elif name == 'set_clipboard': result = ClipboardTool.set_text(args.get('text', ''))
                        elif name == 'list_processes': result = ProcessManager.list_processes(args.get('limit', 5))
                        elif name == 'kill_process': result = ProcessManager.kill_process(args.get('identifier', ''))
                        elif name == 'get_ip_info': result = NetworkInfo.get_ip_info()
                        elif name == 'calculate_math': result = MathEvaluator.calculate(args.get('expression', ''))
                        elif name == 'get_user_info': result = UserInfo.get_info()
                        
                        self.tool_finished.emit(name, str(result))
                        current_messages.append({'role': 'tool', 'content': str(result), 'name': name})
                    continue 
                
                else:
                    final_stream = ollama.chat(
                        model=self.model,
                        messages=current_messages,
                        stream=True
                    )
                    
                    full_text = ""
                    for chunk in final_stream:
                        if self._abort: return
                        content = chunk['message']['content']
                        full_text += content
                        self.response_received.emit(content)
                    
                    # 2. Automatic Indexing with Summarization
                    if not self._abort:
                        self.tool_started.emit("Memory Processing")
                        # Generate concise summary before saving to prevent bloat
                        summary_prompt = f"Summarize this interaction in ONE extremely concise sentence for long-term memory:\nUser: {self.prompt}\nAI: {full_text}"
                        try:
                            sum_res = ollama.generate(model=self.model, prompt=summary_prompt)
                            concise_summary = sum_res.get('response', f"Conversation about: {self.prompt[:50]}").strip()
                            KnowledgeBase.auto_index(concise_summary)
                            self.tool_finished.emit("Memory Processing", f"Indexed: {concise_summary}")
                        except:
                            KnowledgeBase.auto_index(f"User: {self.prompt}\nAI: {full_text[:200]}")
                            self.tool_finished.emit("Memory Processing", "Interaction indexed.")
                    
                    self.history.append({'role': 'user', 'content': self.prompt})
                    self.history.append({'role': 'assistant', 'content': full_text})
                    self.finished_streaming.emit()
                    break

        except Exception as e:
            if not self._abort:
                self.error_occurred.emit(str(e))