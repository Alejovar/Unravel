"""Construye la evidencia que se le entrega al LLM para el resumen final,
y un resumen alternativo por reglas (sin LLM) para cuando no hay
OPENROUTER_API_KEY configurada, de modo que el producto siga siendo útil."""

from __future__ import annotations

from app.llm.types import EvidenceItem
from app.models.models import Article, ArticleRelation

ROLE_BY_RELATION = {
    "confirmation": "confirma",
    "developing": "desarrollo no confirmado",
    "correction": "corrige",
    "reaction": "reacciona",
    "update": "actualiza",
    "republication": "republica",
    "cites": "cita",
    "same_story": "misma historia",
}


def build_evidence(
    articles: list[Article], relations: list[ArticleRelation], claims_by_article: dict[str, list[str]]
) -> list[EvidenceItem]:
    role_by_article: dict[str, str] = {}
    for rel in relations:
        role_by_article[rel.target_article_id] = ROLE_BY_RELATION.get(rel.relation.value, "relacionado")

    items: list[EvidenceItem] = []
    for article in sorted(articles, key=lambda a: a.published_at or a.created_at):
        role = "origen" if article.is_origin else role_by_article.get(article.id, "relacionado")
        items.append(
            EvidenceItem(
                source=f"{article.domain}" + (f" ({article.source_handle})" if article.source_handle else ""),
                published_at=article.published_at.isoformat() if article.published_at else None,
                headline=article.title or article.url,
                role=role,
                claims=claims_by_article.get(article.id, [])[:2],
            )
        )
    return items


def rule_based_summary(
    articles: list[Article],
    relations: list[ArticleRelation],
    divergence_count: int,
    llm_configured: bool = False,
) -> str:
    """Resumen extractivo simple, sin LLM, usado cuando no hay API key
    configurada (VeriGraph.md: el resumen debe poder generarse igual, solo
    que sin la profundidad semántica del LLM)."""
    if not articles:
        return "No se encontraron fuentes suficientes para reconstruir esta historia."

    ordered = sorted(articles, key=lambda a: a.published_at or a.created_at)
    origin = next((a for a in ordered if a.is_origin), ordered[0])
    pub = origin.published_at
    # Muchas fuentes solo dan la fecha; el parser completa la hora faltante
    # con medianoche UTC, que no es una hora real.
    has_time = pub and not (pub.hour == 0 and pub.minute == 0 and pub.second == 0)
    origin_time = pub.strftime("%H:%M") if has_time else "hora desconocida"

    parts = [
        f"Se encontraron {len(articles)} publicaciones relacionadas con esta historia.",
        f'La primera versión localizada fue "{origin.title or origin.url}" '
        f"({origin.domain}, {origin_time}).",
    ]

    correction_edges = [r for r in relations if r.relation.value == "correction"]
    if correction_edges:
        parts.append(
            f"Se detectaron {len(correction_edges)} correcciones formales sobre versiones anteriores."
        )
    if divergence_count:
        parts.append(
            f"El sistema identificó {divergence_count} divergencia(s) entre las afirmaciones de "
            "distintas fuentes; revisa cada nodo para ver el detalle."
        )
    else:
        parts.append("No se identificaron contradicciones claras entre las fuentes analizadas.")

    if llm_configured:
        parts.append(
            "No se pudo generar el resumen semántico con el modelo de lenguaje en este intento "
            "(el servicio no respondió); este es un resumen básico generado sin LLM."
        )
    else:
        parts.append(
            "Configura tu OPENROUTER_API_KEY en el archivo .env para obtener un resumen semántico "
            "más detallado generado por el modelo de lenguaje."
        )
    return " ".join(parts)
