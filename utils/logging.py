
import logging


def setup_logging():
    logger = logging.getLogger("weather")
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(LoggingFormat())
    logger.addHandler(sh)


class LoggingFormat(logging.Formatter):
    """Custom logging format."""
    grey = "\x1b[90;20m"
    white = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    process_format = "(p: %(process)d) (t: %(thread)d) %(asctime)s - %(name)s:%(levelname)s - %(message)s"
    thread_format = "(t: %(thread)d) %(asctime)s - %(name)s:%(levelname)s - %(message)s"
    normal_format = "%(asctime)s - %(name)s:%(levelname)s - %(message)s"
    format = normal_format

    COLORED_FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: white + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }
    COLORLESS_FORMATS = {
        logging.DEBUG: format,
        logging.INFO: format,
        logging.WARNING: format,
        logging.ERROR: format,
        logging.CRITICAL: format
    }

    def format(self, record):
        log_fmt = self.COLORED_FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)