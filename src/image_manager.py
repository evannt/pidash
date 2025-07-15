import os
import logging
import shutil
from PIL import Image

logger = logging.getLogger(__name__)

class ImageManager:

    BASE_DIR = os.path.dirname(__file__)
    image_extensions = [".jpg", ".jpeg", ".png"]

    def __init__(self, config):
        self.config = config
        self.image_folder = os.path.abspath(os.path.join(self.BASE_DIR, config.get("image_folder")))
        self.current_index = config.get("current_image_index", 0)
        self.image_files = []
        self.refresh_image_list()

    def get_image_names(self):
        return [os.path.basename(image_path) for image_path in self.image_files]
    
    def add_image(self, image_path):
        if not os.path.exists(image_path):
            logger.error(f"Source image {image_path} doesn't exist.")
        
        if not any(image_path.lower().endswith(ext) for ext in self.image_extensions):
            logger.error(f"File {image_path} is not a supported image format.")
        
        destination_name = os.path.basename(image_path)
        
        destination_path = os.path.join(self.image_folder, destination_name)
        
        if os.path.exists(destination_path):
            logger.warning(f"Image {destination_name} already exists in {self.image_folder}.")
        
        try:
            shutil.copy2(image_path, destination_path)
            logger.info(f"Successfully added {destination_name} to {self.image_folder}.")
            
            self.refresh_image_list()
        except Exception as e:
            logger.error(f"Failed to add image {image_path}: {str(e)}")

    def remove_all_images(self):
        self.remove_images(self.get_image_names())

    def remove_image(self, image_path):
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist.")
        
        if os.path.dirname(image_path):
            image_path = image_path
            image_path = os.path.basename(image_path)
        else:
            image_path = os.path.join(self.image_folder, image_path)
        
        if not os.path.exists(image_path):
            logger.error(f"Image {image_path} doesn't exist in {self.image_folder}.")
        
        if not any(image_path.lower().endswith(ext) for ext in self.image_extensions):
            logger.error(f"File {image_path} is not a supported image format.")
        
        try:
            was_current_image = (image_path in self.image_files and 
                               self.image_files.index(image_path) == self.current_index)
            
            os.remove(image_path)
            logger.info(f"Successfully removed {image_path} from {self.image_folder}.")
            
            self.refresh_image_list()
            
            if was_current_image and self.image_files and self.current_index >= len(self.image_files):
                self.current_index = 0
            
        except Exception as e:
            logger.error(f"Failed to remove image {image_path}: {str(e)}")

    def remove_images(self, image_paths):
        for image in image_paths:
            self.remove_image(image)

    def refresh_image_list(self):
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist. Creating it.")
            os.makedirs(self.image_folder, exist_ok=True)
            return

        logger.info(f"Scanning folder: {self.image_folder}")
        logger.info(f"Scanning images: {os.listdir(self.image_folder)}")
        self.image_files = []

        for file in os.listdir(self.image_folder):
            if any(file.lower().endswith(ext) for ext in self.image_extensions):
                logger.info(f"Loaded {file}.")
                self.image_files.append(os.path.join(self.image_folder, file))
        
        logger.info(f"Successfully loaded {len(self.image_files)} images.")
        
        if self.current_index >= len(self.image_files):
            self.current_index = 0
    
    def set_current_image(self, image_name):
        for i, img_name in enumerate(self.get_image_names()):
            if image_name == img_name:
                self.config.set("current_image_index", i)
                break

    def get_current_image(self):
        return self.image_files[self.current_index]

    def get_next_image(self):
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get('image_folder')}.")
            return None
        
        current_image_index = (self.current_index + 1) % len(self.image_files)
        image_path = self.image_files[current_image_index]
        
        try:
            image = Image.open(image_path)
            logger.info(f"Loaded image for display: {os.path.basename(image_path)} ({current_image_index}/{len(self.image_files)})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def get_previouse_image(self):
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get('image_folder')}.")
            return None
        
        previous_image_index = (self.current_index - 1) % len(self.image_files)
        image_path = self.image_files[previous_image_index]
        
        try:
            image = Image.open(image_path)
            logger.info(f"Loaded image for display: {os.path.basename(image_path)} ({previous_image_index}/{len(self.image_files)})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def update_image_index(self, increment=True):
        if increment:
            self.current_index = (self.current_index + 1) % len(self.image_files)
        else:
            self.current_index = (self.current_index - 1) % len(self.image_files)
        self.config.set("current_image_index", self.current_index)

    def get_image_count(self):
        return len(self.image_files)
