"""Client for the GDELT DOC 2.0 API — search across news published by many
outlets. It is a public endpoint and requires no API key."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from app.config import get_settings
from app.discovery.types import CandidateSource

logger = logging.getLogger(__name__)


def _parse_seendate(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


async def search(query: str, max_records: int = 20) -> list[CandidateSource]:
    settings = get_settings()
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": str(max_records),
        "format": "json",
        "sort": "datedesc",
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(settings.gdelt_doc_api_url, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("GDELT search failed for %r: %s", query, exc)
        return []

    results: list[CandidateSource] = []
    for item in data.get("articles", []):
        url = item.get("url")
        if not url:
            continue
        results.append(
            CandidateSource(
                url=url,
                title=item.get("title", "") or "",
                published_at=_parse_seendate(item.get("seendate")),
                discovered_via="gdelt",
            )
        )
    return results
