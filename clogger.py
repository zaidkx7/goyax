import logging
from colorama import Fore, Style, init

init(autoreset=True)


class CustomFormatter(logging.Formatter):
    """Custom formatter for adding colors to logs."""
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.YELLOW,
        logging.WARNING: Fore.MAGENTA,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, "")
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"


def get_logger(log_file="scraper.log"):
    """Create and return a logger with colored output and file saving."""
    logger = logging.getLogger("scraper_logger")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = CustomFormatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
