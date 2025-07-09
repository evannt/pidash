import os
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class ImageManager:
    """
    Manages image loading and cycling.
    """

    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

    def __init__(self, config):
        self.config = config
        self.image_folder = config.get("image_folder")
        self.current_index = config.get("current_image_index", 0)
        self.image_files = []
        self.refresh_image_list()
    
    def refresh_image_list(self):
        """Scan mages folder for images."""
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist. Creating it.")
            os.makedirs(self.image_folder, exist_ok=True)
            return
        
        self.image_files = []
        for file in os.listdir(self.image_folder):
            if any(file.lower().endswith(ext) for ext in self.image_extensions):
                self.image_files.append(os.path.join(self.image_folder, file))
        
        self.image_files.sort()
        logger.info(f"Successfully loaded {len(self.image_files)} images.")
        
        if self.current_index >= len(self.image_files):
            self.current_index = 0
    
    def get_next_image(self):
        """Get the next image in rotation."""
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get("image_folder")}.")
            return None
        
        image_path = self.image_files[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.image_files)
        
        self.config.set("current_image_index", self.current_index)
        
        try:
            image = Image.open(image_path)
            logger.info(f"Loaded image: {os.path.basename(image_path)} ({self.current_index}/{len(self.image_files)})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def get_image_count(self):
        """Get total number of images."""
        return len(self.image_files)
