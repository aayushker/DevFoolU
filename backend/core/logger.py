"""Logging configuration for the backend"""

import logging
import re
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from .config import settings


REDACTION_PATTERNS = (
    (re.compile(r"(mongodb(?:\+srv)?://)([^:/\s]+):([^@/\s]+)@", re.IGNORECASE), r"\1***:***@"),
    (re.compile(r"(api_key:)([A-Za-z0-9_-]+)", re.IGNORECASE), r"\1***"),
    (re.compile(r"AIza[0-9A-Za-z_-]{20,}"), "AIza***"),
)


class RedactingFormatter(logging.Formatter):
    """Formatter that masks common credential patterns in log messages."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in REDACTION_PATTERNS:
            message = pattern.sub(replacement, message)
        return message


def setup_logging() -> logging.Logger:
    """
    Setup comprehensive logging for the application
    Logs to both file and console with different formats
    """
    
    # Create logs directory if it doesn't exist
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("DevFoolU")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with colored output (if available)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = RedactingFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler with detailed information
    log_file = settings.LOGS_DIR / f"api_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = RedactingFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logging()
