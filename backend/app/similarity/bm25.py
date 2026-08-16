"""BM25 ranking (VeriGraph.md section 18): useful to prioritise which
candidate sources to process first, or with a larger budget, before
applying more expensive filters (pairwise TF-IDF, entities, LLM)."""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{2,}")


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def rank_by_relevance(query: str, documents: list[str]) -> list[float]:
    """Returns one BM25 score per document with respect to `query`."""
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
