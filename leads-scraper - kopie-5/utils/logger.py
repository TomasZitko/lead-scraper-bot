"""
Logging utility for the Czech Lead Scraper
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = "czech_scraper", verbose: bool = False) -> logging.Logger:
    """
    Set up and configure logger with file and console handlers

    Args:
        name: Logger name
        verbose: If True, set console logging to DEBUG level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # File handler - detailed logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"scraper_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler - colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = ColoredFormatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log error with context information

    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context about where the error occurred
    """
    error_msg = f"{context}: {type(error).__name__} - {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)


def log_progress(logger: logging.Logger, current: int, total: int, item: str = "items") -> None:
    """
    Log progress information

    Args:
        logger: Logger instance
        current: Current progress count
        total: Total count
        item: Name of items being processed
    """
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"Progress: {current}/{total} {item} ({percentage:.1f}%)")
