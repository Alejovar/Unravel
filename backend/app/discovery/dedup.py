"""Deduplicación: canonical URL, hash de contenido y similitud textual.

Ver VeriGraph.md sección 14.
"""

from __future__ import annotations

import re

from app.scraping.extractor import ExtractedArticle
from app.scraping.pipeline import content_hash

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{3,}")


def _jaccard(a: str, b: str) -> float:
    tokens_a = set(WORD_RE.findall(a.lower()))
    tokens_b = set(WORD_RE.findall(b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union else 0.0


def dedupe_articles(
    articles: list[ExtractedArticle], near_dup_threshold: float = 0.9
) -> list[ExtractedArticle]:
    """Colapsa artículos con la misma canonical_url, el mismo hash de
    contenido, o texto casi idéntico (posible republicación exacta del
    mismo boletín)."""
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    kept: list[ExtractedArticle] = []

    for article in articles:
        if article.canonical_url in seen_urls:
            continue
        h = content_hash(article.text)
        if h in seen_hashes:
            continue

        is_near_dup = any(_jaccard(article.text, other.text) >= near_dup_threshold for other in kept)
        if is_near_dup:
            continue

        seen_urls.add(article.canonical_url)
        seen_hashes.add(h)
        kept.append(article)

    return kept
