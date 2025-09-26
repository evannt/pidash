import threading
import time
import logging

logger = logging.getLogger(__name__)

class RefreshManager:

    def __init__(self, config, image_manager, display_manager):
        self.config = config
        self.image_manager = image_manager
        self.display_manager = display_manager
        
        self.thread = None
        self.lock = threading.Lock()
        self.running = False
        self.condition = threading.Condition()
    
    def start(self):
        if self.thread and self.thread.is_alive():
            logger.warning("Rotation task already running")
            return
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.running = True
        self.thread.start()
        logger.info("Refresh task started")
    
    def stop(self):
        with self.condition:
            self.running = False
            self.condition.notify_all()
        
        if self.thread:
            self.thread.join()
            logger.info("Refresh task stopped")
    
    def trigger_immediate_refresh(self):
        with self.condition:
            self.condition.notify_all()
    
    def _run(self):
        logger.info("Starting refresh loop")
        
        while self.running:
            try:
                refresh_interval = self.config.get("refresh_interval", 3600)

                if not self.running:
                    break

                self.image_manager.refresh_image_list()
                
                if self.image_manager.get_image_count() == 0:
                    logger.warning("No images available for display. Monitoring for changes...")
                else:
                    self.display_next_image()
                
                with self.condition:
                    if self.running:
                        self.condition.wait(timeout=refresh_interval)
                
            except Exception as e:
                logger.exception(f"Error in refresh loop: {e}")
                time.sleep(10)

    def refresh_display(self):
        image = self.image_manager.get_current_image()

        if image:
            self.display_manager.display_image(image)
        else:
            logger.warning("Failed to refresh display.")

    def display_next_image(self):
        image = self.image_manager.get_next_image()
        self.image_manager.update_image_index()

        if image:
            self.display_manager.display_image(image)
        else:
            logger.warning("Failed to display next image.")

    def display_previous_image(self):
        image = self.image_manager.get_previous_image()
        self.image_manager.update_image_index(increment=False)

        if image:
            self.display_manager.display_image(image)
        else:
            logger.warning("Failed to display previous image.")
