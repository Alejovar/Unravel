"""Heurística que traduce las señales sin-LLM + con-LLM en una etiqueta de
relación del taxonomy del proyecto: confirmation, developing, correction,
reaction, update, republication, cites, same_story.

Esto es intencionalmente una heurística documentada, no una verdad
absoluta: el MVP prioriza mostrar el razonamiento (kind observado/inferido,
confidence, explicación) antes que fingir precisión perfecta.
"""

from __future__ import annotations

from dataclasses import dataclass

REPUBLICATION_PHRASE_OVERLAP = 0.85
REACTION_MAX_GAP_HOURS = 0.5


@dataclass
class ClassificationInput:
    link_evidence: bool
    phrase_overlap: float
    temporal_gap_hours: float | None
    claim_relation: str | None  # SUPPORTS | CONTRADICTS | RELATED | INSUFFICIENT | None
    narrative_changed: bool


def classify_relation(data: ClassificationInput) -> str:
    if data.phrase_overlap >= REPUBLICATION_PHRASE_OVERLAP:
        return "republication"

    if data.claim_relation == "CONTRADICTS":
        return "correction"

    if data.claim_relation == "SUPPORTS":
        return "confirmation"

    if data.narrative_changed:
        return "update"

    if (
        data.temporal_gap_hours is not None
        and data.temporal_gap_hours <= REACTION_MAX_GAP_HOURS
        and data.claim_relation in (None, "INSUFFICIENT", "RELATED")
    ):
        return "reaction"

    if data.link_evidence:
        return "cites"

    return "developing"


def status_for_target(relation: str, current_status: str) -> str:
    """Determina el estado visual del nodo `target` de una relación,
    respetando que `corrected` y `confirmed` no se degraden accidentalmente."""
    if current_status == "corrected":
        return current_status
    if relation == "correction":
        return "corrected"
    if relation == "developing":
        return "developing" if current_status == "unverified" else current_status
    if relation in ("confirmation", "update", "republication", "cites", "same_story"):
        return "confirmed" if current_status != "developing" else current_status
    return current_status
