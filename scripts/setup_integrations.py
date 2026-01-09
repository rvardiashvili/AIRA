import os
import sys
import shutil
import textwrap

def get_paths():
    home = os.path.expanduser("~")
    # project_root should be /home/rati/CustonIconPack
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python = os.path.join(project_root, "venv", "bin", "python3")
    script_path = os.path.join(project_root, "scripts", "aira_index.py")
    return home, venv_python, script_path

def setup_gnome_style(file_manager, home, venv_python, script_path):
    # Nautilus / Nemo / Caja
    base_dir = os.path.join(home, ".local", "share", file_manager)
    if not os.path.exists(base_dir):
        return False
        
    scripts_dir = os.path.join(base_dir, "scripts")
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir, exist_ok=True)
    
    dest_file = os.path.join(scripts_dir, "AIRA - Index Folder")
    
    content = textwrap.dedent(f"""
        #!/usr/bin/env bash
        # AIRA Indexing Script for {file_manager}
        
        # Use provided env vars or positional arguments
        TARGETS="${{NAUTILUS_SCRIPT_SELECTED_FILE_PATHS:-$NEMO_SCRIPT_SELECTED_FILE_PATHS}}"
        
        if [ -n "$TARGETS" ]; then
            echo "$TARGETS" | while read -r line; do
                [ -z "$line" ] && continue
                "{venv_python}" "{script_path}" "$line"
            done
        else
            for arg in "$@"; do
                [ -z "$arg" ] && continue
                "{venv_python}" "{script_path}" "$arg"
            done
        fi
    """).strip()
    
    try:
        with open(dest_file, "wb") as f:
            f.write(content.encode('utf-8').replace(b'\r\n', b'\n') + b'\n')
        os.chmod(dest_file, 0o755)
        print(f"✅ Installed script for {file_manager} at {dest_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to install for {file_manager}: {e}")
        return False

def setup_kde(home, venv_python, script_path):
    # Dolphin / Konqueror
    possible_paths = [
        os.path.join(home, ".local", "share", "kio", "servicemenus"),
        os.path.join(home, ".local", "share", "kservices5", "ServiceMenus")
    ]
    
    installed_any = False
    for services_dir in possible_paths:
        if not os.path.exists(services_dir):
            try:
                os.makedirs(services_dir, exist_ok=True)
            except:
                continue

        desktop_file = os.path.join(services_dir, "aira_index.desktop")
        
        content = textwrap.dedent(f"""
            [Desktop Entry]
            Type=Service
            ServiceTypes=KonqPopupMenu/Plugin
            MimeType=inode/directory;
            Actions=indexFolder;

            [Desktop Action indexFolder]
            Name=AIRA: Index this Folder
            Icon=utilities-terminal
            Exec="{venv_python}" "{script_path}" "%f"
        """).strip()
        
        try:
            with open(desktop_file, "wb") as f:
                f.write(content.encode('utf-8').replace(b'\r\n', b'\n') + b'\n')
            # CRITICAL: KDE Service Menu .desktop files often need execute permission to run
            os.chmod(desktop_file, 0o755)
            print(f"✅ Installed ServiceMenu for KDE/Dolphin at {services_dir}")
            installed_any = True
        except Exception as e:
            print(f"❌ Failed to install for KDE at {services_dir}: {e}")
            
    return installed_any

def main():
    print("🔌 Setting up File Manager Integrations...")
    home, venv_python, script_path = get_paths()
    
    if not os.path.exists(venv_python):
        print(f"⚠️ Warning: Venv python not found: {venv_python}")
    if not os.path.exists(script_path):
        print(f"⚠️ Warning: Script not found: {script_path}")

    try:
        os.chmod(script_path, 0o755)
    except:
        pass

    installed = False
    for fm in ["nautilus", "nemo", "caja"]:
        if setup_gnome_style(fm, home, venv_python, script_path):
            installed = True
            
    if setup_kde(home, venv_python, script_path):
        installed = True
        
    if not installed:
        print("⚠️ No compatible file managers detected.")
    else:
        print("🎉 Integrations updated! If you see 'Not authorized', please check permissions manually.")

if __name__ == "__main__":
    main()