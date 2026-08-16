"""Combina las señales sin LLM en un score de relevancia/relación entre
artículos (VeriGraph.md secciones 22-25).

Distingue explícitamente:
  - relación OBSERVADA: hay un hyperlink directo de un artículo a otro.
  - relación INFERIDA: solo hay indicios (similitud alta), nunca se afirma
    causalidad ("B copió a A"), solo relación posible con una confianza.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

from app.similarity.ngrams import phrase_overlap
from app.similarity.temporal import temporal_score

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{3,}")

WEIGHTS = {
    "title_similarity": 0.30,
    "tfidf_similarity": 0.30,
    "phrase_overlap": 0.15,
    "entity_overlap": 0.15,
    "temporal_score": 0.10,
}

RELATED_THRESHOLD = 0.42


class ArticleLike(Protocol):
    id: str
    title: str
    text: str
    published_at: object
    links: list[str] | None
    canonical_url: str
    entities: list[str] | None


def _title_similarity(title_a: str, title_b: str) -> float:
    tokens_a = set(WORD_RE.findall(title_a.lower()))
    tokens_b = set(WORD_RE.findall(title_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def _link_evidence(a: ArticleLike, b: ArticleLike) -> str | None:
    """Devuelve 'a_to_b', 'b_to_a' o None según haya un hyperlink explícito
    de un artículo hacia el dominio/URL canónica del otro."""
    links_a = a.links or []
    links_b = b.links or []
    domain_b = _domain(b.canonical_url)
    domain_a = _domain(a.canonical_url)

    if any(b.canonical_url in link or (domain_b and domain_b in link) for link in links_a):
        return "a_to_b"
    if any(a.canonical_url in link or (domain_a and domain_a in link) for link in links_b):
        return "b_to_a"
    return None


@dataclass
class RelationCandidate:
    article_a_id: str
    article_b_id: str
    title_similarity: float
    tfidf_similarity: float
    phrase_overlap: float
    entity_overlap: float
    temporal_score: float
    related_score: float
    link_evidence: str | None  # 'a_to_b' | 'b_to_a' | None
    kind: str  # 'observed' | 'inferred'
    default_relation: str  # 'cites' | 'same_story'


def score_pair(a: ArticleLike, b: ArticleLike, tfidf_sim: float, entity_overlap_score: float) -> RelationCandidate:
    title_sim = _title_similarity(a.title, b.title)
    phrase_ov = phrase_overlap(a.text, b.text)
    temporal = temporal_score(a.published_at, b.published_at)

    related = (
        WEIGHTS["title_similarity"] * title_sim
        + WEIGHTS["tfidf_similarity"] * tfidf_sim
        + WEIGHTS["phrase_overlap"] * phrase_ov
        + WEIGHTS["entity_overlap"] * entity_overlap_score
        + WEIGHTS["temporal_score"] * temporal
    )

    link_evidence = _link_evidence(a, b)
    kind = "observed" if link_evidence else "inferred"
    default_relation = "cites" if link_evidence else "same_story"

    return RelationCandidate(
        article_a_id=a.id,
        article_b_id=b.id,
        title_similarity=round(title_sim, 4),
        tfidf_similarity=round(tfidf_sim, 4),
        phrase_overlap=round(phrase_ov, 4),
        entity_overlap=round(entity_overlap_score, 4),
        temporal_score=round(temporal, 4),
        related_score=round(related, 4),
        link_evidence=link_evidence,
        kind=kind,
        default_relation=default_relation,
    )


def compute_candidates(articles: list[ArticleLike]) -> list[RelationCandidate]:
    """Calcula candidatos de relación para todos los pares de `articles`.
    Conserva un candidato si hay evidencia de enlace directo O si el score
    combinado supera RELATED_THRESHOLD."""
    from app.similarity.entities import entity_overlap as entity_overlap_fn
    from app.similarity.tfidf import similarity_matrix

    if len(articles) < 2:
        return []

    texts = [a.text for a in articles]
    tfidf_matrix = similarity_matrix(texts)

    candidates: list[RelationCandidate] = []
    for i in range(len(articles)):
        for j in range(i + 1, len(articles)):
            a, b = articles[i], articles[j]
            tfidf_sim = float(tfidf_matrix[i][j]) if tfidf_matrix.size else 0.0
            entity_ov = entity_overlap_fn(a.entities or [], b.entities or [])
            candidate = score_pair(a, b, tfidf_sim, entity_ov)
            if candidate.kind == "observed" or candidate.related_score >= RELATED_THRESHOLD:
                candidates.append(candidate)
    return candidates
