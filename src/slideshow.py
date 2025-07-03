import time
import logging
from PIL import Image
from config import Config
from image_manager import ImageManager
from display_manager import DisplayManager
from refresh_task import RefreshTask

logger = logging.getLogger(__name__)

class SlideShow:
    """
    Main application class.
    Designed for easy extension to web server functionality.
    """
    def __init__(self):
        self.config = Config()
        self.image_manager = ImageManager(self.config)
        self.display_manager = DisplayManager(self.config)
        self.refresh_task = RefreshTask(self.config, self.image_manager, self.display_manager)
    
    def run(self):
        """Run the image refresh."""
        try:
            logger.info("Starting Image Refresh")
            logger.info(f"Image folder: {self.config.get('image_folder')}")
            logger.info(f"Refresh interval: {self.config.get('refresh_interval_seconds')} seconds")
            
            self.refresh_task.start()
            
            # Keep main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.refresh_task.stop()
    
    def display_single_image(self, image_path):
        """Display a specific image (useful for testing or web interface)."""
        try:
            image = Image.open(image_path)
            return self.display_manager.display_image(image)
        except Exception as e:
            logger.error(f"Error displaying single image: {e}")
            return False
