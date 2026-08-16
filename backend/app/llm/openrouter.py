"""Implementación de LLMProvider usando OpenRouter.

Es el único proveedor de modelo de lenguaje del proyecto. Usa un solo
modelo gratuito (":free") configurable vía OPENROUTER_MODEL, para que el
usuario solo tenga que pegar una API key en `.env` y nada más.
"""

from __future__ import annotations

import json
import logging
import re

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.llm.base import LLMNotConfiguredError, LLMProvider
from app.llm.prompts import (
    ANALYZE_CHANGE_SYSTEM,
    ANALYZE_CHANGE_USER,
    COMPARE_CLAIMS_SYSTEM,
    COMPARE_CLAIMS_USER,
    EXTRACT_CLAIMS_SYSTEM,
    EXTRACT_CLAIMS_USER,
    SUMMARIZE_SYSTEM,
    SUMMARIZE_USER,
)
from app.llm.types import ClaimComparisonResult, EvidenceItem, ExtractedClaim, NarrativeChange

logger = logging.getLogger(__name__)

JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(raw: str) -> dict:
    """Los modelos gratuitos a veces envuelven el JSON en texto o markdown.
    Esta función intenta rescatar el primer objeto JSON balanceado."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = JSON_OBJECT_RE.search(raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning("No se pudo parsear JSON de la respuesta del LLM: %.200s", raw)
    return {}


class OpenRouterProvider(LLMProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def _require_key(self) -> None:
        if not self.settings.llm_configured:
            raise LLMNotConfiguredError(
                "OPENROUTER_API_KEY no está configurada. Agrégala a tu archivo .env "
                "(ver .env.example) para habilitar el motor de análisis semántico."
            )

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError,)),
    )
    async def _chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        self._require_key()
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.openrouter_site_url,
            "X-Title": self.settings.openrouter_app_name,
        }
        payload = {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                f"{self.settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ValueError(f"Respuesta inesperada de OpenRouter: {data}") from exc

    async def extract_claims(self, article_text: str, article_title: str) -> list[ExtractedClaim]:
        content = await self._chat(
            EXTRACT_CLAIMS_SYSTEM,
            EXTRACT_CLAIMS_USER.format(title=article_title, text=article_text[:6000]),
        )
        data = _extract_json(content)
        claims_raw = data.get("claims", []) if isinstance(data, dict) else []
        claims: list[ExtractedClaim] = []
        for item in claims_raw:
            if not isinstance(item, dict) or not item.get("text"):
                continue
            claims.append(
                ExtractedClaim(
                    text=str(item.get("text", "")).strip(),
                    subject=str(item.get("subject", "")).strip(),
                    value=str(item.get("value", "")).strip(),
                )
            )
        return claims

    async def compare_claims(self, claim_a: str, claim_b: str) -> ClaimComparisonResult:
        content = await self._chat(
            COMPARE_CLAIMS_SYSTEM,
            COMPARE_CLAIMS_USER.format(claim_a=claim_a, claim_b=claim_b),
        )
        data = _extract_json(content)
        relation = str(data.get("relation", "INSUFFICIENT")).upper()
        if relation not in {"SUPPORTS", "CONTRADICTS", "RELATED", "INSUFFICIENT"}:
            relation = "INSUFFICIENT"
        confidence = data.get("confidence", 0.5)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.5
        return ClaimComparisonResult(
            relation=relation,
            explanation=str(data.get("explanation", "")).strip(),
            confidence=max(0.0, min(1.0, confidence)),
        )

    async def analyze_change(self, previous_text: str, current_text: str) -> NarrativeChange:
        content = await self._chat(
            ANALYZE_CHANGE_SYSTEM,
            ANALYZE_CHANGE_USER.format(previous=previous_text[:2000], current=current_text[:2000]),
        )
        data = _extract_json(content)
        return NarrativeChange(
            changed=bool(data.get("changed", False)),
            explanation=str(data.get("explanation", "")).strip(),
        )

    async def summarize(self, evidence: list[EvidenceItem]) -> str:
        lines = []
        for i, item in enumerate(evidence, start=1):
            claims_txt = "; ".join(item.claims) if item.claims else "sin afirmaciones extraídas"
            lines.append(
                f"{i}. [{item.role or 'fuente'}] {item.source} "
                f"({item.published_at or 'fecha desconocida'}): \"{item.headline}\" — {claims_txt}"
            )
        evidence_block = "\n".join(lines)
        content = await self._chat(
            SUMMARIZE_SYSTEM,
            SUMMARIZE_USER.format(evidence_block=evidence_block),
            temperature=0.3,
        )
        return content.strip()
