import json
import os
import getpass
import platform

class Config:
    DATA_DIR = os.path.expanduser("~/.local/share/aira")
    FILE = os.path.join(DATA_DIR, "config.json")
    
    DEFAULTS = {
        "last_model": "llama3.2",
        "theme": "System",
        "personas": {
            "Default": "You are a helpful assistant.",
            "Code Expert": "You are an expert programmer. Write clean, efficient code.",
            "Creative Writer": "You are a creative writer. Use vivid imagery."
        },
        "user_profile": {
            "name": "",
            "role": "",
            "interests": ""
        }
    }
    
    @staticmethod
    def load():
        config = Config.DEFAULTS.copy()
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR, exist_ok=True)
            
        if os.path.exists(Config.FILE):
            try:
                with open(Config.FILE, "r") as f:
                    data = json.load(f)
                    config.update(data)
                    if "personas" in data: config["personas"].update(data["personas"])
                    if "user_profile" in data: config["user_profile"].update(data["user_profile"])
            except:
                pass
        
        # Pull basics from system if not setup
        if not config["user_profile"]["name"]:
            config["user_profile"]["name"] = getpass.getuser()
        if not config["user_profile"]["role"]:
            config["user_profile"]["role"] = f"User on {platform.system()}"
            
        return config

    @staticmethod
    def save(data):
        if not os.path.exists(Config.DATA_DIR):
            os.makedirs(Config.DATA_DIR, exist_ok=True)
        with open(Config.FILE, "w") as f:
            json.dump(data, f, indent=4)
