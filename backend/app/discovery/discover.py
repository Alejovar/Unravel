"""Orchestrates the discovery of candidate sources: it combines GDELT,
RSS, web search and the hyperlinks of the seed article. Iterative discovery
bounded by MAX_DEPTH / MAX_SOURCES (VeriGraph.md sections 12-13).
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

from app.config import get_settings
from app.discovery import gdelt, rss, search_api
from app.discovery.query_builder import build_queries
from app.discovery.types import CandidateSource
from app.scraping.extractor import ExtractedArticle
from app.scraping.pipeline import is_safe_url

logger = logging.getLogger(__name__)

# Aggregator/social network domains that do not count as a source of their own.
SKIP_DOMAINS = {
    "twitter.com", "x.com", "facebook.com", "instagram.com", "t.co",
    "youtube.com", "tiktok.com", "reddit.com", "news.google.com",
}


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _is_useful(url: str, seed_domain: str) -> bool:
    if not is_safe_url(url):
        return False
    domain = _domain(url)
    if not domain or domain in SKIP_DOMAINS:
        return False
    return True


async def discover_candidates(seed: ExtractedArticle) -> list[CandidateSource]:
    """First round: queries generated from the seed article against GDELT
    + RSS + search, plus the article's explicit hyperlinks."""
    settings = get_settings()
    queries = build_queries(seed.title, seed.text)
    seed_domain = _domain(seed.canonical_url)

    tasks = []
    for query in queries:
        tasks.append(gdelt.search(query, max_records=settings.search_max_results))
        tasks.append(rss.search(query))
        tasks.append(search_api.search(query, max_results=settings.search_max_results))

    results_lists = await asyncio.gather(*tasks, return_exceptions=True)

    candidates: dict[str, CandidateSource] = {}
    for result in results_lists:
        if isinstance(result, Exception):
            logger.warning("Discovery source failed: %s", result)
            continue
        for candidate in result:
            if _is_useful(candidate.url, seed_domain) and candidate.url not in candidates:
                candidates[candidate.url] = candidate

    # Explicit hyperlinks cited by the seed article itself.
    for link in seed.links:
        if _is_useful(link, seed_domain) and link not in candidates:
            candidates[link] = CandidateSource(url=link, discovered_via="link")

    ordered = list(candidates.values())[: settings.discovery_max_sources]
    return ordered


def discover_second_round(
    known_urls: set[str], newly_found_links: list[str], seed_domain: str, budget: int
) -> list[CandidateSource]:
    """Second discovery round: follows links cited by the articles already
    found in the first round (it does not call the search engines again, it
    only expands through direct citation)."""
    out: list[CandidateSource] = []
    for link in newly_found_links:
        if len(out) >= budget:
            break
        if link in known_urls:
            continue
        if _is_useful(link, seed_domain):
            out.append(CandidateSource(url=link, discovered_via="link"))
    return out
