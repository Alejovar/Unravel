"""Ranking BM25 (VeriGraph.md sección 18): útil para priorizar qué fuentes
candidatas procesar primero/con más presupuesto antes de aplicar filtros
más costosos (TF-IDF pairwise, entidades, LLM)."""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{2,}")


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def rank_by_relevance(query: str, documents: list[str]) -> list[float]:
    """Devuelve un score BM25 por documento respecto a `query`."""
    if not documents:
        return []
    tokenized_docs = [_tokenize(doc) for doc in documents]
    if not any(tokenized_docs):
        return [0.0] * len(documents)
    bm25 = BM25Okapi(tokenized_docs)
    scores = bm25.get_scores(_tokenize(query))
    return [float(s) for s in scores]


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []
    max_score = max(scores) or 1.0
    return [s / max_score for s in scores]
