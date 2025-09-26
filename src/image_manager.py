import os
import logging
import shutil
import time
from typing import List, Optional, Any, Dict, Tuple
from PIL import Image
from constants import SUPPORTED_IMAGE_EXTENSIONS, DEFAULT_IMAGE_FOLDER

logger = logging.getLogger(__name__)

class ImageManager:
    """
    Manages image files for the PiDash display.
    
    Handles loading, organizing, and providing access to image files.
    Supports various image formats and provides methods for navigation.
    """
    
    BASE_DIR = os.path.dirname(__file__)
    image_extensions = SUPPORTED_IMAGE_EXTENSIONS

    @classmethod
    def list_supported_images_in_dir(cls, directory_path: str) -> List[str]:
        """
        List all supported image files in a directory.
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            List[str]: List of image filenames
        """
        if not os.path.isdir(directory_path):
            return []
        try:
            files = []
            for filename in os.listdir(directory_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in cls.image_extensions:
                    files.append(filename)
            return files
        except Exception:
            return []

    def __init__(self, config: Any) -> None:
        """
        Initialize the image manager.
        
        Args:
            config: Configuration object containing image folder path and settings
        """
        self.config = config
        self.image_folder: str = os.path.abspath(os.path.join(self.BASE_DIR, config.get("image_folder")))
        self.current_index: int = config.get("current_image_index", 0)
        self.image_files: List[str] = []
        
        self._image_cache: Dict[str, Tuple[Image.Image, float]] = {}
        self._cache_max_size = 10  # Maximum number of images to cache
        self._cache_timeout = 300  # 5 minutes cache timeout
        
        self.refresh_image_list()

    def _clean_cache(self) -> None:
        """Clean expired entries from the image cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._image_cache.items()
            if current_time - timestamp > self._cache_timeout
        ]
        for key in expired_keys:
            del self._image_cache[key]
            logger.debug(f"Removed expired cache entry: {key}")

    def _get_cached_image(self, image_path: str) -> Optional[Image.Image]:
        """Get image from cache if available and not expired."""
        current_time = time.time()
        
        if image_path in self._image_cache:
            cached_image, timestamp = self._image_cache[image_path]
            if current_time - timestamp <= self._cache_timeout:
                logger.debug(f"Using cached image: {os.path.basename(image_path)}")
                return cached_image
            else:
                del self._image_cache[image_path]
        
        return None

    def _cache_image(self, image_path: str, image: Image.Image) -> None:
        """Cache an image with timestamp."""
        if len(self._image_cache) >= self._cache_max_size:
            self._clean_cache()
        
        if len(self._image_cache) >= self._cache_max_size:
            oldest_key = min(self._image_cache.keys(), 
                           key=lambda k: self._image_cache[k][1])
            del self._image_cache[oldest_key]
        
        self._image_cache[image_path] = (image, time.time())
        logger.debug(f"Cached image: {os.path.basename(image_path)}")

    def clear_cache(self) -> None:
        """Clear the image cache."""
        self._image_cache.clear()
        logger.debug("Image cache cleared")

    def get_image_names(self) -> List[str]:
        """
        Get list of image filenames (without full paths).
        
        Returns:
            List[str]: List of image filenames
        """
        return [os.path.basename(image_path) for image_path in self.image_files]
    
    def add_image(self, image_path: str) -> None:
        """
        Add an image to the image folder.
        
        Args:
            image_path: Path to the image file to add
        """
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
        """Refresh the list of available images and clear cache if needed."""
        if not os.path.exists(self.image_folder):
            logger.warning(f"Image folder {self.image_folder} doesn't exist. Creating it.")
            os.makedirs(self.image_folder, exist_ok=True)
            return

        logger.info(f"Scanning folder: {self.image_folder}")
        logger.info(f"Scanning images: {os.listdir(self.image_folder)}")
        
        old_image_files = set(self.image_files)
        self.image_files = []

        for file in os.listdir(self.image_folder):
            if any(file.lower().endswith(ext) for ext in self.image_extensions):
                logger.info(f"Loaded {file}.")
                self.image_files.append(os.path.join(self.image_folder, file))
        
        new_image_files = set(self.image_files)
        if old_image_files != new_image_files:
            self.clear_cache()
            logger.info("Image list changed, cache cleared")
        
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

    def get_next_image(self) -> Optional[Image.Image]:
        """
        Get the next image in the sequence.
        
        Returns:
            Optional[Image.Image]: Next image or None if no images available
        """
        if not self.image_files:
            logger.warning(f"No images were found in {self.config.get('image_folder')}.")
            return None
        
        try:
            current_image_index = (self.current_index + 1) % len(self.image_files)
            image_path = self.image_files[current_image_index]
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            cached_image = self._get_cached_image(image_path)
            if cached_image is not None:
                logger.info(f"Using cached image: {os.path.basename(image_path)} ({current_image_index}/{len(self.image_files)})")
                return cached_image
                
            image = Image.open(image_path)
            self._cache_image(image_path, image)
            logger.info(f"Loaded image for display: {os.path.basename(image_path)} ({current_image_index}/{len(self.image_files)})")
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
            logger.warning(f"No images were found in {self.config.get('image_folder')}.")
            return None
        
        try:
            previous_image_index = (self.current_index - 1) % len(self.image_files)
            image_path = self.image_files[previous_image_index]
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            cached_image = self._get_cached_image(image_path)
            if cached_image is not None:
                logger.info(f"Using cached image: {os.path.basename(image_path)} ({previous_image_index}/{len(self.image_files)})")
                return cached_image
                
            image = Image.open(image_path)
            self._cache_image(image_path, image)
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
