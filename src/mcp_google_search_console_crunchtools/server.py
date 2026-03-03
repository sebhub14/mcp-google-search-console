"""FastMCP server setup for Google Search Console MCP.

This module creates and configures the MCP server with all tools.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from .tools import (
    add_site,
    delete_site,
    delete_sitemap,
    get_site,
    get_sitemap,
    inspect_url,
    list_sitemaps,
    list_sites,
    query_search_analytics,
    submit_sitemap,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="mcp-google-search-console-crunchtools",
    version="0.1.0",
    instructions=(
        "Secure MCP server for Google Search Console. "
        "Query search analytics (clicks, impressions, CTR, position), "
        "manage sitemaps, inspect URL indexing status, and manage site properties."
    ),
)


@mcp.tool()
async def list_sites_tool() -> dict[str, Any]:
    """List all Search Console properties accessible by the authenticated user.

    Returns:
        List of site entries with permission levels and site URLs
    """
    return await list_sites()


@mcp.tool()
async def get_site_tool(
    site_url: str,
) -> dict[str, Any]:
    """Get details for a specific Search Console property.

    Args:
        site_url: Site URL (e.g., "https://example.com/") or domain property
                  (e.g., "sc-domain:example.com")

    Returns:
        Site details including permission level
    """
    return await get_site(site_url=site_url)


@mcp.tool()
async def add_site_tool(
    site_url: str,
) -> dict[str, Any]:
    """Add a site to Search Console.

    Args:
        site_url: Site URL (e.g., "https://example.com/") or domain property

    Returns:
        Confirmation of addition
    """
    return await add_site(site_url=site_url)


@mcp.tool()
async def delete_site_tool(
    site_url: str,
) -> dict[str, Any]:
    """Remove a site from Search Console.

    Args:
        site_url: Site URL to remove

    Returns:
        Confirmation of deletion
    """
    return await delete_site(site_url=site_url)


@mcp.tool()
async def query_search_analytics_tool(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str] | None = None,
    search_type: str = "web",
    aggregation_type: str = "auto",
    row_limit: int = 1000,
    start_row: int = 0,
    dimension_filter_groups: list[dict[str, list[dict[str, str]]]] | None = None,
    data_state: str = "final",
) -> dict[str, Any]:
    """Query search traffic data with filters and dimensions.

    Returns clicks, impressions, CTR, and average position grouped by
    the requested dimensions. Use this to analyze search performance
    for specific pages, queries, countries, devices, or date ranges.

    Args:
        site_url: Site URL or domain property
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        dimensions: Dimensions to group by (date, query, page, country,
                    device, searchAppearance). Multiple allowed.
        search_type: Search type filter (web, image, video, news,
                     googleNews, discover). Default: web
        aggregation_type: How to aggregate results (auto, byPage,
                          byProperty). Default: auto
        row_limit: Maximum rows to return, 1-25000 (default: 1000)
        start_row: Zero-based row offset for pagination (default: 0)
        dimension_filter_groups: Filter groups to narrow results
        data_state: Data freshness (final, all). Default: final

    Returns:
        Search analytics data with rows containing clicks, impressions,
        ctr, and position values
    """
    return await query_search_analytics(
        site_url=site_url,
        start_date=start_date,
        end_date=end_date,
        dimensions=dimensions,
        search_type=search_type,
        aggregation_type=aggregation_type,
        row_limit=row_limit,
        start_row=start_row,
        dimension_filter_groups=dimension_filter_groups,
        data_state=data_state,
    )


@mcp.tool()
async def list_sitemaps_tool(
    site_url: str,
) -> dict[str, Any]:
    """List all sitemaps submitted for a site.

    Args:
        site_url: Site URL or domain property

    Returns:
        List of sitemaps with status, type, and submission metadata
    """
    return await list_sitemaps(site_url=site_url)


@mcp.tool()
async def get_sitemap_tool(
    site_url: str,
    feedpath: str,
) -> dict[str, Any]:
    """Get details for a specific sitemap.

    Args:
        site_url: Site URL or domain property
        feedpath: Full URL of the sitemap (e.g., "https://example.com/sitemap.xml")

    Returns:
        Sitemap details including type, submission time, and index status
    """
    return await get_sitemap(site_url=site_url, feedpath=feedpath)


@mcp.tool()
async def submit_sitemap_tool(
    site_url: str,
    feedpath: str,
) -> dict[str, Any]:
    """Submit a sitemap for crawling.

    Args:
        site_url: Site URL or domain property
        feedpath: Full URL of the sitemap to submit (e.g., "https://example.com/sitemap.xml")

    Returns:
        Confirmation of submission
    """
    return await submit_sitemap(site_url=site_url, feedpath=feedpath)


@mcp.tool()
async def delete_sitemap_tool(
    site_url: str,
    feedpath: str,
) -> dict[str, Any]:
    """Remove a sitemap from Search Console.

    Args:
        site_url: Site URL or domain property
        feedpath: Full URL of the sitemap to delete

    Returns:
        Confirmation of deletion
    """
    return await delete_sitemap(site_url=site_url, feedpath=feedpath)


@mcp.tool()
async def inspect_url_tool(
    inspection_url: str,
    site_url: str,
    language_code: str = "en-US",
) -> dict[str, Any]:
    """Inspect a URL's index status in Google Search.

    Returns detailed information about how Google sees a URL including
    index coverage, crawl status, mobile usability, and rich results.

    Args:
        inspection_url: The fully-qualified URL to inspect
                        (e.g., "https://example.com/page")
        site_url: The Search Console property this URL belongs to
        language_code: Language code for localized results (default: en-US)

    Returns:
        URL inspection result with indexing, crawling, and mobile usability data
    """
    return await inspect_url(
        inspection_url=inspection_url,
        site_url=site_url,
        language_code=language_code,
    )
