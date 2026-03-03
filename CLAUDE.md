# Claude Code Instructions

Secure MCP server for Google Search Console API with 10 tools across 4 categories. Query search analytics, manage sitemaps, inspect URL indexing, and manage site properties.

## Quick Start

```bash
# uvx (recommended)
claude mcp add mcp-google-search-console-crunchtools \
    --env GSC_CLIENT_ID=your_client_id \
    --env GSC_CLIENT_SECRET=your_client_secret \
    --env GSC_REFRESH_TOKEN=your_refresh_token \
    -- uvx mcp-google-search-console-crunchtools

# Container
claude mcp add mcp-google-search-console-crunchtools \
    -- podman run -i --rm \
    --env-file ~/.config/mcp-env/mcp-google-search-console.env \
    quay.io/crunchtools/mcp-google-search-console

# Local development
cd ~/Projects/crunchtools/mcp-google-search-console
claude mcp add mcp-google-search-console-crunchtools \
    --env GSC_CLIENT_ID=your_client_id \
    --env GSC_CLIENT_SECRET=your_client_secret \
    --env GSC_REFRESH_TOKEN=your_refresh_token \
    -- uv run mcp-google-search-console-crunchtools
```

## OAuth Setup

1. Go to Google Cloud Console > APIs & Services > Credentials
2. Create or reuse an OAuth 2.0 Client ID (Desktop application type)
3. Enable the Search Console API under APIs & Services > Library
4. Run a one-time consent flow to obtain a refresh_token with `https://www.googleapis.com/auth/webmasters` scope
5. Store the client ID, client secret, and refresh token as environment variables

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GSC_CLIENT_ID` | Yes | Google Cloud OAuth client ID |
| `GSC_CLIENT_SECRET` | Yes | Google Cloud OAuth client secret |
| `GSC_REFRESH_TOKEN` | Yes | OAuth refresh token with webmasters scope |

## Available Tools (10)

| Category | Tools | Operations |
|----------|------:|------------|
| Sites | 4 | list, get, add, delete |
| Search Analytics | 1 | query (clicks, impressions, CTR, position) |
| Sitemaps | 4 | list, get, submit, delete |
| URL Inspection | 1 | inspect (index status, crawl, mobile) |

Full tool inventory with API endpoints: `.specify/specs/000-baseline/spec.md`

## Example Usage

```
List my Search Console properties
Show search analytics for crunchtools.com last 7 days
What are the top queries for crunchtools.com this month?
Show CTR by page for educatedconfusion.com
List sitemaps for crunchtools.com
Check if https://crunchtools.com/blog/post is indexed
Submit a new sitemap for crunchtools.com
```

## Development

```bash
uv sync --all-extras          # Install dependencies
uv run ruff check src tests   # Lint
uv run mypy src               # Type check
uv run pytest -v              # Tests (mocked)
gourmand --full .              # AI slop detection (zero violations)
```

Quality gates, testing standards, and architecture: `.specify/memory/constitution.md`
