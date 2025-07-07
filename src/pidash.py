#!/usr/bin/env python3

import logging
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
    config = Config()
    display_manager = DisplayManager(config)
    refresh_task = RefreshTask(config, display_manager)
    refresh_task.start()

if __name__ == "__main__":
    main()
