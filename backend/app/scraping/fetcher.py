"""Page download through httpx. No LLM: this is the first pipeline stage."""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; UnravelBot/0.1; "
    "+https://github.com/Alejovar/Unravel) NewsTraceabilityResearch"
)

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

TIMEOUT = httpx.Timeout(15.0, connect=10.0)


class FetchResult:
    def __init__(self, url: str, status_code: int, html: str | None, content_type: str = ""):
        self.url = url
        self.status_code = status_code
        self.html = html
        self.content_type = content_type

    @property
    def ok(self) -> bool:
        return self.status_code < 400 and bool(self.html)

    @property
    def looks_incomplete(self) -> bool:
        """Simple heuristic to detect JS-rendered pages (little useful HTML)."""
        if not self.html:
            return True
        stripped = self.html.strip()
        return len(stripped) < 800


async def fetch(url: str) -> FetchResult:
    """Downloads a URL with httpx. It does not raise on HTTP/network
    errors: they are wrapped in the result so the pipeline can decide the
    next step (for example, falling back to Playwright)."""
    try:
        async with httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            timeout=TIMEOUT,
            follow_redirects=True,
            http2=True,
        ) as client:
            response = await client.get(url)
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "xml" not in content_type and content_type:
                return FetchResult(str(response.url), response.status_code, None, content_type)
            return FetchResult(str(response.url), response.status_code, response.text, content_type)
    except httpx.HTTPError as exc:
        logger.warning("fetch failed for %s: %s", url, exc)
        return FetchResult(url, 0, None)


async def fetch_many(urls: list[str], concurrency: int = 6) -> dict[str, FetchResult]:
    import asyncio

    semaphore = asyncio.Semaphore(concurrency)
    results: dict[str, FetchResult] = {}

    async def _bounded(u: str) -> None:
        async with semaphore:
            results[u] = await fetch(u)

    await asyncio.gather(*(_bounded(u) for u in urls))
    return results
