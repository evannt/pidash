import threading
import time
import logging
from image_manager import ImageManager

logger = logging.getLogger(__name__)

class RefreshTask:
    """
    Handles background image rotation using threading.
    Core component for automatic image cycling.
    """
    def __init__(self, config, display_manager):
        self.config = config
        self.display_manager = display_manager
        self.image_manager = ImageManager(config)
        
        self.thread = None
        self.lock = threading.Lock()
        self.running = False
        self.condition = threading.Condition()
    
    def start(self):
        """Start the background refresh task."""
        if self.thread and self.thread.is_alive():
            logger.warning("Rotation task already running")
            return
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.running = True
        self.thread.start()
        logger.info("Refresh task started")
    
    def stop(self):
        """Stop the refresh task."""
        with self.condition:
            self.running = False
            self.condition.notify_all()
        
        if self.thread:
            self.thread.join()
            logger.info("Refresh task stopped")
    
    def trigger_immediate_refresh(self):
        """Trigger immediate image refresh (useful for web interface)."""
        with self.condition:
            self.condition.notify_all()
    
    def _run(self):
        """
        Background refresh loop.
        This is the heart of the automatic image cycling.
        """
        logger.info("Starting refresh loop")
        
        while self.running:
            try:
                sleep_time = self.config.get("sleep_time", 3600)

                if not self.running:
                    break

                self.image_manager.refresh_image_list()
                
                if self.image_manager.get_image_count() == 0:
                    logger.warning("No images available for display. Monitoring for changes...")
                else:
                    self.display_next_image()
                
                with self.condition:
                    if self.running:
                        self.condition.wait(timeout=sleep_time)
                
            except Exception as e:
                logger.exception("Error in rotation loop")
                time.sleep(10)

    def display_next_image(self):
        image = self.image_manager.get_next_image()

        if image:
            self.display_manager.display_image(image)