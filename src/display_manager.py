import logging
import hashlib
from PIL import Image
from inky.auto import auto

logger = logging.getLogger(__name__)
class DisplayManager:
    """
    Handles Inky display operations with image processing.
    Crucial for proper e-ink display rendering.
    """
    def __init__(self, config):
        self.config = config
        self.display = None
        self.last_image_hash = None
        self.initialize_display()
    
    def initialize_display(self):
        """Initialize the Inky display."""
        try:
            self.display = auto()
            self.display.set_border(self.display.BLACK)
            logger.info(f"Inky display initialized: {self.display.width}x{self.display.height}")
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise
    
    def compute_image_hash(self, image):
        """Compute hash of image to detect changes."""
        return hashlib.md5(image.tobytes()).hexdigest()
    
    def process_image(self, image):
        """
        Process image for display: resize, rotate, optimize.
        Critical for proper e-ink rendering.
        """
        if not image:
            return None
        
        # Handle orientation
        orientation = self.config.get('display_orientation', 0)
        if orientation != 0:
            image = image.rotate(-orientation, expand=True)
        
        # Resize to display dimensions while maintaining aspect ratio
        display_size = (self.display.width, self.display.height)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Create a new image with display dimensions and paste the resized image
        processed_image = Image.new('RGB', display_size, 'white')
        
        # Center the image
        x_offset = (display_size[0] - image.width) // 2
        y_offset = (display_size[1] - image.height) // 2
        processed_image.paste(image, (x_offset, y_offset))
        
        return processed_image
    
    def display_image(self, image):
        """
        Display image on Inky screen.
        Only updates if image has changed (saves battery).
        """
        if not image or not self.display:
            logger.error("No image or display not initialized")
            return False
        
        processed_image = self.process_image(image)
        if not processed_image:
            logger.error("Failed to process image")
            return False
        
        # Check if image has changed
        image_hash = self.compute_image_hash(processed_image)
        if image_hash == self.last_image_hash:
            logger.info("Image unchanged, skipping display update")
            return False
        
        try:
            self.display.set_image(processed_image)
            self.display.show()
            self.last_image_hash = image_hash
            logger.info("Image displayed successfully")
            return True
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            return False
