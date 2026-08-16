"""Builds search queries from the seed article, without using an LLM.

See VeriGraph.md section 11: full title, normalised title, main entities +
topic, and distinctive phrases taken from the body text.
"""

from __future__ import annotations

import re

# The product interface is in English, but the sources it traces are not:
# news coverage of the same event is routinely published in several
# languages. The stopword list therefore covers English and Spanish so that
# query normalisation works on both.
STOPWORDS = {
    # English
    "the", "a", "an", "of", "in", "on", "at", "and", "or", "to", "for",
    "with", "by", "from", "is", "was", "were", "be", "as", "that", "after",
    "over", "into", "its", "his", "her", "their",
    # Spanish
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "que", "en", "por", "para", "con", "su", "sus", "es", "fue",
    "ser", "se", "a", "no", "mas", "sobre", "como", "entre", "tras", "segun",
}

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]{3,}")


def normalize_title(title: str) -> str:
    tokens = WORD_RE.findall(title.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)


def extract_distinctive_phrases(text: str, max_phrases: int = 3, phrase_len: int = 6) -> list[str]:
    """Takes phrases of `phrase_len` words that are likely to be unique
    (uncommon) so they can be used as a "textual fingerprint" search."""
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
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(q)
    return unique[:max_queries]
