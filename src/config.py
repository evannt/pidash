import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """
    Manages application configuration with extensible structure.
    Key for future web server integration.
    """
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "image_folder": "images",
            "rotation_interval_seconds": 60,
            "current_image_index": 0,
            "display_orientation": 0,
            "image_extensions": [".jpg", ".jpeg", ".png", ".bmp"]
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create with defaults."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}. Using defaults.")
                return self.default_config.copy()
        return self.default_config.copy()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value, save=True):
        """Set configuration value."""
        self.config[key] = value
        if save:
            self.save_config()
