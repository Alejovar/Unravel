"""Detection of shared text fragments through n-grams (VeriGraph.md
section 19). Useful for republications and partial copies."""

from __future__ import annotations

import re

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{2,}")


def _tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def ngrams(tokens: list[str], n: int = 5) -> set[tuple[str, ...]]:
    if len(tokens) < n:
        return set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def phrase_overlap(text_a: str, text_b: str, n: int = 5) -> float:
    """Fraction of `text_a` n-grams that also appear in `text_b` (Jaccard
    over the smaller set, so long texts are not penalised against short
    summaries)."""
    ngrams_a = ngrams(_tokenize(text_a), n)
    ngrams_b = ngrams(_tokenize(text_b), n)
    if not ngrams_a or not ngrams_b:
        return 0.0
    shared = ngrams_a & ngrams_b
    smaller = min(len(ngrams_a), len(ngrams_b))
    return len(shared) / smaller if smaller else 0.0
