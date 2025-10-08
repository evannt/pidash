#!/usr/bin/env python3

import socket
import logging
from app import create_app
from waitress import serve
from constants import LOG_FORMAT, LOG_DATE_FORMAT, DEFAULT_HOST, DEFAULT_PORT, REFRESH_MANAGER_KEY, CONFIG_KEY, HOSTNAME_KEY, LOCAL_IP_KEY

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)
logger = logging.getLogger(__name__)

def get_network_info():
    hostname = socket.gethostname()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
    
    return hostname, local_ip
def main():
    app = create_app()
    logger.info("Starting PiDash webserver")
    
    hostname, local_ip = get_network_info()

    app.config[CONFIG_KEY].set(HOSTNAME_KEY, hostname)
    app.config[CONFIG_KEY].set(LOCAL_IP_KEY, local_ip)
    
    try:
        app.config[REFRESH_MANAGER_KEY].start()
        logger.info("Refresh manager started")

        logger.info("Running in production mode with Waitress")
        logger.info(f"Access at: http://{local_ip}:{DEFAULT_PORT} or http://{hostname}:{DEFAULT_PORT}")
        serve(app, 
                host=DEFAULT_HOST, 
                port=DEFAULT_PORT,
                threads=4,
                connection_limit=100)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main loop: {e}")
    finally:
        logger.info("Stopping refresh manager...")
        app.config[REFRESH_MANAGER_KEY].stop()

if __name__ == "__main__":
    main()
