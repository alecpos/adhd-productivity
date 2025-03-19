"""
Logging Utilities

This module provides standardized logging configuration for the ADHD Calendar API.
"""

import logging
import sys
from typing import Optional

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: The name of the logger. Defaults to the root logger.
    
    Returns:
        A configured logger
    """
    logger = logging.getLogger(name)
    return logger


def configure_logger(
    logger: logging.Logger,
    level: int = logging.INFO,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """
    Configure a logger with the specified level and format.
    
    Args:
        logger: The logger to configure
        level: The logging level (default: INFO)
        format_str: The log format string
    """
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add a new handler with the specified format
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_request_logger() -> logging.Logger:
    """
    Get a logger for request handling.
    
    Returns:
        A configured logger for request handling
    """
    logger = get_logger("app.request")
    return logger


def get_error_logger() -> logging.Logger:
    """
    Get a logger for error handling.
    
    Returns:
        A configured logger for error handling
    """
    logger = get_logger("app.error")
    return logger 