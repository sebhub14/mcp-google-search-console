"""Google Search Console API client with OAuth2 token management.

This module provides a secure async HTTP client for the Search Console API.
Handles automatic OAuth2 token refresh and dual base URL routing.
"""

import logging
import time
from typing import Any

import httpx

from .config import get_config
from .errors import (
    PermissionDeniedError,
    RateLimitError,
    SearchConsoleApiError,
    SiteNotFoundError,
)

logger = logging.getLogger(__name__)

MAX_RESPONSE_SIZE = 10 * 1024 * 1024
REQUEST_TIMEOUT = 30.0
TOKEN_REFRESH_BUFFER = 60


def _parse_error_body(response: httpx.Response) -> str:
    """Extract a human-readable error message from an API error response."""
    try:
        error_body = response.json()
    except ValueError:
        return response.text[:200] if response.text else "Unknown error"

    if not isinstance(error_body, dict):
        return str(error_body)

    error_detail = error_body.get("error", {})
    if isinstance(error_detail, dict):
        return str(error_detail.get("message", str(error_detail)))
    if isinstance(error_detail, str):
        return error_detail
    return str(error_body)


class SearchConsoleClient:
    """Async HTTP client for Google Search Console API.

    Security features:
    - OAuth2 token refresh with expiry tracking
    - Bearer token auth (never in URL)
    - TLS certificate validation (httpx default)
    - Request timeout enforcement
    - Response size limits
    - Dual base URL routing (webmasters vs inspection)
    """

    def __init__(self) -> None:
        """Initialize the Search Console client."""
        self._config = get_config()
        self._client: httpx.AsyncClient | None = None
        self._access_token: str | None = None
        self._token_expires_at: float = 0.0

    async def _ensure_token(self) -> None:
        """Exchange refresh_token for access_token, cache until expiry."""
        if (
            self._access_token
            and time.time() < self._token_expires_at - TOKEN_REFRESH_BUFFER
        ):
            return

        async with httpx.AsyncClient(timeout=httpx.Timeout(REQUEST_TIMEOUT)) as token_client:
            response = await token_client.post(
                self._config.token_endpoint,
                data={
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                    "refresh_token": self._config.refresh_token,
                    "grant_type": "refresh_token",
                },
            )

        if not response.is_success:
            raise SearchConsoleApiError(
                response.status_code,
                f"Token refresh failed: {response.text[:200]}",
            )

        token_data = response.json()
        self._access_token = token_data["access_token"]
        self._token_expires_at = time.time() + token_data.get("expires_in", 3600)
        logger.debug("OAuth2 token refreshed, expires in %ds", token_data.get("expires_in", 3600))

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client with current Bearer token."""
        await self._ensure_token()

        if self._client is not None:
            self._client.headers["Authorization"] = f"Bearer {self._access_token}"
            return self._client

        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(REQUEST_TIMEOUT),
        )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _send(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        params: dict[str, Any] | None,
        json_data: dict[str, Any] | None,
    ) -> httpx.Response:
        """Send a single HTTP request with error wrapping."""
        try:
            return await client.request(
                method=method, url=url, params=params, json=json_data,
            )
        except httpx.TimeoutException as e:
            raise SearchConsoleApiError(0, f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise SearchConsoleApiError(0, f"Request failed: {e}") from e

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request with error handling and token retry.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: Full API URL
            params: Query parameters
            json_data: JSON body data

        Returns:
            API response data

        Raises:
            SearchConsoleApiError: On API errors
            RateLimitError: On rate limiting
            PermissionDeniedError: On authorization failures
        """
        client = await self._get_client()
        logger.debug("API request: %s %s", method, url)

        response = await self._send(client, method, url, params, json_data)

        if response.status_code == 401:
            self._access_token = None
            self._token_expires_at = 0.0
            client = await self._get_client()
            response = await self._send(client, method, url, params, json_data)

        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_RESPONSE_SIZE:
            raise SearchConsoleApiError(0, "Response too large")

        if not response.is_success:
            self._handle_error_response(response)

        if response.status_code == 204:
            return {"status": "deleted"}

        return self._parse_response(response)

    def _parse_response(self, response: httpx.Response) -> dict[str, Any]:
        """Parse a successful JSON response."""
        try:
            parsed = response.json()
        except ValueError as e:
            raise SearchConsoleApiError(
                response.status_code, f"Invalid JSON response: {e}"
            ) from e

        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"items": parsed}
        return {"data": parsed}

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        error_msg = _parse_error_body(response)

        match response.status_code:
            case 401:
                raise PermissionDeniedError("Invalid or expired OAuth2 credentials")
            case 403:
                raise PermissionDeniedError(error_msg)
            case 404:
                raise SiteNotFoundError(error_msg)
            case 429:
                retry_after = response.headers.get("retry-after")
                raise RateLimitError(int(retry_after) if retry_after else None)
            case _:
                raise SearchConsoleApiError(response.status_code, error_msg)

    def _webmasters_url(self, path: str) -> str:
        """Build a full URL for the webmasters API."""
        return f"{self._config.webmasters_base_url}{path}"

    def _inspection_url(self, path: str) -> str:
        """Build a full URL for the inspection API."""
        return f"{self._config.inspection_base_url}{path}"

    async def webmasters_get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a GET request to the webmasters API."""
        return await self._request("GET", self._webmasters_url(path), params=params)

    async def webmasters_post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the webmasters API."""
        return await self._request("POST", self._webmasters_url(path), json_data=json_data)

    async def webmasters_put(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a PUT request to the webmasters API."""
        return await self._request("PUT", self._webmasters_url(path), json_data=json_data)

    async def webmasters_delete(self, path: str) -> dict[str, Any]:
        """Make a DELETE request to the webmasters API."""
        return await self._request("DELETE", self._webmasters_url(path))

    async def inspection_post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the inspection API."""
        return await self._request("POST", self._inspection_url(path), json_data=json_data)


_client: SearchConsoleClient | None = None


def get_client() -> SearchConsoleClient:
    """Get the global Search Console client instance."""
    global _client
    if _client is None:
        _client = SearchConsoleClient()
    return _client
