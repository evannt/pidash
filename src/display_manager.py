import logging
from src.image_utils import resize_image, change_orientation, apply_image_enhancement
from PIL import Image
from inky.auto import auto
from src.config import Config
from src.constants import (
    RESOLUTION_KEY, ORIENTATION_KEY, INVERTED_IMAGE_KEY, IMAGE_SETTINGS_KEY
)

logger = logging.getLogger(__name__)

class DisplayManager:

    def __init__(self, config: Config):
        self.config = config
        self.initialize_display()
    
    def initialize_display(self):
        self.inky_display = auto()
        self.inky_display.set_border(self.inky_display.BLACK)
        logger.info(f"Inky display initialized: {self.inky_display.width}x{self.inky_display.height}")
        if not self.config.get(RESOLUTION_KEY):
            self.config.set(RESOLUTION_KEY, [int(self.inky_display.width), int(self.inky_display.height)], save=True)

    def display_image(self, image: Image.Image, image_settings=[]):
        logger.info("Displaying image to Inky display.")
        if not image:
            raise ValueError(f"No image provided.")
        
        try:
            image = change_orientation(image, self.config.get(ORIENTATION_KEY))
            image = resize_image(image, self.config.get(RESOLUTION_KEY), image_settings)
            if self.config.get(INVERTED_IMAGE_KEY, False): 
                image = image.rotate(180)
            image = apply_image_enhancement(image, self.config.get(IMAGE_SETTINGS_KEY))

            self.inky_display.set_image(image)
            self.inky_display.show()
            logger.info("Image displayed successfully")
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
            raise
