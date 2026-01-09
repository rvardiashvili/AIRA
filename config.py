import json
import os

class Config:
    FILE = "config.json"
    
    @staticmethod
    def load():
        if os.path.exists(Config.FILE):
            try:
                with open(Config.FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"last_model": "llama3.2"}

    @staticmethod
    def save(data):
        with open(Config.FILE, "w") as f:
            json.dump(data, f)
