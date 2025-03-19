"""Logging configuration for the application."""


class Logger:
    """Custom logger class with configurable output."""

    def __init__(self, name: str, level: Optional[int] = None):
        self.logger = logging.getLogger(name)
        self.level = level or logging.INFO
        self._configure()

    def _configure(self):
        """Configure the logger with handlers and formatting."""
        self.logger.setLevel(self.level)

        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self.level)

            # Create formatter
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(msg, *args, **kwargs)


def get_logger(name: str, level: Optional[int] = None) -> Logger:
    """Get a configured logger instance."""
    return Logger(name, level)


# Create default logger instance
logger = Logger(__name__)

__all__ = ["Logger", "logger", "get_logger"]
