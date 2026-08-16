"""Pipeline de scraping: URL -> validar -> httpx -> trafilatura -> (fallback
Playwright si el HTML se ve incompleto) -> artículo normalizado.

Ver VeriGraph.md sección 9. Ninguna etapa aquí usa un LLM.
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
    """Validación de seguridad básica contra SSRF antes de scrapear."""
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
        pass  # es un hostname, no una IP literal; se deja pasar
    return True


def content_hash(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def scrape_article(url: str) -> ExtractedArticle | None:
    if not is_safe_url(url):
        logger.warning("URL rechazada por validación de seguridad: %s", url)
        return None

    result = await fetch(url)

    html = result.html
    if not result.ok or result.looks_incomplete:
        rendered = await playwright_fallback.render(url)
        if rendered:
            html = rendered
        elif result.status_code >= 400:
            # Sin fallback exitoso y la respuesta original fue un error HTTP
            # (bot-block, paywall, WAF, etc.) — no hay contenido real que
            # extraer, así que descartamos en vez de parsear la página de error.
            logger.warning("Descartando %s: status %s sin fallback exitoso", url, result.status_code)
            return None

    if not html:
        return None

    return extract(html, result.url or url)
