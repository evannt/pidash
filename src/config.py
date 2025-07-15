import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    config_file = os.path.join(BASE_DIR, "config", "device.json")

    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        with open(self.config_file) as f:
            config = json.load(f)

        logger.debug("Loaded config:\n%s", json.dumps(config, indent=2))

        return config
    
    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value, save=True):
        self.config[key] = value
        if save:
            self.save_config()
