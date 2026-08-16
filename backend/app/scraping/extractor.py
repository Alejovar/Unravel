"""Extraction of title/author/date/text/links out of HTML.

Trafilatura does the heavy lifting (content + metadata). BeautifulSoup is
used as a fallback and to extract ALL outbound hyperlinks of the article,
which the discovery engine uses as citation evidence.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlparse

import trafilatura
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

logger = logging.getLogger(__name__)

# Typical titles of block/challenge pages (WAF, Cloudflare, paywall) that
# sometimes answer with status 200 but are not the real article.
BLOCK_PAGE_TITLES = (
    "access denied",
    "attention required",
    "just a moment",
    "are you a human",
    "you have been blocked",
    "request unsuccessful",
    "403 forbidden",
    "429 too many requests",
)


@dataclass
class ExtractedArticle:
    url: str
    canonical_url: str
    domain: str
    title: str = ""
    author: str | None = None
    published_at: datetime | None = None
    text: str = ""
    links: list[str] = field(default_factory=list)


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _canonicalize(url: str, soup: BeautifulSoup | None = None) -> str:
    if soup is not None:
        link = soup.find("link", rel="canonical")
        if link and link.get("href"):
            return link["href"].split("#")[0]
    parsed = urlparse(url)
    query_pairs = [
        p
        for p in parsed.query.split("&")
        if p and not p.split("=")[0].lower().startswith(("utm_", "fbclid", "gclid", "ref"))
    ]
    cleaned = parsed._replace(query="&".join(query_pairs), fragment="")
    return cleaned.geturl()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return dateparser.parse(value)
    except (ValueError, OverflowError):
        return None


def _extract_links(html: str, base_url: str) -> list[str]:
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    links: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("javascript:", "mailto:", "#")):
            continue
        absolute = urljoin(base_url, href)
        if absolute.startswith("http"):
            links.add(absolute.split("#")[0])
    return sorted(links)[:200]


def extract(html: str, url: str) -> ExtractedArticle | None:
    if not html:
        return None

    downloaded_meta = trafilatura.extract(
        html,
        url=url,
        output_format="json",
        with_metadata=True,
        favor_precision=True,
        include_links=False,
    )

    title = ""
    author = None
    published_at = None
    text = ""

    if downloaded_meta:
        try:
            data = json.loads(downloaded_meta)
            title = data.get("title") or ""
            author = data.get("author") or None
            published_at = _parse_date(data.get("date"))
            text = data.get("text") or ""
        except json.JSONDecodeError:
            logger.warning("trafilatura returned non-JSON payload for %s", url)

    soup: BeautifulSoup | None
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    if not title and soup.title:
        title = soup.title.get_text(strip=True)

    if not text:
        # Minimal fallback when trafilatura could not extract any content.
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        text = "\n".join(p for p in paragraphs if len(p) > 40)

    if not published_at:
        meta_date = None
        for meta_name in (
            "article:published_time",
            "og:updated_time",
            "date",
            "pubdate",
            "publish-date",
        ):
            tag = soup.find("meta", attrs={"property": meta_name}) or soup.find(
                "meta", attrs={"name": meta_name}
            )
            if tag and tag.get("content"):
                meta_date = tag["content"]
                break
        published_at = _parse_date(meta_date)

    canonical_url = _canonicalize(url, soup)
    links = _extract_links(html, url)

    if not text or len(text) < 60:
        return None

    if title.strip().lower() in BLOCK_PAGE_TITLES:
        logger.warning("Discarding %s: block page title (%r)", url, title)
        return None

    return ExtractedArticle(
        url=url,
        canonical_url=canonical_url,
        domain=_domain(canonical_url or url),
        title=title.strip(),
        author=author.strip() if author else None,
        published_at=published_at,
        text=text.strip(),
        links=links,
    )
