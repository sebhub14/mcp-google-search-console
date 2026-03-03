"""Secure configuration handling.

This module handles all configuration including the sensitive OAuth credentials.
Tokens are stored as SecretStr to prevent accidental logging.
"""

import logging
import os

from pydantic import SecretStr

from .errors import ConfigurationError

logger = logging.getLogger(__name__)

TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
WEBMASTERS_BASE_URL = "https://www.googleapis.com/webmasters/v3"
INSPECTION_BASE_URL = "https://searchconsole.googleapis.com/v1"


class Config:
    """Secure configuration handling.

    OAuth credentials are stored as SecretStr and should only be accessed
    via properties when actually needed for token exchange.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables.

        Raises:
            ConfigurationError: If required environment variables are missing.
        """
        client_id = os.environ.get("GSC_CLIENT_ID")
        if not client_id:
            raise ConfigurationError(
                "GSC_CLIENT_ID environment variable required. "
                "Set this to your Google Cloud OAuth client ID."
            )

        client_secret = os.environ.get("GSC_CLIENT_SECRET")
        if not client_secret:
            raise ConfigurationError(
                "GSC_CLIENT_SECRET environment variable required. "
                "Set this to your Google Cloud OAuth client secret."
            )

        refresh_token = os.environ.get("GSC_REFRESH_TOKEN")
        if not refresh_token:
            raise ConfigurationError(
                "GSC_REFRESH_TOKEN environment variable required. "
                "Obtain via OAuth consent flow with webmasters scope."
            )

        self._client_id = SecretStr(client_id)
        self._client_secret = SecretStr(client_secret)
        self._refresh_token = SecretStr(refresh_token)

        logger.info("Configuration loaded successfully")

    @property
    def client_id(self) -> str:
        """Get OAuth client ID."""
        return self._client_id.get_secret_value()

    @property
    def client_secret(self) -> str:
        """Get OAuth client secret."""
        return self._client_secret.get_secret_value()

    @property
    def refresh_token(self) -> str:
        """Get OAuth refresh token."""
        return self._refresh_token.get_secret_value()

    @property
    def token_endpoint(self) -> str:
        """Google OAuth2 token endpoint."""
        return TOKEN_ENDPOINT

    @property
    def webmasters_base_url(self) -> str:
        """Base URL for Sites, Analytics, and Sitemaps APIs."""
        return WEBMASTERS_BASE_URL

    @property
    def inspection_base_url(self) -> str:
        """Base URL for URL Inspection API."""
        return INSPECTION_BASE_URL

    def __repr__(self) -> str:
        """Safe repr that never exposes credentials."""
        return "Config(client_id=***, client_secret=***, refresh_token=***)"

    def __str__(self) -> str:
        """Safe str that never exposes credentials."""
        return "Config(client_id=***, client_secret=***, refresh_token=***)"


_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    This function lazily initializes the configuration on first call.
    Subsequent calls return the same instance.

    Returns:
        The global Config instance.

    Raises:
        ConfigurationError: If configuration is invalid.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
