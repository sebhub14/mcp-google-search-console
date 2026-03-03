"""Shared test fixtures for mcp-google-search-console tests."""

import json
import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest


@pytest.fixture(autouse=True)
def _reset_singletons() -> Generator[None, None, None]:
    """Reset client and config singletons between tests."""
    os.environ["GSC_CLIENT_ID"] = "test_client_id"
    os.environ["GSC_CLIENT_SECRET"] = "test_client_secret"
    os.environ["GSC_REFRESH_TOKEN"] = "test_refresh_token"

    yield

    import mcp_google_search_console_crunchtools.client as client_module
    import mcp_google_search_console_crunchtools.config as config_module

    client_module._client = None
    config_module._config = None

    os.environ.pop("GSC_CLIENT_ID", None)
    os.environ.pop("GSC_CLIENT_SECRET", None)
    os.environ.pop("GSC_REFRESH_TOKEN", None)


def _mock_response(
    status_code: int = 200,
    json_data: Any = None,
    text: str = "",
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """Build a mock httpx.Response."""
    if json_data is not None:
        content = json.dumps(json_data).encode()
        content_type = "application/json"
    else:
        content = text.encode()
        content_type = "text/plain"

    resp_headers = {"content-type": content_type}
    if headers:
        resp_headers.update(headers)

    return httpx.Response(
        status_code=status_code,
        content=content,
        headers=resp_headers,
        request=httpx.Request("GET", "https://example.com"),
    )


@contextmanager
def _patch_client(
    response: httpx.Response,
) -> Generator[AsyncMock, None, None]:
    """Patch httpx.AsyncClient to return a mock response.

    Bypasses OAuth token exchange by patching _ensure_token and provides
    a mock client that returns the given response for API calls.
    """
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.request = AsyncMock(return_value=response)
    mock_client.aclose = AsyncMock()
    mock_client.headers = {}

    with (
        patch(
            "mcp_google_search_console_crunchtools.client.SearchConsoleClient._ensure_token",
            new_callable=AsyncMock,
        ),
        patch("httpx.AsyncClient", return_value=mock_client),
    ):
        yield mock_client
