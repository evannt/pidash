#!/usr/bin/env python3

import logging
from app import create_app
from constants import LOG_FORMAT, LOG_DATE_FORMAT, DEFAULT_HOST, DEFAULT_PORT

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)

def main():
    app = create_app()
    logger.info("Starting PiDash webserver")
    
    try:
        app.config["refresh_manager"].start()
        logger.info("Refresh manager started")
        app.run(host=DEFAULT_HOST, port=DEFAULT_PORT)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}")
    finally:
        logger.info("Stopping refresh manager...")
        app.config["refresh_manager"].stop()

if __name__ == "__main__":
    main()
