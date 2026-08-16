"""Extracción de entidades (VeriGraph.md sección 20).

Usa spaCy si el modelo `es_core_news_sm` está instalado. Si no lo está (o
falla la carga), cae a un extractor por reglas basado en mayúsculas, para
que el sistema nunca dependa de manera dura de este paso.
"""

from __future__ import annotations

import logging
import re
import threading

logger = logging.getLogger(__name__)

_nlp = None
_load_lock = threading.Lock()
_load_attempted = False

CAPITALIZED_RE = re.compile(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})\b")
SENTENCE_START_WORDS = {"El", "La", "Los", "Las", "Un", "Una", "Sin", "Pero", "Aunque"}


def _load_spacy_model():
    global _nlp, _load_attempted
    if _load_attempted:
        return _nlp
    with _load_lock:
        if _load_attempted:
            return _nlp
        _load_attempted = True
        try:
            import spacy

            _nlp = spacy.load("es_core_news_sm")
            logger.info("Modelo spaCy es_core_news_sm cargado")
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "spaCy no disponible (%s); usando extractor de entidades por reglas", exc
            )
            _nlp = None
    return _nlp


def _fallback_extract(text: str, max_entities: int = 25) -> list[str]:
    candidates = CAPITALIZED_RE.findall(text[:20000])
    entities: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        first_word = candidate.split()[0]
        if first_word in SENTENCE_START_WORDS and len(candidate.split()) == 1:
            continue
        key = candidate.lower()
        if key not in seen:
            seen.add(key)
            entities.append(candidate)
        if len(entities) >= max_entities:
            break
    return entities


def extract_entities(text: str, max_entities: int = 25) -> list[str]:
    if not text:
        return []
    nlp = _load_spacy_model()
    if nlp is None:
        return _fallback_extract(text, max_entities)

    try:
        doc = nlp(text[:100000])
        entities: list[str] = []
        seen: set[str] = set()
        for ent in doc.ents:
            if ent.label_ in {"PER", "ORG", "LOC", "GPE", "MISC"}:
                key = ent.text.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    entities.append(ent.text.strip())
            if len(entities) >= max_entities:
                break
        return entities
    except Exception as exc:  # noqa: BLE001
        logger.warning("Fallo extrayendo entidades con spaCy: %s", exc)
        return _fallback_extract(text, max_entities)


def entity_overlap(entities_a: list[str], entities_b: list[str]) -> float:
    set_a = {e.lower() for e in entities_a}
    set_b = {e.lower() for e in entities_b}
    if not set_a or not set_b:
        return 0.0
    shared = set_a & set_b
    smaller = min(len(set_a), len(set_b))
    return len(shared) / smaller if smaller else 0.0
