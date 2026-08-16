"""Language model provider interface.

Unravel uses the LLM only for the tasks that require semantic
understanding (extracting claims, comparing them, explaining narrative
changes and writing the final summary). Everything else — scraping,
discovery, similarity — happens beforehand, without an LLM. This class
exists so the project does not depend on one concrete provider; today only
OpenRouter is implemented (see openrouter.py), but any other compatible
provider can be added by implementing this same interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.types import ClaimComparisonResult, EvidenceItem, ExtractedClaim, NarrativeChange


class LLMNotConfiguredError(RuntimeError):
    """Raised when no OPENROUTER_API_KEY is configured."""


class LLMProvider(ABC):
    @abstractmethod
    async def extract_claims(self, article_text: str, article_title: str) -> list[ExtractedClaim]:
        """Extracts verifiable/quantifiable claims from an article."""
        raise NotImplementedError

    @abstractmethod
    async def compare_claims(self, claim_a: str, claim_b: str) -> ClaimComparisonResult:
        """Classifies the relation between two claims: SUPPORTS,
        CONTRADICTS, RELATED or INSUFFICIENT."""
        raise NotImplementedError

    @abstractmethod
    async def analyze_change(self, previous_text: str, current_text: str) -> NarrativeChange:
        """Explains how the narrative changed between two versions of the
        story (e.g. from hypothesis to confirmed claim)."""
        raise NotImplementedError

    @abstractmethod
    async def summarize(self, evidence: list[EvidenceItem]) -> str:
        """Writes the final summary citing only the evidence already
        processed by the LLM-free engine."""
        raise NotImplementedError
