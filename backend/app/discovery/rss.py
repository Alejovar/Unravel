"""Discovery through RSS feeds of outlets and wire agencies. No API key."""

from __future__ import annotations

import logging
import re

import feedparser
import httpx

from app.discovery.types import CandidateSource

logger = logging.getLogger(__name__)

# Broadly available general feeds from wire agencies and outlets. Feeds in
# other languages are kept on purpose: the same event is often covered
# first by a non-English outlet, and entries are matched by token overlap,
# not by language. The list can be extended without touching code (see the
# future DISCOVERY_RSS_FEEDS in .env).
DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.reuters.com/arc/outboundfeeds/rss/category/world/?outputType=xml",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    "https://www.eluniversal.com.mx/rss.xml",
    "https://elpais.com/rss/elpais/portada.xml",
]

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{4,}")


def _tokenize(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


async def _fetch_feed(client: httpx.AsyncClient, feed_url: str):
    try:
        response = await client.get(feed_url, timeout=10.0)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except httpx.HTTPError as exc:
        logger.info("RSS feed unavailable (%s): %s", feed_url, exc)
        return None


async def search(query: str, feeds: list[str] | None = None, min_overlap: int = 2) -> list[CandidateSource]:
    """Keeps feed entries whose title shares tokens with `query`."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    feeds = feeds or DEFAULT_FEEDS
    results: list[CandidateSource] = []

    async with httpx.AsyncClient(headers={"User-Agent": "UnravelBot/0.1"}) as client:
        for feed_url in feeds:
            parsed = await _fetch_feed(client, feed_url)
            if not parsed or not getattr(parsed, "entries", None):
                continue
            for entry in parsed.entries[:60]:
                title = getattr(entry, "title", "") or ""
                overlap = len(_tokenize(title) & query_tokens)
                if overlap >= min_overlap and getattr(entry, "link", None):
                    results.append(
                        CandidateSource(url=entry.link, title=title, discovered_via="rss")
                    )
    return results
