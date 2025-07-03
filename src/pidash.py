#!/usr/bin/env python3

"""
Image Slideshow for Raspberry Pi Zero 2 W + Inky Impression
Rotates through images in a folder at configurable intervals.
Designed to be extensible for future web server functionality.
"""

import logging
from slideshow import SlideShow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Running PiDash")


if __name__ == "__main__":
    app = SlideShow()
    app.run()
