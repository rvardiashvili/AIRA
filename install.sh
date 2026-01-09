#!/bin/bash

APP_NAME="AIRA"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_PATH="$APP_DIR/icons/aira.svg"
EXEC_PATH="$APP_DIR/run.sh"
DESKTOP_FILE="$HOME/.local/share/applications/aira.desktop"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/aira.desktop"

echo "🚀 Installing $APP_NAME..."

# 1. Install Python Dependencies
if [ -d "venv" ]; then
    echo "📦 Virtual environment found. Installing requirements..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 2. Make all scripts executable
echo "🔐 Setting permissions..."
chmod +x "$EXEC_PATH"
chmod +x "$APP_DIR/scripts/"*

# 3. Create Desktop Entry
echo "Desktop Entry..."
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Comment=AI Desktop Assistant
Exec=$EXEC_PATH
Path=$APP_DIR
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;
EOF

# 4. Enable Autostart
echo "Enable Autostart..."
mkdir -p "$AUTOSTART_DIR"
cp "$DESKTOP_FILE" "$AUTOSTART_FILE"

# 5. File Manager Integrations
echo "🔌 Setting up Integrations..."
python3 scripts/setup_integrations.py

echo "✅ Installation Complete!"
echo "You can now find AIRA in your app menu."
echo "It will start automatically on next login."
echo "Run './run.sh' to start immediately."
