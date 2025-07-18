import logging
from image_utils import resize_image, change_orientation, apply_image_enhancement
from PIL import Image
from inky.auto import auto

logger = logging.getLogger(__name__)

class DisplayManager:

    def __init__(self, config):
        self.config = config
        self.initialize_display()
    
    def initialize_display(self):
        self.inky_display = auto()
        self.inky_display.set_border(self.inky_display.BLACK)
        logger.info(f"Inky display initialized: {self.inky_display.width}x{self.inky_display.height}")
        if not self.config.get("resolution"):
            self.config.set("resolution", [int(self.inky_display.width), int(self.inky_display.height)], save=True)

    def display_image(self, image, image_settings=[]):
        logger.info("Displaying image to Inky display.")
        if not image:
            raise ValueError(f"No image provided.")
        
        image = change_orientation(image, self.config.get("orientation"))
        image = resize_image(image, self.config.get("resolution"), image_settings)
        if self.config.get("inverted_image"): image = image.rotate(180)
        image = apply_image_enhancement(image, self.config.get("image_settings"))

        try:
            self.inky_display.set_image(image)
            self.inky_display.show()
        except Exception as e:
            logger.error(f"Failed to display image: {e}")
