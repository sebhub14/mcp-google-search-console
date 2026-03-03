"""URL inspection tools.

Tools for inspecting URL index status, coverage, crawl, and mobile usability.
"""

from typing import Any

from ..client import get_client
from ..models import InspectUrlInput


async def inspect_url(
    inspection_url: str,
    site_url: str,
    language_code: str = "en-US",
) -> dict[str, Any]:
    """Inspect a URL's index status.

    Returns detailed information about how Google sees a URL including:
    - Index coverage (whether the URL is indexed)
    - Crawl status (last crawl time, crawl errors)
    - Mobile usability (mobile-friendly status)
    - Rich results (structured data status)

    Args:
        inspection_url: The fully-qualified URL to inspect
        site_url: The site URL (Search Console property) this URL belongs to
        language_code: Language code for localized results (default: en-US)

    Returns:
        URL inspection result with indexing, crawling, and mobile data
    """
    validated = InspectUrlInput(
        inspection_url=inspection_url,
        site_url=site_url,
        language_code=language_code,
    )

    client = get_client()
    return await client.inspection_post(
        "/urlInspection/index:inspect",
        json_data={
            "inspectionUrl": validated.inspection_url,
            "siteUrl": validated.site_url,
            "languageCode": validated.language_code,
        },
    )
