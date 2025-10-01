import os
import logging
import shutil
from typing import List, Optional
from PIL import Image
from src.constants import SUPPORTED_IMAGE_EXTENSIONS, IMAGE_FOLDER_KEY, CURRENT_IMAGE_INDEX_KEY
from src.config import Config

logger = logging.getLogger(__name__)

class ImageManager:
    """
    Manages image files for the PiDash display.
    
    Handles loading, organizing, and providing access to image files.
    Supports various image formats and provides methods for navigation.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_extensions = SUPPORTED_IMAGE_EXTENSIONS

    def __init__(self, config: Config) -> None:
        """
        Initialize the image manager.
        
        Args:
            config: Configuration object containing image folder path and settings
        """
        self.config = config
        self.image_folder: str = os.path.abspath(os.path.join(self.BASE_DIR, config.get(IMAGE_FOLDER_KEY)))
        self.current_index: int = config.get(CURRENT_IMAGE_INDEX_KEY, 0)
        self.image_files: List[str] = []
        
        self.refresh_image_list()

    def get_image_names(self) -> List[str]:
        """
        Get list of image filenames (without full paths).
        
        Returns:
            List[str]: List of image filenames
        """
        return [os.path.basename(image_path) for image_path in self.image_files]
    
    def get_image_paths(self) -> List[str]:
        """
        Get list of image full paths.
        
        Returns:
            List[str]: List of image full paths
        """
        return self.image_files
    
    def add_image(self, image_path: str, original_filename: str) -> bool:
        """
        Add an image to the image folder.
        
        Args:
            image_path: Path to the image file to add
        """
        if not os.path.exists(image_path):
            logger.error(f"Source image {image_path} doesn't exist.")
            return False

        if not any(original_filename.lower().endswith(ext) for ext in self.image_extensions):
            logger.error(f"File {image_path} is not a supported image format.")
            return False
        
        destination_name = original_filename
        destination_path = os.path.join(self.image_folder, destination_name)
        
        if os.path.exists(destination_path):
            base, ext = os.path.splitext(destination_name)
            counter = 1
            while os.path.exists(destination_path):
                destination_name = f"{base}_{counter}{ext}"
                destination_path = os.path.join(self.image_folder, destination_name)
                counter += 1
            logger.info(f"File renamed to {destination_name} to avoid overwriting.")
        
        try:
            shutil.copy2(image_path, destination_path)
            logger.info(f"Successfully added {destination_name} to {self.image_folder}.")
            self.refresh_image_list()
            return True
        except Exception as e:
            logger.error(f"Failed to add image {image_path}: {str(e)}")
            return False

    def remove_all_images(self) -> None:
        self.remove_images(self.get_image_names())

    def remove_image(self, image_path) -> bool:
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist.")
            return False
        
        if not os.path.dirname(image_path):
            full_path = os.path.join(self.image_folder, image_path)
        else:
            full_path = image_path
        
        if not os.path.exists(full_path):
            logger.error(f"Image {full_path} doesn't exist.")
            return False
        
        if not any(full_path.lower().endswith(ext) for ext in self.image_extensions):
            logger.error(f"File {full_path} is not a supported image format.")
            return False
        
        try:
            was_current_image = (full_path in self.image_files and 
                               self.image_files.index(full_path) == self.current_index)
            
            os.remove(full_path)
            logger.info(f"Successfully removed {os.path.basename(full_path)} from {self.image_folder}.")
            
            self.refresh_image_list()
            
            if was_current_image and self.image_files and self.current_index >= len(self.image_files):
                self.current_index = 0
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove image {full_path}: {str(e)}")
            return False

    def remove_images(self, image_paths) -> None:
        for imagePath in image_paths:
            self.remove_image(imagePath)

    def refresh_image_list(self) -> None:
        """Refresh the list of available images and clear cache if needed."""
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist. Creating it.")
            os.makedirs(self.image_folder, exist_ok=True)
            return

        logger.info(f"Scanning folder: {self.image_folder}")
        
        self.image_files = []

        for file in os.listdir(self.image_folder):
            if any(file.lower().endswith(ext) for ext in self.image_extensions):
                logger.info(f"Loaded {file}.")
                self.image_files.append(os.path.join(self.image_folder, file))
        
        logger.info(f"Successfully loaded {len(self.image_files)} images.")
        
        if self.current_index >= len(self.image_files):
            self.current_index = 0

    def get_current_image_name(self) -> str:
        image_path =self.get_current_image()
        if not image_path:
            logger.warning(f"No images were found in {self.config.get(IMAGE_FOLDER_KEY)}.")
            return None
        return os.path.basename(image_path)

    def set_current_image(self, image_name) -> None:
        for i, img_name in enumerate(self.get_image_names()):
            if image_name == img_name:
                self.current_index = i
                self.config.set(CURRENT_IMAGE_INDEX_KEY, i)
                break

    def get_current_image(self) -> str:
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get(IMAGE_FOLDER_KEY)}.")
            return None
        logger.info(f"Current image index: {self.images_files[self.current_index]}")
        return Image.open(self.image_files[self.current_index])

    def get_next_image(self) -> Optional[Image.Image]:
        """
        Get the next image in the sequence.
        
        Returns:
            Optional[Image.Image]: Next image or None if no images available
        """
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get(IMAGE_FOLDER_KEY)}.")
            return None
        
        try:
            next_image_index = (self.current_index + 1) % len(self.image_files)
            image_path = self.image_files[next_image_index]
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
                
            image = Image.open(image_path)
            logger.info(f"Loaded image for display: {os.path.basename(image_path)} ({next_image_index + 1}/{len(self.image_files)})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None

    def get_previous_image(self) -> Optional[Image.Image]:
        """
        Get the previous image in the sequence.
        
        Returns:
            Optional[Image.Image]: Previous image or None if no images available
        """
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get(IMAGE_FOLDER_KEY)}.")
            return None
        
        try:
            previous_image_index = (self.current_index - 1) % len(self.image_files)
            image_path = self.image_files[previous_image_index]
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
                
            image = Image.open(image_path)
            logger.info(f"Loaded image for display: {os.path.basename(image_path)} ({previous_image_index + 1}/{len(self.image_files)})")
            return image
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
        
    def update_image_index(self, increment: bool = True) -> None:
        if increment:
            self.current_index = (self.current_index + 1) % len(self.image_files)
        else:
            self.current_index = (self.current_index - 1) % len(self.image_files)
        self.config.set(CURRENT_IMAGE_INDEX_KEY, self.current_index)

    def get_image_count(self) -> int:
        return len(self.image_files)
