# AIRA Roadmap & Documentation

A minimalist, high-performance desktop AI assistant for Linux.

## ✅ Currently Implemented Features

### 🖥️ User Interface
- **KRunner Style:** Sleek, centered search bar that expands only when needed.
- **Global Toggle:** `Super+Space` to summon the assistant from anywhere.
- **Auto-Hide:** Automatically disappears and resets when you switch focus or press `Esc`.
- **System Theme Adherence:** Uses native Qt palettes to match your OS colors and transparency.
- **Interactive Tool Blocks:** Tool results appear as compact, clickable badges that expand/collapse.
- **Markdown Support:** Full rendering of bold text, lists, and code blocks.
- **Interruptible AI:** Submit a new query to instantly stop the current thinking/streaming process.
- **Drag & Drop:** Drop files directly onto the bar to process them.
- **Smooth Animations:** Graceful window expansion and collapse.

### 🧠 AI & Backend (AIRA)
- **Native Ollama Tools:** Uses the innate tool-calling API for high reliability.
- **Semantic RAG:** Automatic memory retrieval and storage using high-speed vector embeddings (`all-minilm`).
- **Memory Summarization:** AI automatically summarizes interactions before saving them to long-term memory to prevent bloat.
- **Model Selector:** Persistent memory of your preferred LLM with a checkmarked menu.
- **Personas:** Switch between "Code Expert", "Creative Writer", "Tutor", and more.
- **Vision Integration:** Automatic screenshot-to-model pipeline for Llama 3.2 Vision.

---

## 🛠️ Integrated Tools (Verified)
1.  **`search_web`**: Live web search via DuckDuckGo.
2.  **`get_weather`**: Real-time local weather.
3.  **`check_calendar`**: Check time and local `agenda.txt`.
4.  **`get_current_datetime`**: Get the current system date and time.
5.  **`take_screenshot`**: Captures screen context (Wayland & X11).
6.  **`get_system_stats`**: Real-time CPU, RAM, and Disk usage.
7.  **`list_processes`**: List top resource-consuming processes.
8.  **`kill_process`**: Kill a process by name or PID.
9.  **`control_system`**: Hardware control for Volume and Brightness.
10. **`get_clipboard`**: Read text from the system clipboard.
11. **`set_clipboard`**: Write text to the system clipboard.
12. **`read_local_file`**: Read and summarize text and PDF files.
13. **`run_shell_command`**: Execute arbitrary bash commands.
14. **`open_application`**: Launcher for desktop applications.
15. **`execute_python_code`**: Isolated Python environment.
16. **`calculate_math`**: Safe mathematical evaluation.
17. **`scrape_web`**: Extract full text from any URL.
18. **`get_ip_info`**: Check local and public IP addresses.
19. **`get_user_info`**: Get current user and hostname.
20. **`media_control`**: Control system media (Play/Pause/Skip).
21. **`forget_all_memories`**: Wipe the semantic vector database.

---

## 🚀 Future Roadmap (Planned / Not Implemented)
- [ ] **File Organizer:** Move, rename, or delete files based on AI logic.
- [ ] **Plugin Store:** A way for users to drop custom `.py` tools into a folder.
- [ ] **Theme Store:** Pre-defined themes (Nord, Dracula, Solarized).
- [ ] **Multi-Modal Drag & Drop:** Drop images for instant visual analysis.

## 🗑️ Deprecated / Removed Features
- **Voice Control & TTS:** Removed to maintain a lightweight, text-only experience.
