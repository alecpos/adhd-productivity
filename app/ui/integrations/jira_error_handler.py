"""
Jira Error Handler Module

This module provides specialized error handling for Jira API interactions.
"""

import logging
import traceback
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


class JiraErrorHandler:
    """Specialized error handling for Jira API interactions."""
    
    def __init__(self, logger=None):
        """
        Initialize the Jira error handler.
        
        Args:
            logger: Optional custom logger to use
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_categories = {
            "authentication": 0,
            "permission": 0,
            "not_found": 0,
            "rate_limit": 0,
            "server": 0,
            "network": 0,
            "timeout": 0,
            "parsing": 0,
            "validation": 0,
            "other": 0
        }
    
    def handle_error(self, message: str, exception: Exception, reraise: bool = False) -> None:
        """
        Handle Jira API errors with proper logging and classification.
        
        Args:
            message: Context message for the error
            exception: The exception that occurred
            reraise: Whether to re-raise the exception after handling
        """
        error_msg = f"{message}: {str(exception)}"
        self.logger.error(error_msg)
        
        # Log detailed stack trace in debug mode
        self.logger.debug(f"Stack trace: {traceback.format_exc()}")
        
        # Classify and handle specific error types
        self._classify_error(exception)
        
        if reraise:
            raise exception
    
    def _classify_error(self, exception: Exception) -> str:
        """
        Classify error by type and provide specific handling.
        
        Args:
            exception: The exception to classify
            
        Returns:
            Error category string
        """
        # Check for HTTP status code errors first
        if hasattr(exception, "status"):
            return self._handle_http_error(getattr(exception, "status"), str(exception).lower())
        
        # Use error type mapping for other error types
        error_type_map = [
            (self._is_timeout_error, "timeout", self._handle_timeout_error),
            (self._is_connection_error, "network", self._handle_connection_error),
            (self._is_json_error, "parsing", self._handle_json_error),
            (self._is_validation_error, "validation", self._handle_validation_error)
        ]
        
        for checker, category, handler in error_type_map:
            if checker(exception):
                handler(exception)
                return category
        
        # Default case
        self._handle_generic_error(exception)
        return "other"
    
    def _is_timeout_error(self, exception: Exception) -> bool:
        """Check if the exception is a timeout error."""
        return "timeout" in str(exception).lower()
    
    def _is_connection_error(self, exception: Exception) -> bool:
        """Check if the exception is a connection error."""
        return "connection" in str(exception).lower()
    
    def _is_json_error(self, exception: Exception) -> bool:
        """Check if the exception is a JSON parse error."""
        return isinstance(exception, json.JSONDecodeError)
    
    def _is_validation_error(self, exception: Exception) -> bool:
        """Check if the exception is a validation error."""
        return isinstance(exception, ValueError) and "validation" in str(exception).lower()
    
    def _handle_http_error(self, status: int, error_str: str) -> str:
        """
        Handle HTTP response errors.
        
        Args:
            status: HTTP status code
            error_str: Error message string
            
        Returns:
            Error category string
        """
        # Use a dictionary to map status codes to handlers
        status_handlers = {
            401: ("Authentication failed. Please check credentials.", "authentication"),
            403: ("Permission denied. User lacks necessary permissions.", "permission"),
            404: ("Resource not found. Please check IDs and paths.", "not_found"),
            429: ("Rate limit exceeded. Implementing backoff and retry logic.", "rate_limit")
        }
        
        # Handle specific status codes
        if status in status_handlers:
            message, category = status_handlers[status]
            self.logger.error(message)
            self.error_categories[category] += 1
            return category
        
        # Handle server errors (5xx)
        if status >= 500:
            self.logger.error("Jira server error. Please try again later.")
            self.error_categories["server"] += 1
            return "server"
        
        # Default for other status codes
        self.logger.error(f"HTTP error with status {status}.")
        self.error_categories["other"] += 1
        return "other"
    
    def _handle_connection_error(self, exception: Exception) -> None:
        """
        Handle connection errors.
        
        Args:
            exception: The connection exception
        """
        self.logger.error("Connection error. Please check network and Jira server status.")
        self.error_categories["network"] += 1
        
        # Add more specific guidance if possible
        error_str = str(exception).lower()
        if "dns" in error_str:
            self.logger.error("DNS resolution failed. Check the Jira URL for typos.")
        elif "refused" in error_str:
            self.logger.error("Connection refused. The server may be down or blocking connections.")
        elif "reset" in error_str:
            self.logger.error("Connection reset. The server closed the connection unexpectedly.")
    
    def _handle_timeout_error(self, exception: Exception) -> None:
        """
        Handle timeout errors.
        
        Args:
            exception: The timeout exception
        """
        self.logger.error("Request timed out. Jira server might be overloaded.")
        self.error_categories["timeout"] += 1
        self.logger.error("Consider increasing timeout values or implementing retries.")
    
    def _handle_json_error(self, exception: json.JSONDecodeError) -> None:
        """
        Handle JSON parsing errors.
        
        Args:
            exception: The JSON decode exception
        """
        self.logger.error(f"Invalid JSON response: {str(exception)}")
        self.error_categories["parsing"] += 1
        self.logger.error(f"Error at position {exception.pos}: {exception.msg}")
    
    def _handle_validation_error(self, exception: Exception) -> None:
        """
        Handle data validation errors.
        
        Args:
            exception: The validation exception
        """
        self.logger.error(f"Validation error: {str(exception)}")
        self.error_categories["validation"] += 1
        
    def _handle_generic_error(self, exception: Exception) -> None:
        """
        Handle other types of errors.
        
        Args:
            exception: The exception to handle
        """
        self.logger.error(f"Unexpected error: {str(exception)}")
        self.error_categories["other"] += 1
    
    def get_error_stats(self) -> Dict[str, int]:
        """
        Get statistics on encountered error categories.
        
        Returns:
            Dictionary of error categories and counts
        """
        return self.error_categories
    
    def reset_stats(self) -> None:
        """Reset error statistics counters."""
        for category in self.error_categories:
            self.error_categories[category] = 0 