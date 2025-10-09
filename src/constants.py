"""
Constants for PiDash application.

Centralizes all magic numbers, strings, and configuration values
to improve maintainability and reduce duplication.
"""

# File and path constants
DEFAULT_IMAGE_FOLDER = "src/static/images"
DEFAULT_CONFIG_FILE = "device.json"
CONFIG_DIR = "config"

# Config constants
NAME_KEY = "name"
HOSTNAME_KEY = "hostname"
LOCAL_IP_KEY = "local_ip"
IMAGE_FOLDER_KEY = "image_folder"
ORIENTATION_KEY = "orientation"
INVERTED_IMAGE_KEY = "inverted_image"
REFRESH_INTERVAL_KEY = "refresh_interval"
CURRENT_IMAGE_INDEX_KEY = "current_image_index"
IMAGE_SETTINGS_KEY = "image_settings"
RESOLUTION_KEY = "resolution"

CONFIG_KEY = "config"
IMAGE_MANAGER_KEY = "image_manager"
REFRESH_MANAGER_KEY = "refresh_manager"
DISPLAY_MANAGER_KEY = "display_manager"

# Image processing constants
SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico"
}

# Display constants
DEFAULT_ORIENTATION = "landscape"
DEFAULT_REFRESH_INTERVAL = 900  # 15 minutes in seconds
DEFAULT_BRIGHTNESS = 1.0
DEFAULT_CONTRAST = 1.0
DEFAULT_SATURATION = 1.0
DEFAULT_SHARPNESS = 1.0

# Gallery constants
DEFAULT_GALLERY_LIMIT = 24

# Time constants (in seconds)
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400

# File upload constants
MAX_FILE_SIZE_MB = 16
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 
    'image/tiff', 'image/webp'
}

# Validation constants
MIN_REFRESH_INTERVAL = 60  # 1 second
MAX_REFRESH_INTERVAL = SECONDS_PER_DAY  # 24 hours
VALID_ORIENTATIONS = {"landscape", "portrait"}

# Logging constants
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

# Web server constants
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 80

# Image enhancement settings
DEFAULT_IMAGE_SETTINGS = {
    "brightness": DEFAULT_BRIGHTNESS,
    "contrast": DEFAULT_CONTRAST,
    "saturation": DEFAULT_SATURATION,
    "sharpness": DEFAULT_SHARPNESS
}
