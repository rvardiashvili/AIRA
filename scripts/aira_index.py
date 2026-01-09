#!/usr/bin/env python3
import sys
import os
import subprocess
import logging

# Setup Logging
data_dir = os.path.expanduser("~/.local/share/aira")
os.makedirs(data_dir, exist_ok=True)
log_file = os.path.join(data_dir, "indexer.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.tools.indexer import DiskIndexer

def notify(summary, body):
    logging.info(f"Notification: {summary} - {body}")
    try:
        subprocess.run(["notify-send", "-a", "AIRA", "-i", "utilities-terminal", summary, body])
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

def main():
    if len(sys.argv) < 2:
        logging.warning("No path provided to indexer.")
        return

    path = sys.argv[1]
    # Some managers pass file:// URLs
    if path.startswith('file://'):
        from urllib.parse import unquote
        path = unquote(path[7:])
    
    path = os.path.abspath(path)
    logging.info(f"Starting indexing for: {path}")
    
    if not os.path.exists(path):
        notify("AIRA Indexing", f"Error: Path not found: {path}")
        return

    notify("AIRA Indexing", f"Started indexing: {os.path.basename(path)}")
    
    try:
        result = DiskIndexer.index_directory(path)
        notify("AIRA Indexing", result)
        logging.info(f"Success: {result}")
    except Exception as e:
        error_msg = f"Failed: {str(e)}"
        notify("AIRA Indexing", error_msg)
        logging.exception(error_msg)

if __name__ == "__main__":
    main()
