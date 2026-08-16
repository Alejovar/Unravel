"""Scraping pipeline: URL -> validate -> httpx -> trafilatura -> (Playwright
fallback if the HTML looks incomplete) -> normalised article.

See VeriGraph.md section 9. No stage here uses an LLM.
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
from urllib.parse import urlparse

from app.scraping import playwright_fallback
from app.scraping.extractor import ExtractedArticle, extract
from app.scraping.fetcher import fetch

logger = logging.getLogger(__name__)

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def is_safe_url(url: str) -> bool:
    """Basic SSRF safety validation before scraping."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    if host.lower() in BLOCKED_HOSTS:
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    except ValueError:
        pass  # it is a hostname, not a literal IP; let it through
    return True


def content_hash(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def scrape_article(url: str) -> ExtractedArticle | None:
    if not is_safe_url(url):
        logger.warning("URL rejected by the safety validation: %s", url)
        return None

    result = await fetch(url)

    html = result.html
    if not result.ok or result.looks_incomplete:
        rendered = await playwright_fallback.render(url)
        if rendered:
            html = rendered
        elif result.status_code >= 400:
            # No successful fallback and the original response was an HTTP
            # error (bot-block, paywall, WAF, etc.) — there is no real
            # content to extract, so we discard instead of parsing the
            # error page.
            logger.warning("Discarding %s: status %s and no successful fallback", url, result.status_code)
            return None

    if not html:
        return None

    return extract(html, result.url or url)
