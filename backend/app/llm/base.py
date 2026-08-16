"""Interfaz de proveedor de modelo de lenguaje.

Unravel usa el LLM únicamente para las tareas que requieren comprensión
semántica (extraer afirmaciones, compararlas, explicar cambios narrativos
y redactar el resumen final). Todo lo demás —scraping, discovery,
similitud— ocurre antes, sin LLM. Esta clase existe para que el proyecto
no dependa de un proveedor concreto; hoy solo se implementa OpenRouter
(ver openrouter.py), pero cualquier otro proveedor compatible puede
añadirse implementando esta misma interfaz.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.types import ClaimComparisonResult, EvidenceItem, ExtractedClaim, NarrativeChange


class LLMNotConfiguredError(RuntimeError):
    """Se lanza cuando no hay una OPENROUTER_API_KEY configurada."""


class LLMProvider(ABC):
    @abstractmethod
    async def extract_claims(self, article_text: str, article_title: str) -> list[ExtractedClaim]:
        """Extrae afirmaciones verificables/cuantificables de un artículo."""
        raise NotImplementedError

    @abstractmethod
    async def compare_claims(self, claim_a: str, claim_b: str) -> ClaimComparisonResult:
        """Clasifica la relación entre dos afirmaciones: SUPPORTS,
        CONTRADICTS, RELATED o INSUFFICIENT."""
        raise NotImplementedError

    @abstractmethod
    async def analyze_change(self, previous_text: str, current_text: str) -> NarrativeChange:
        """Explica cómo cambió la narrativa entre dos versiones de la
        historia (p.ej. de hipótesis a afirmación confirmada)."""
        raise NotImplementedError

    @abstractmethod
    async def summarize(self, evidence: list[EvidenceItem]) -> str:
        """Redacta el resumen final citando únicamente la evidencia ya
        procesada por el motor sin LLM."""
        raise NotImplementedError
