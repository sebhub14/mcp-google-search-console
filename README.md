# mcp-google-search-console-crunchtools

Secure MCP server for Google Search Console. Query search analytics (clicks, impressions, CTR, position), manage sitemaps, inspect URL indexing status, and manage site properties.

[![CI](https://github.com/crunchtools/mcp-google-search-console/actions/workflows/ci.yml/badge.svg)](https://github.com/crunchtools/mcp-google-search-console/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mcp-google-search-console-crunchtools)](https://pypi.org/project/mcp-google-search-console-crunchtools/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Installation

### uvx (recommended, zero-install)

```bash
claude mcp add mcp-google-search-console-crunchtools \
    --env GSC_CLIENT_ID=your_client_id \
    --env GSC_CLIENT_SECRET=your_client_secret \
    --env GSC_REFRESH_TOKEN=your_refresh_token \
    -- uvx mcp-google-search-console-crunchtools
```

### pip

```bash
pip install mcp-google-search-console-crunchtools
```

### Container (Podman/Docker)

```bash
podman run -d -p 8017:8017 \
    --env-file ~/.config/mcp-env/mcp-google-search-console.env \
    quay.io/crunchtools/mcp-google-search-console \
    --transport streamable-http --host 0.0.0.0
```

## OAuth Setup

This server uses OAuth2 with the Google Search Console API. You need:

1. A Google Cloud project with the Search Console API enabled
2. An OAuth 2.0 Client ID (Desktop application type)
3. A refresh token obtained via one-time consent flow

### Getting a Refresh Token

```bash
# 1. Set your client credentials
export GSC_CLIENT_ID="your_client_id"
export GSC_CLIENT_SECRET="your_client_secret"

# 2. Open this URL in a browser and authorize:
echo "https://accounts.google.com/o/oauth2/v2/auth?client_id=${GSC_CLIENT_ID}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=https://www.googleapis.com/auth/webmasters&access_type=offline"

# 3. Exchange the authorization code for a refresh token:
curl -s -X POST https://oauth2.googleapis.com/token \
    -d "client_id=${GSC_CLIENT_ID}" \
    -d "client_secret=${GSC_CLIENT_SECRET}" \
    -d "code=YOUR_AUTH_CODE" \
    -d "grant_type=authorization_code" \
    -d "redirect_uri=urn:ietf:wg:oauth:2.0:oob" | python -m json.tool
```

## Available Tools (10)

| Category | Count | Tools |
|----------|------:|-------|
| Sites | 4 | list_sites, get_site, add_site, delete_site |
| Search Analytics | 1 | query_search_analytics |
| Sitemaps | 4 | list_sitemaps, get_sitemap, submit_sitemap, delete_sitemap |
| URL Inspection | 1 | inspect_url |

## Security

- OAuth2 credentials stored as `SecretStr` (never logged)
- Environment-variable-only credential storage
- Automatic token scrubbing from error messages
- Pydantic input validation with `extra="forbid"`
- No filesystem access, shell execution, or code evaluation
- TLS certificate validation (httpx default)
- Request timeouts and response size limits
- Built on [Hummingbird](https://github.com/hummingbird-project) container images

See [SECURITY.md](SECURITY.md) for the full security design document.

## Development

```bash
uv sync --all-extras
uv run ruff check src tests
uv run mypy src
uv run pytest -v
gourmand --full .
podman build -f Containerfile .
```

## License

[AGPL-3.0-or-later](LICENSE)
