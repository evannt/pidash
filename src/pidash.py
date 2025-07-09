#!/usr/bin/env python3

import logging
import time
from config import Config
from refresh_task import RefreshTask
from display_manager import DisplayManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("Running PiDash")

def main():
    try:
        config = Config()
        display_manager = DisplayManager(config)
        refresh_task = RefreshTask(config, display_manager)
        refresh_task.start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        refresh_task.stop()
    except Exception as e:
        logger.exception("Fatal error in main loop")

if __name__ == "__main__":
    main()
