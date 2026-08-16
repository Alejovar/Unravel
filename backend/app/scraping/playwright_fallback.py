"""Fallback con Playwright para páginas cuyo contenido depende de JavaScript.

Es opcional: si Playwright o sus navegadores no están instalados, el
pipeline simplemente sigue sin este paso (la fuente se descarta o se usa
el HTML incompleto que ya se tenía).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:  # pragma: no cover - entorno sin playwright instalado
    PLAYWRIGHT_AVAILABLE = False


async def render(url: str, timeout_ms: int = 15000) -> str | None:
    """Renderiza `url` en un navegador headless y devuelve el HTML final."""
    if not PLAYWRIGHT_AVAILABLE:
        logger.info("Playwright no disponible; se omite fallback para %s", url)
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
    except Exception as exc:  # noqa: BLE001 - cualquier fallo de render es un fallback fallido
        logger.warning("Playwright fallback failed for %s: %s", url, exc)
        return None
