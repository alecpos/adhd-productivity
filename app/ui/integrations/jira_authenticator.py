"""
JiraAuthenticator module handles authentication with Atlassian Jira APIs.

This module contains the JiraAuthenticator class which is responsible for:
1. Authenticating with Jira using various authentication methods
2. Managing authentication tokens and credentials
3. Providing authentication headers for API requests
"""

import base64
import logging
import time
from typing import Dict, Optional, Tuple

from app.core.integrations.project_tool_config import ProjectToolConfig


class JiraAuthenticator:
    """
    Handles authentication with Atlassian Jira APIs.

    Supports both basic authentication and API token authentication methods.
    Manages authentication state and provides authentication headers for API requests.
    """

    def __init__(self, config: ProjectToolConfig):
        """
        Initialize the JiraAuthenticator with the given configuration.

        Args:
            config: ProjectToolConfig containing Jira connection settings
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.auth_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        self.authenticated = False
        self.auth_errors = 0

    async def authenticate(self) -> bool:
        """
        Authenticate with Jira using the configured authentication method.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        self.logger.info("Authenticating with Jira")

        # Check if we have a valid token already
        if self._is_token_valid():
            self.logger.debug("Using existing valid auth token")
            return True

        # Select the appropriate authentication method
        return await self._authenticate_with_configured_method()

    async def _authenticate_with_configured_method(self) -> bool:
        """
        Authenticate using the configured authentication method.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        auth_methods = {
            "basic": self._authenticate_basic,
            "token": self._authenticate_token,
            "oauth": self._authenticate_oauth,
        }

        # Check if the configured method is supported
        auth_method = self.config.auth_method
        if auth_method not in auth_methods:
            self.logger.error(f"Unsupported authentication method: {auth_method}")
            return False

        # Try to authenticate with the selected method
        try:
            auth_func = auth_methods[auth_method]
            # Handle both sync and async methods
            if auth_method == "oauth":
                return await auth_func()
            else:
                return auth_func()
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            self.auth_errors += 1
            self.authenticated = False
            return False

    def _authenticate_basic(self) -> bool:
        """
        Authenticate using basic authentication (username/password).

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if not self.config.username or not self.config.password:
            self.logger.error("Username or password missing for basic authentication")
            return False

        # Create credentials from username/password
        credentials = f"{self.config.username}:{self.config.password}"
        return self._set_auth_credentials(credentials, "Basic authentication")

    def _authenticate_token(self) -> bool:
        """
        Authenticate using API token authentication.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if not self.config.username or not self.config.api_token:
            self.logger.error("Username or API token missing for token authentication")
            return False

        # Create credentials from username/API token
        credentials = f"{self.config.username}:{self.config.api_token}"
        # API tokens last longer, so use 24 hour expiry
        return self._set_auth_credentials(credentials, "Token authentication", expiry_seconds=86400)

    def _set_auth_credentials(
        self, credentials: str, auth_type: str, expiry_seconds: int = 3600
    ) -> bool:
        """
        Encode credentials and set authentication token.

        Args:
            credentials: String containing credentials to encode
            auth_type: Authentication type for logging
            expiry_seconds: Token expiry time in seconds (default: 1 hour)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.auth_token = encoded_credentials
            self.token_expiry = time.time() + expiry_seconds
            self.authenticated = True
            self.logger.info(f"{auth_type} prepared successfully")
            return True
        except Exception as e:
            self.logger.error(f"{auth_type} preparation failed: {str(e)}")
            return False

    async def _authenticate_oauth(self) -> bool:
        """
        Authenticate using OAuth 2.0 flow.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        self.logger.warning("OAuth authentication not yet implemented")
        return False

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dict[str, str]: Dictionary containing authentication headers
        """
        # Check authentication status
        if not self.authenticated:
            self.logger.warning("Attempting to get auth headers when not authenticated")
            return {}

        # Base headers for all requests
        base_headers = {"Content-Type": "application/json"}

        # Add auth header based on auth method
        auth_header_value = self._get_auth_header_value()
        if auth_header_value:
            base_headers["Authorization"] = auth_header_value

        return base_headers

    def _get_auth_header_value(self) -> Optional[str]:
        """
        Get the appropriate authentication header value based on auth method.

        Returns:
            Optional[str]: Authorization header value or None if not available
        """
        if not self.auth_token:
            return None

        auth_method = self.config.auth_method
        if auth_method in ["basic", "token"]:
            return f"Basic {self.auth_token}"
        elif auth_method == "oauth":
            return f"Bearer {self.auth_token}"

        return None

    def _is_token_valid(self) -> bool:
        """
        Check if the current authentication token is valid.

        Returns:
            bool: True if token is valid, False otherwise
        """
        # Check if token exists
        if not self.auth_token or not self.token_expiry:
            return False

        # Check if not authenticated
        if not self.authenticated:
            return False

        # Check if token has expired
        current_time = time.time()
        if current_time >= self.token_expiry:
            self.logger.debug("Auth token has expired")
            return False

        return True

    def invalidate_token(self) -> None:
        """
        Invalidate the current authentication token.
        Useful when receiving authentication errors from the API.
        """
        self.logger.info("Invalidating authentication token")
        self.auth_token = None
        self.token_expiry = None
        self.authenticated = False

    async def refresh_token_if_needed(self) -> bool:
        """
        Check if the token needs refreshing and refresh it if necessary.

        Returns:
            bool: True if token is valid (either didn't need refresh or refresh was successful)
        """
        if self._is_token_valid():
            return True

        self.logger.info("Token needs refreshing, attempting to re-authenticate")
        return await self.authenticate()

    def handle_auth_error(self, status_code: int) -> bool:
        """
        Handle authentication-related error based on status code.

        Args:
            status_code: HTTP status code from the API response

        Returns:
            bool: True if the error was handled, False otherwise
        """
        if status_code == 401:  # Unauthorized
            self.logger.warning("Received 401 Unauthorized, invalidating token")
            self.invalidate_token()
            self.auth_errors += 1
            return True
        elif status_code == 403:  # Forbidden
            self.logger.warning("Received 403 Forbidden, may need permission adjustment")
            self.auth_errors += 1
            return True

        return False

    def get_status(self) -> Dict[str, object]:
        """
        Get the current authentication status.

        Returns:
            Dict[str, object]: Authentication status information
        """
        time_remaining = 0
        if self.authenticated and self.token_expiry:
            time_remaining = max(0, self.token_expiry - time.time())

        return {
            "authenticated": self.authenticated,
            "auth_method": self.config.auth_method,
            "token_valid": self._is_token_valid(),
            "token_expiry_seconds": round(time_remaining),
            "auth_errors": self.auth_errors,
            "last_authenticated": self.token_expiry - 3600 if self.token_expiry else None,
            "username": self.config.username if self.authenticated else None,
        }

    def get_health_metrics(self) -> Dict[str, object]:
        """
        Get health metrics for monitoring and debugging.

        Returns:
            Dict[str, object]: Health metrics dictionary
        """
        return {
            "is_healthy": self.authenticated and self._is_token_valid(),
            "auth_errors": self.auth_errors,
            "auth_method": self.config.auth_method,
            "token_time_remaining_seconds": (
                round(max(0, self.token_expiry - time.time())) if self.token_expiry else 0
            ),
        }
