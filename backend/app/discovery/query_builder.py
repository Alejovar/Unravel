"""Genera consultas de búsqueda a partir del artículo semilla, sin usar LLM.

Ver VeriGraph.md sección 11: título completo, título normalizado, entidades
principales + tema, y frases distintivas tomadas del cuerpo del texto.
"""

from __future__ import annotations

import re

STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "que", "en", "por", "para", "con", "su", "sus", "es", "fue",
    "ser", "se", "a", "no", "más", "sobre", "como", "entre", "tras", "según",
}

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{3,}")


def normalize_title(title: str) -> str:
    tokens = WORD_RE.findall(title.lower())
    tokens = [t for t in tokens if t not in STOPWORDS_ES]
    return " ".join(tokens)


def extract_distinctive_phrases(text: str, max_phrases: int = 3, phrase_len: int = 6) -> list[str]:
    """Toma frases de `phrase_len` palabras que probablemente sean únicas
    (poco comunes) para usarlas como búsqueda de "huella textual"."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    phrases: list[str] = []
    for sentence in sentences:
        words = sentence.strip().split()
        if len(words) >= phrase_len:
            phrases.append(" ".join(words[:phrase_len]))
        if len(phrases) >= max_phrases:
            break
    return phrases


def build_queries(title: str, text: str, max_queries: int = 4) -> list[str]:
    queries: list[str] = []
    if title:
        queries.append(title.strip())
        normalized = normalize_title(title)
        if normalized and normalized != title.strip().lower():
            queries.append(normalized)
    queries.extend(extract_distinctive_phrases(text, max_phrases=max_queries - len(queries)))
    # Deduplicar preservando orden
    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(q)
    return unique[:max_queries]
