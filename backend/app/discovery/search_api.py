"""Motor de búsqueda vía API sin necesidad de API key: DuckDuckGo HTML.

Esto implementa el rol de "Search API" descrito en la arquitectura sin
requerir que el usuario configure una clave adicional además de la de
OpenRouter. Si en el futuro se quiere usar Bing/Google/Serper, basta con
añadir otra implementación con la misma firma `search(query, max_results)`.
"""

from __future__ import annotations

import logging
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from app.discovery.types import CandidateSource

logger = logging.getLogger(__name__)

SEARCH_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}


def _clean_result_url(href: str) -> str | None:
    """DuckDuckGo HTML envuelve los links en `//duckduckgo.com/l/?uddg=<url>`."""
    if href.startswith("//duckduckgo.com/l/") or "duckduckgo.com/l/" in href:
        parsed = urlparse(href if href.startswith("http") else f"https:{href}")
        qs = parse_qs(parsed.query)
        target = qs.get("uddg", [None])[0]
        return unquote(target) if target else None
    if href.startswith("http"):
        return href
    return None


async def search(query: str, max_results: int = 20) -> list[CandidateSource]:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
            response = await client.post(SEARCH_URL, data={"q": query})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Search API (DuckDuckGo) failed for %r: %s", query, exc)
        return []

    try:
        soup = BeautifulSoup(response.text, "lxml")
    except Exception:
        soup = BeautifulSoup(response.text, "html.parser")

    results: list[CandidateSource] = []
    for result in soup.select(".result"):
        link_tag = result.select_one(".result__a")
        if not link_tag or not link_tag.get("href"):
            continue
        url = _clean_result_url(link_tag["href"])
        if not url:
            continue
        title = link_tag.get_text(strip=True)
        results.append(CandidateSource(url=url, title=title, discovered_via="search"))
        if len(results) >= max_results:
            break
    return results
