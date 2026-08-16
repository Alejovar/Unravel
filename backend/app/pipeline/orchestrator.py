"""Orquesta el flujo completo de un análisis (VeriGraph.md sección 3):

URL/titular -> scraping -> discovery -> dedup -> similitud sin LLM ->
LLM (claims, comparaciones, resumen) -> grafo + timeline en la base de
datos, listos para que la API los sirva al frontend.
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.config import get_settings
from app.discovery.dedup import dedupe_articles
from app.discovery.discover import discover_candidates, discover_second_round
from app.discovery.query_builder import build_queries
from app.llm.base import LLMNotConfiguredError
from app.llm.factory import get_llm_provider
from app.llm.types import EvidenceItem
from app.models.models import (
    AnalysisStatus,
    Article,
    ArticleRelation,
    ArticleStatus,
    Claim,
    ClaimComparison,
    ClaimRelation,
    RelationKind,
    RelationType,
)
from app.models.models import Analysis, AnalysisSummary
from app.pipeline.evidence import build_evidence, rule_based_summary
from app.pipeline.relation_classifier import ClassificationInput, classify_relation, status_for_target
from app.scraping.extractor import ExtractedArticle
from app.scraping.pipeline import scrape_article
from app.similarity.entities import extract_entities
from app.similarity.scoring import compute_candidates

logger = logging.getLogger(__name__)


def _looks_like_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


def _set_status(db: Session, analysis: Analysis, status: AnalysisStatus) -> None:
    analysis.status = status
    db.add(analysis)
    db.commit()


async def _scrape_candidates(urls: list[str]) -> list[ExtractedArticle]:
    results = await asyncio.gather(*(scrape_article(u) for u in urls), return_exceptions=True)
    articles: list[ExtractedArticle] = []
    for result in results:
        if isinstance(result, ExtractedArticle):
            articles.append(result)
        elif isinstance(result, Exception):
            logger.info("scrape_article failed: %s", result)
    return articles


async def _run_discovery(
    seed: ExtractedArticle, settings
) -> list[ExtractedArticle]:
    round_one = await discover_candidates(seed)
    round_one_urls = [c.url for c in round_one]
    scraped_round_one = await _scrape_candidates(round_one_urls)

    all_articles = [seed, *scraped_round_one]
    known_urls = {a.canonical_url for a in all_articles} | {seed.url}

    if settings.discovery_max_depth >= 2:
        budget = max(0, settings.discovery_max_sources - len(all_articles))
        second_round_links: list[str] = []
        for article in scraped_round_one:
            second_round_links.extend(article.links)
        seed_domain = urlparse(seed.canonical_url).netloc.replace("www.", "")
        second_round = discover_second_round(known_urls, second_round_links, seed_domain, budget)
        if second_round:
            scraped_round_two = await _scrape_candidates([c.url for c in second_round])
            all_articles.extend(scraped_round_two)

    return all_articles[: settings.discovery_max_sources + 1]


def _build_synthetic_seed(query_input: str) -> ExtractedArticle:
    """Cuando el usuario pega un titular/descripción en vez de una URL, no
    hay artículo semilla que scrapear: se usa el texto como semilla de
    búsqueda únicamente (no se inserta como fuente en el grafo)."""
    return ExtractedArticle(
        url="",
        canonical_url="",
        domain="",
        title=query_input.strip(),
        text=query_input.strip(),
        links=[],
    )


def run_analysis(analysis_id: str) -> None:
    """Punto de entrada síncrono usado por el worker de RQ."""
    from app.db import SessionLocal

    db = SessionLocal()
    try:
        asyncio.run(_run_analysis_async(db, analysis_id))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Analysis %s failed", analysis_id)
        analysis = db.get(Analysis, analysis_id)
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.error = str(exc)
            db.add(analysis)
            db.commit()
    finally:
        db.close()


async def _run_analysis_async(db: Session, analysis_id: str) -> None:
    settings = get_settings()
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise ValueError(f"Analysis {analysis_id} no existe")

    # --- 1. Scraping del artículo semilla (si el input es una URL) ---
    _set_status(db, analysis, AnalysisStatus.SCRAPING)
    query_input = analysis.query_input.strip()

    if _looks_like_url(query_input):
        seed = await scrape_article(query_input)
        if seed is None:
            analysis.status = AnalysisStatus.FAILED
            analysis.error = (
                "No se pudo extraer contenido de la URL proporcionada. "
                "Verifica que el enlace sea accesible públicamente."
            )
            db.add(analysis)
            db.commit()
            return
        has_real_seed = True
    else:
        seed = _build_synthetic_seed(query_input)
        has_real_seed = False

    # --- 2. Discovery (GDELT + RSS + búsqueda + hyperlinks) ---
    _set_status(db, analysis, AnalysisStatus.DISCOVERING)
    if has_real_seed:
        found = await _run_discovery(seed, settings)
    else:
        candidates = await discover_candidates(seed)
        found = await _scrape_candidates([c.url for c in candidates])

    # --- 3. Deduplicación ---
    deduped = dedupe_articles(found)
    if not deduped:
        analysis.status = AnalysisStatus.FAILED
        analysis.error = "No se encontraron fuentes relacionadas para esta historia."
        db.add(analysis)
        db.commit()
        return

    # --- 4. Persistir artículos + extraer entidades ---
    db_articles: list[Article] = []
    for extracted in deduped:
        entities = extract_entities(extracted.text)
        article = Article(
            analysis_id=analysis.id,
            url=extracted.url,
            canonical_url=extracted.canonical_url,
            domain=extracted.domain,
            title=extracted.title or extracted.url,
            author=extracted.author,
            published_at=extracted.published_at,
            text=extracted.text,
            content_hash=None,
            entities=entities,
            links=extracted.links,
            discovered_via="seed" if (has_real_seed and extracted.url == seed.url) else "discovery",
        )
        db.add(article)
        db_articles.append(article)
    db.flush()

    origin = None
    if has_real_seed:
        origin = next((a for a in db_articles if a.url == seed.url), None)
    if origin is None:
        with_dates = [a for a in db_articles if a.published_at is not None]
        origin = min(with_dates, key=lambda a: a.published_at) if with_dates else db_articles[0]
    origin.is_origin = True
    analysis.origin_article_id = origin.id
    db.add(origin)
    db.add(analysis)
    db.commit()
    for a in db_articles:
        db.refresh(a)

    # --- 5. Similitud sin LLM -> candidatos de relación ---
    _set_status(db, analysis, AnalysisStatus.COMPARING)
    candidates = compute_candidates(db_articles)
    articles_by_id = {a.id: a for a in db_articles}

    # --- 6. Motor de análisis (LLM, opcional) ---
    llm = get_llm_provider()
    llm_available = settings.llm_configured
    claims_by_article: dict[str, list[Claim]] = {a.id: [] for a in db_articles}

    if llm_available:
        _set_status(db, analysis, AnalysisStatus.ANALYZING)
        try:
            for article in db_articles:
                extracted_claims = await llm.extract_claims(article.text, article.title)
                for c in extracted_claims:
                    claim = Claim(article_id=article.id, text=c.text, subject=c.subject, value=c.value)
                    db.add(claim)
                    claims_by_article[article.id].append(claim)
            db.flush()
        except LLMNotConfiguredError:
            llm_available = False

    # --- 7. Construir relaciones (edges) usando señales + LLM cuando aplica ---
    relations: list[ArticleRelation] = []
    divergence_count = 0

    for candidate in candidates:
        a = articles_by_id[candidate.article_a_id]
        b = articles_by_id[candidate.article_b_id]

        if a.published_at and b.published_at:
            source, target = (a, b) if a.published_at <= b.published_at else (b, a)
            gap_hours = abs((a.published_at - b.published_at).total_seconds()) / 3600.0
        else:
            source, target = a, b
            gap_hours = None

        claim_relation = None
        explanation = None
        narrative_changed = False

        if llm_available and claims_by_article.get(source.id) and claims_by_article.get(target.id):
            try:
                comparison = await llm.compare_claims(
                    claims_by_article[source.id][0].text, claims_by_article[target.id][0].text
                )
                claim_relation = comparison.relation
                explanation = comparison.explanation
                db.add(
                    ClaimComparison(
                        analysis_id=analysis.id,
                        claim_a_id=claims_by_article[source.id][0].id,
                        claim_b_id=claims_by_article[target.id][0].id,
                        relation=ClaimRelation(comparison.relation),
                        explanation=comparison.explanation,
                        confidence=comparison.confidence,
                    )
                )
                if comparison.relation == "CONTRADICTS":
                    divergence_count += 1

                change = await llm.analyze_change(source.text, target.text)
                narrative_changed = change.changed
                if change.explanation:
                    explanation = f"{explanation} {change.explanation}".strip()
            except Exception as exc:  # noqa: BLE001
                logger.warning("LLM comparison failed for %s/%s: %s", source.id, target.id, exc)

        relation_label = classify_relation(
            ClassificationInput(
                link_evidence=candidate.link_evidence is not None,
                phrase_overlap=candidate.phrase_overlap,
                temporal_gap_hours=gap_hours,
                claim_relation=claim_relation,
                narrative_changed=narrative_changed,
            )
        )

        relation_row = ArticleRelation(
            analysis_id=analysis.id,
            source_article_id=source.id,
            target_article_id=target.id,
            relation=RelationType(relation_label),
            kind=RelationKind(candidate.kind),
            confidence=candidate.related_score if candidate.kind == "inferred" else 1.0,
            score_breakdown={
                "title_similarity": candidate.title_similarity,
                "tfidf_similarity": candidate.tfidf_similarity,
                "phrase_overlap": candidate.phrase_overlap,
                "entity_overlap": candidate.entity_overlap,
                "temporal_score": candidate.temporal_score,
            },
            explanation=explanation,
        )
        db.add(relation_row)
        relations.append(relation_row)

        target.status = ArticleStatus(status_for_target(relation_label, target.status.value))
        db.add(target)

    db.flush()

    # --- 8. Resumen final ---
    if llm_available:
        try:
            evidence: list[EvidenceItem] = build_evidence(
                db_articles,
                relations,
                {aid: [c.text for c in claims] for aid, claims in claims_by_article.items()},
            )
            summary_text = await llm.summarize(evidence)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM summarize failed, using rule-based summary: %s", exc)
            summary_text = rule_based_summary(db_articles, relations, divergence_count)
    else:
        summary_text = rule_based_summary(db_articles, relations, divergence_count)

    ordered = sorted(db_articles, key=lambda a: a.published_at or a.created_at)
    latest = ordered[-1] if ordered else origin
    correction_edges = [r for r in relations if r.relation == RelationType.CORRECTION]
    story_drift_label = (
        f"{correction_edges[0].explanation or 'Se detectó una corrección formal sobre una versión anterior.'}"
        if correction_edges
        else ("Se detectaron afirmaciones divergentes entre fuentes." if divergence_count else "Sin divergencias mayores detectadas.")
    )

    summary = AnalysisSummary(
        analysis_id=analysis.id,
        summary_text=summary_text,
        origin_label=origin.title,
        story_drift_label=story_drift_label,
        latest_state_label=latest.title if latest else None,
        divergence_count=divergence_count,
        sources_count=len(db_articles),
        edges_count=len(relations),
    )
    db.add(summary)

    analysis.status = AnalysisStatus.DONE
    db.add(analysis)
    db.commit()
