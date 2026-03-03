"""Search analytics tools.

Tools for querying search traffic data (clicks, impressions, CTR, position).
"""

from typing import Any

from ..client import get_client
from ..models import SearchAnalyticsQuery, encode_site_url


async def query_search_analytics(
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

    Args:
        site_url: Site URL or domain property
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        dimensions: Dimensions to group by (date, query, page, country, device,
                    searchAppearance)
        search_type: Search type (web, image, video, news, googleNews, discover)
        aggregation_type: How to aggregate (auto, byPage, byProperty)
        row_limit: Maximum rows to return (1-25000, default: 1000)
        start_row: Zero-based row offset for pagination (default: 0)
        dimension_filter_groups: Filter groups for the query
        data_state: Data freshness (final, all)

    Returns:
        Search analytics data with rows containing clicks, impressions, ctr, position
    """
    validated = SearchAnalyticsQuery(
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

    client = get_client()
    encoded_url = encode_site_url(site_url)

    body: dict[str, Any] = {
        "startDate": validated.start_date,
        "endDate": validated.end_date,
        "type": validated.search_type,
        "aggregationType": validated.aggregation_type,
        "rowLimit": validated.row_limit,
        "startRow": validated.start_row,
        "dataState": validated.data_state,
    }

    if validated.dimensions:
        body["dimensions"] = validated.dimensions
    if validated.dimension_filter_groups:
        body["dimensionFilterGroups"] = validated.dimension_filter_groups

    return await client.webmasters_post(
        f"/sites/{encoded_url}/searchAnalytics/query",
        json_data=body,
    )
