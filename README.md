# mcp-google-search-console-crunchtools

<!-- mcp-name: io.github.crunchtools/google-search-console -->

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

This server authenticates to Google using OAuth2 with a **refresh token**. This is a one-time setup — once you have the three credentials, you store them as environment variables and never need to touch OAuth again.

### What you need

| Credential | What it is | Where it comes from |
|------------|-----------|-------------------|
| `GSC_CLIENT_ID` | Identifies your OAuth app to Google | Google Cloud Console |
| `GSC_CLIENT_SECRET` | Secret key for your OAuth app | Google Cloud Console |
| `GSC_REFRESH_TOKEN` | Long-lived token that lets the server get access tokens | One-time browser consent flow |

### Step 1: Create a Google Cloud OAuth App

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services > Library**
4. Search for **Google Search Console API** and click **Enable**
5. Navigate to **APIs & Services > Credentials**
6. Click **+ CREATE CREDENTIALS > OAuth client ID**
7. If prompted, configure the OAuth consent screen first:
   - User type: **External** (or Internal if using Google Workspace)
   - App name: anything (e.g., "MCP Search Console")
   - Scopes: add `https://www.googleapis.com/auth/webmasters`
   - Test users: add your Google account email
8. Back on Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: anything (e.g., "MCP Search Console Desktop")
9. Click **Create** — copy the **Client ID** and **Client Secret**

### Step 2: Get a Refresh Token

Run this in your terminal to start the consent flow:

```bash
# Set your credentials from Step 1
export GSC_CLIENT_ID="your_client_id_here"
export GSC_CLIENT_SECRET="your_client_secret_here"

# Generate the authorization URL
echo "Open this URL in your browser:"
echo ""
echo "https://accounts.google.com/o/oauth2/v2/auth?client_id=${GSC_CLIENT_ID}&redirect_uri=http://127.0.0.1&response_type=code&scope=https://www.googleapis.com/auth/webmasters&access_type=offline&prompt=consent"
```

1. Open the printed URL in your browser
2. Sign in with the Google account that owns your Search Console properties
3. Click **Allow** to grant Search Console access
4. The browser will redirect to `http://127.0.0.1/?code=XXXX&scope=...`
5. **This page will fail to load — that's expected.** Copy the `code=` value from the URL bar (everything between `code=` and `&scope`)

Now exchange the authorization code for a refresh token:

```bash
# Paste the code value from the URL bar (the part between code= and &scope)
AUTH_CODE="paste_your_code_here"

curl -s -X POST https://oauth2.googleapis.com/token \
    -d "client_id=${GSC_CLIENT_ID}" \
    -d "client_secret=${GSC_CLIENT_SECRET}" \
    -d "code=${AUTH_CODE}" \
    -d "grant_type=authorization_code" \
    -d "redirect_uri=http://127.0.0.1" | python3 -m json.tool
```

The response will include a `refresh_token` field — copy it. This is the long-lived credential that lets the server authenticate without a browser.

> **Note:** If you don't see `refresh_token` in the response, add `&prompt=consent` to the authorization URL and try again. Google only returns the refresh token on the first consent or when explicitly prompted.

### Step 3: Store the Credentials

Create an env file:

```bash
cat > ~/.config/mcp-env/mcp-google-search-console.env << 'EOF'
GSC_CLIENT_ID=your_client_id
GSC_CLIENT_SECRET=your_client_secret
GSC_REFRESH_TOKEN=your_refresh_token
EOF
chmod 600 ~/.config/mcp-env/mcp-google-search-console.env
```

### How it works at runtime

The server never stores or manages tokens on disk. On each API call:
1. Server sends the refresh token to Google's token endpoint
2. Google returns a short-lived access token (valid ~1 hour)
3. Server uses the access token for the Search Console API call
4. Access tokens are cached in memory and refreshed automatically when they expire

The refresh token itself never expires unless you explicitly revoke it in your [Google Account permissions](https://myaccount.google.com/permissions).

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
