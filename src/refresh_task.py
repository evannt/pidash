import threading
import time
import logging

logger = logging.getLogger(__name__)

class RefreshTask:
    """
    Handles background image rotation using threading.
    Core component for automatic image cycling.
    """
    def __init__(self, config, image_manager, display_manager):
        self.config = config
        self.image_manager = image_manager
        self.display_manager = display_manager
        
        self.thread = None
        self.running = False
        self.condition = threading.Condition()
    
    def start(self):
        """Start the background rotation task."""
        if self.thread and self.thread.is_alive():
            logger.warning("Rotation task already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Rotation task started")
    
    def stop(self):
        """Stop the rotation task."""
        with self.condition:
            self.running = False
            self.condition.notify_all()
        
        if self.thread:
            self.thread.join(timeout=5)
            logger.info("Rotation task stopped")
    
    def trigger_immediate_rotation(self):
        """Trigger immediate image rotation (useful for web interface)."""
        with self.condition:
            self.condition.notify_all()
    
    def _run(self):
        """
        Background rotation loop.
        This is the heart of the automatic image cycling.
        """
        logger.info("Starting rotation loop")
        
        while self.running:
            try:
                # Get rotation interval
                interval = self.config.get('rotation_interval_seconds', 3600)
                
                # Refresh image list and display next image
                self.image_manager.refresh_image_list()
                
                if self.image_manager.get_image_count() == 0:
                    logger.warning("No images found, waiting...")
                else:
                    next_image = self.image_manager.get_next_image()
                    if next_image:
                        self.display_manager.display_image(next_image)
                
                # Wait for interval or until notified
                with self.condition:
                    if self.running:
                        self.condition.wait(timeout=interval)
                
            except Exception as e:
                logger.exception("Error in rotation loop")
                time.sleep(10)  # Brief pause before retrying
