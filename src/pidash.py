#!/usr/bin/env python3

import logging
import time
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def main():
    app = create_app()
    logger.info("Starting PiDash webserver")
    app.run(host="0.0.0.0", port=80)

    try:
        app.config["refresh_manager"].start()

        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Fatal error in main loop")
    finally:
        app.config["refresh_manager"].stop()

if __name__ == "__main__":
    main()
