
from utils.logging import setup_logging
setup_logging()

import logging
logger = logging.getLogger("weather")

import os
import sys

from api import KNMI


def main():
    knmi = KNMI()

    latest_file = knmi.latest_file_name()
    if latest_file is None:
        sys.exit()


    logger.info(f"Latest file name: {latest_file}. Downloading...")
    
    try:
        knmi.download(latest_file)
    except KeyboardInterrupt:
        sys.exit()

    logger.info("Done.")


if __name__ == "__main__":
    main()