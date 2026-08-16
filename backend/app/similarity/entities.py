"""Entity extraction (VeriGraph.md section 20).

It uses spaCy when one of the small news models is installed. If none of
them is available (or loading fails) it falls back to a rule-based
extractor driven by capitalisation, so the system never hard-depends on
this step.

Two models are attempted: the English one first, then the Spanish one,
because the sources being traced are frequently published in either
language.
"""

from __future__ import annotations

import logging
import re
import threading

logger = logging.getLogger(__name__)

_nlp = None
_load_lock = threading.Lock()
_load_attempted = False

SPACY_MODELS = ("en_core_web_sm", "es_core_news_sm")

CAPITALIZED_RE = re.compile(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3})\b")

# Words that commonly open a sentence and would otherwise be mistaken for a
# proper noun by the capitalisation heuristic. Kept bilingual for the same
# reason as the model list above.
SENTENCE_START_WORDS = {
    "The", "A", "An", "This", "That", "But", "However", "Although", "After",
    "El", "La", "Los", "Las", "Un", "Una", "Sin", "Pero", "Aunque",
}


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
        except Exception as exc:  # noqa: BLE001
            logger.warning("spaCy unavailable (%s); using rule-based entity extractor", exc)
            return _nlp

        for model_name in SPACY_MODELS:
            try:
                _nlp = spacy.load(model_name)
                logger.info("spaCy model %s loaded", model_name)
                return _nlp
            except Exception as exc:  # noqa: BLE001
                logger.info("spaCy model %s not available (%s)", model_name, exc)

        logger.warning(
            "No spaCy model available (%s); using rule-based entity extractor",
            ", ".join(SPACY_MODELS),
        )
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
            if ent.label_ in {"PER", "PERSON", "ORG", "LOC", "GPE", "MISC"}:
                key = ent.text.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    entities.append(ent.text.strip())
            if len(entities) >= max_entities:
                break
        return entities
    except Exception as exc:  # noqa: BLE001
        logger.warning("Entity extraction with spaCy failed: %s", exc)
        return _fallback_extract(text, max_entities)


def entity_overlap(entities_a: list[str], entities_b: list[str]) -> float:
    set_a = {e.lower() for e in entities_a}
    set_b = {e.lower() for e in entities_b}
    if not set_a or not set_b:
        return 0.0
    shared = set_a & set_b
    smaller = min(len(set_a), len(set_b))
    return len(shared) / smaller if smaller else 0.0
