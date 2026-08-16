"""Playwright fallback for pages whose content depends on JavaScript.

It is optional: if Playwright or its browsers are not installed, the
pipeline simply continues without this step (the source is discarded, or
the incomplete HTML already fetched is used).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:  # pragma: no cover - environment without playwright installed
    PLAYWRIGHT_AVAILABLE = False


async def render(url: str, timeout_ms: int = 15000) -> str | None:
    """Renders `url` in a headless browser and returns the final HTML."""
    if not PLAYWRIGHT_AVAILABLE:
        logger.info("Playwright unavailable; skipping fallback for %s", url)
        return None

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=timeout_ms, wait_until="networkidle")
                html = await page.content()
                return html
            finally:
                await browser.close()
    except Exception as exc:  # noqa: BLE001 - any render failure is a failed fallback
        logger.warning("Playwright fallback failed for %s: %s", url, exc)
        return None
