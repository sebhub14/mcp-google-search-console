"""Site management tools.

Tools for listing, getting, adding, and removing Search Console properties.
"""

from typing import Any

from ..client import get_client
from ..models import encode_site_url


async def list_sites() -> dict[str, Any]:
    """List all Search Console properties accessible by the authenticated user.

    Returns:
        Dictionary containing site entries with permission levels
    """
    client = get_client()
    return await client.webmasters_get("/sites")


async def get_site(
    site_url: str,
) -> dict[str, Any]:
    """Get details for a specific Search Console property.

    Args:
        site_url: Site URL (e.g., "https://example.com/") or domain property
                  (e.g., "sc-domain:example.com")

    Returns:
        Site details including permission level
    """
    client = get_client()
    encoded_url = encode_site_url(site_url)
    return await client.webmasters_get(f"/sites/{encoded_url}")


async def add_site(
    site_url: str,
) -> dict[str, Any]:
    """Add a site to Search Console.

    Args:
        site_url: Site URL to add

    Returns:
        Confirmation of addition
    """
    client = get_client()
    encoded_url = encode_site_url(site_url)
    return await client.webmasters_put(f"/sites/{encoded_url}")


async def delete_site(
    site_url: str,
) -> dict[str, Any]:
    """Remove a site from Search Console.

    Args:
        site_url: Site URL to remove

    Returns:
        Confirmation of deletion
    """
    client = get_client()
    encoded_url = encode_site_url(site_url)
    return await client.webmasters_delete(f"/sites/{encoded_url}")
