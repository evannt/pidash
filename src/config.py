import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    """
    Manages application configuration.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    config_file = os.path.join(BASE_DIR, "config", "device.json")

    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        with open(self.config_file) as f:
            config = json.load(f)

        logger.debug("Loaded config:\n%s", json.dumps(config, indent=2))

        return config
    
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

    def get_resolution(self):
        """Returns the display resolution as a tuple (width, height) from the configuration."""
        resolution = self.get("resolution")
        width, height = resolution
        return (int(width), int(height))
