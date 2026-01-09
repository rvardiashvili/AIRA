# AIRA (AI Responsive Assistant) 🤖

AIRA is a minimalist, high-performance desktop AI assistant for Linux, built with **Python**, **PyQt6**, and **Ollama**. It integrates deeply with your system to provide local AI power at your fingertips.

## 🚀 Key Features

*   **⚡ Instant Access:** Summon AIRA anywhere with `Super+Space`.
*   **🔒 100% Local:** Powered by Ollama. Your data never leaves your machine.
*   **🧠 Advanced RAG (ChromaDB):** Advanced semantic memory that understands your files and past conversations.
*   **💾 Robust History:** SQLite-backed chat sessions. Resume any past conversation instantly.
*   **🔌 System Integration:**
    *   **File Manager Extensions:** Right-click any folder in Nautilus, Nemo, or Dolphin to index it.
    *   **Disk Indexer:** Recursively index your projects and documents.
    *   **Tool Power:** App launcher, process manager, clipboard control, and network tools.
*   **🎨 Customization:**
    *   **Themes:** Dark, Light, and Nord themes that follow system standards.
    *   **Personas:** Create custom AI experts (Coder, Writer, etc.).
    *   **User Profile:** Personalize responses with your name and role.

## 📦 Installation

### Prerequisites
1.  **Ollama**: Install [Ollama](https://ollama.com/) and pull a model:
    ```bash
    ollama pull llama3.2
    ```
2.  **System Dependencies**:
    ```bash
    sudo apt install python3-venv xclip notify-send
    ```

### Setup
1.  Clone and run the installer:
    ```bash
    git clone https://github.com/your-username/AIRA.git
    cd AIRA
    ./install.sh
    ```

## 🖥️ Usage

*   **Toggle:** `Super+Space`
*   **Index Folder:** Right-click a folder in your file manager -> "AIRA: Index this Folder"
*   **Settings:** Click the ⚙️ icon to manage personas, history, and themes.

## 🛠️ Project Structure

```text
├── src/                  # Source Code
│   ├── core/             # AI logic, DB, and Memory
│   ├── ui/               # PyQt6 Interface & Themes
│   └── tools/            # System & Web integration
├── scripts/              # Integration & CLI scripts
├── docs/                 # Documentation
├── icons/                # Assets
└── requirements.txt      # Dependencies
```

## 📜 License
MIT License. See [LICENSE](LICENSE) for details.