# Ollama Qt Client Prototype

## Tech Stack
- **Language:** Python 3.12+
- **GUI Framework:** PyQt6
- **AI Backend:** Ollama (assumed running locally at http://localhost:11434)
- **Global Hotkeys:** `pynput`
- **Voice:** `SpeechRecognition` with `PyAudio` (for microphone input)

## Features
1.  **Popup Interface:** A minimalist window reminiscent of Spotlight/Alfred/KRunner.
2.  **Global Shortcut:** `Super+Space` (Windows Key + Space) to toggle visibility.
3.  **Ollama Integration:** Chat with local LLMs.
4.  **Voice Control:** "Listen" mode to convert speech to text and send to LLM.

## Setup Instructions
1.  Ensure Ollama is installed and running (`ollama serve`).
2.  Install system dependencies for audio (e.g., `portaudio19-dev` on Debian/Ubuntu for PyAudio).
3.  Install Python dependencies.

## Architecture
- `main.py`: Entry point, Application class, Tray icon.
- `overlay_window.py`: The actual chat GUI.
- `worker.py`: Threads for Ollama API calls and Voice listening to keep UI responsive.
