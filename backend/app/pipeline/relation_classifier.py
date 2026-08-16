"""Heuristic that turns the LLM-free + LLM signals into one relation label
from the project taxonomy: confirmation, developing, correction, reaction,
update, republication, cites, same_story.

This is deliberately a documented heuristic, not absolute truth: the MVP
prioritises showing its reasoning (observed/inferred kind, confidence,
explanation) over pretending to be perfectly accurate.
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
    """Determines the visual status of the `target` node of a relation,
    making sure `corrected` and `confirmed` are not accidentally
    downgraded."""
    if current_status == "corrected":
        return current_status
    if relation == "correction":
        return "corrected"
    if relation == "developing":
        return "developing" if current_status == "unverified" else current_status
    if relation in ("confirmation", "update", "republication", "cites", "same_story"):
        return "confirmed" if current_status != "developing" else current_status
    return current_status
