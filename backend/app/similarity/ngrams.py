"""Detección de fragmentos de texto compartidos vía n-gramas
(VeriGraph.md sección 19). Útil para republicaciones y copias parciales."""

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
    """Fracción de n-gramas de `text_a` que también aparecen en `text_b`
    (Jaccard sobre el conjunto más pequeño para no penalizar textos largos
    frente a resúmenes cortos)."""
    ngrams_a = ngrams(_tokenize(text_a), n)
    ngrams_b = ngrams(_tokenize(text_b), n)
    if not ngrams_a or not ngrams_b:
        return 0.0
    shared = ngrams_a & ngrams_b
    smaller = min(len(ngrams_a), len(ngrams_b))
    return len(shared) / smaller if smaller else 0.0
