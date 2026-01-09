# Ollama Qt Client

A minimalist, Spotlight-like AI assistant using local Ollama models.

## Features
- **Global Hotkey:** Press `Super+Space` (Windows Key + Space) to toggle the chat window anywhere.
- **Voice Control:** Click the microphone icon to speak your prompt.
- **Local AI:** Uses your local Ollama instance (default model: `llama3.2`).
- **System Tray:** Runs in the background with a tray icon.

## Requirements
- Linux (X11 preferred for global hotkeys, Wayland support varies).
- [Ollama](https://ollama.com/) installed and running (`ollama serve`).
- Python 3.12+

## Setup & Run
1.  **Install Dependencies:**
    ```bash
    ./venv/bin/pip install -r requirements.txt
    ```
    (Already done if you followed the setup)

2.  **Run:**
    ```bash
    ./run.sh
    ```

3.  **Usage:**
    - Press `Super+Space` to show the window.
    - Type or speak.
    - Press `Esc` to hide.

## Troubleshooting
- **Microphone:** Ensure `pyaudio` dependencies are met. On Debian/Ubuntu: `sudo apt install python3-pyaudio portaudio19-dev`.
- **Hotkeys:** If `Super+Space` doesn't work (common on Wayland), use the System Tray icon to show/hide.
