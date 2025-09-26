import os
import json
import logging
from typing import Any, Dict
from src.constants import (
    DEFAULT_CONFIG_FILE, CONFIG_DIR, DEFAULT_ORIENTATION, 
    DEFAULT_REFRESH_INTERVAL, DEFAULT_IMAGE_FOLDER
)

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration manager for PiDash application.
    
    Handles loading, saving, and accessing configuration values from device.json.
    Automatically finds the config file in development or production environments.
    """
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    def __init__(self) -> None:
        """Initialize the configuration manager and load config file."""
        self.config_file: str = self._find_config_file()
        self.config: Dict[str, Any] = self.load_config()
    
    def _find_config_file(self) -> str:
        """
        Find the config file, checking multiple possible locations.
        
        Returns:
            str: Path to the found config file
            
        Raises:
            FileNotFoundError: If no config file is found in any location
        """
        possible_paths = [
            # Development path (current working directory)
            os.path.join(self.BASE_DIR, CONFIG_DIR, DEFAULT_CONFIG_FILE),
            # Production path (after install)
            os.path.join(self.BASE_DIR, CONFIG_DIR, DEFAULT_CONFIG_FILE),
            # Fallback to base config
            os.path.join(os.path.dirname(self.BASE_DIR), "install", "config_base", DEFAULT_CONFIG_FILE)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"Found config file at: {path}")
                return path
        
        raise FileNotFoundError(
            f"Config file not found. Checked paths: {possible_paths}\n"
            "Make sure to run the install script or copy install/config_base/device.json to src/config/"
        )
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file contains invalid JSON
            Exception: For other file reading errors
        """
        try:
            with open(self.config_file) as f:
                config = json.load(f)

            logger.debug("Loaded config:\n%s", json.dumps(config, indent=2))
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise
    
    def save_config(self) -> None:
        """
        Save current configuration to file.
        
        Logs errors but doesn't raise exceptions to avoid breaking the application.
        """
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Any: Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key to set
            value: Value to set
            save: Whether to immediately save to file
        """
        self.config[key] = value
        if save:
            self.save_config()
