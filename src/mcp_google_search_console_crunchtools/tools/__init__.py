"""Google Search Console MCP tools.

This package contains all the MCP tool implementations for Search Console operations.
"""

from .analytics import query_search_analytics
from .inspection import inspect_url
from .sitemaps import delete_sitemap, get_sitemap, list_sitemaps, submit_sitemap
from .sites import add_site, delete_site, get_site, list_sites

__all__ = [
    "list_sites",
    "get_site",
    "add_site",
    "delete_site",
    "query_search_analytics",
    "list_sitemaps",
    "get_sitemap",
    "submit_sitemap",
    "delete_sitemap",
    "inspect_url",
]
