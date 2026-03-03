# Baseline Specification: mcp-google-search-console-crunchtools

> **Spec ID:** 000-baseline
> **Status:** Implemented
> **Version:** 0.1.0

## Overview

mcp-google-search-console-crunchtools is a secure MCP server for the Google Search Console API. It provides 10 tools across 4 categories for querying search analytics, managing sitemaps, inspecting URL index status, and managing site properties. Authenticates via OAuth2 with refresh tokens.

---

## Tool Inventory

### Sites (4 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_sites` | GET | `/sites` | List all Search Console properties |
| `get_site` | GET | `/sites/{siteUrl}` | Get details for a specific property |
| `add_site` | PUT | `/sites/{siteUrl}` | Add a site to Search Console |
| `delete_site` | DELETE | `/sites/{siteUrl}` | Remove a site from Search Console |

### Search Analytics (1 tool)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `query_search_analytics` | POST | `/sites/{siteUrl}/searchAnalytics/query` | Query search traffic data |

### Sitemaps (4 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_sitemaps` | GET | `/sites/{siteUrl}/sitemaps` | List all sitemaps for a site |
| `get_sitemap` | GET | `/sites/{siteUrl}/sitemaps/{feedpath}` | Get sitemap details |
| `submit_sitemap` | PUT | `/sites/{siteUrl}/sitemaps/{feedpath}` | Submit a sitemap |
| `delete_sitemap` | DELETE | `/sites/{siteUrl}/sitemaps/{feedpath}` | Remove a sitemap |

### URL Inspection (1 tool)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `inspect_url` | POST | `/urlInspection/index:inspect` | Inspect URL index status |

---

## API Architecture

Two base URLs:
- `https://www.googleapis.com/webmasters/v3` — Sites, Analytics, Sitemaps
- `https://searchconsole.googleapis.com/v1` — URL Inspection

Auth: OAuth2 Bearer token from refresh token exchange via `https://oauth2.googleapis.com/token`

---

## Security Architecture

See `SECURITY.md` for the full threat model and defense-in-depth layers.

---

## Module Structure

```
src/mcp_google_search_console_crunchtools/
  __init__.py          # argparse, port 8017
  __main__.py          # python -m entry point
  server.py            # FastMCP + 10 @mcp.tool() wrappers
  client.py            # OAuth2 token refresh + dual base URL
  config.py            # GSC_CLIENT_ID/SECRET/REFRESH_TOKEN
  errors.py            # UserError hierarchy
  models.py            # Pydantic validation
  tools/
    __init__.py        # Re-exports
    sites.py           # 4 tools
    analytics.py       # 1 tool
    sitemaps.py        # 4 tools
    inspection.py      # 1 tool
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-03-03 | Initial implementation (10 tools) |
