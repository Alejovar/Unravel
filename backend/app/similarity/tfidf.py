"""Similitud TF-IDF (VeriGraph.md sección 17). Sin modelo generativo."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SPANISH_STOPWORDS = [
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "que", "en", "por", "para", "con", "su", "sus", "es", "fue",
    "ser", "se", "a", "no", "más", "sobre", "como", "entre", "tras", "según",
    "the", "a", "an", "of", "in", "on", "and", "or", "to", "is", "was",
]


def similarity_matrix(texts: list[str]) -> np.ndarray:
    """Devuelve una matriz NxN de similitud coseno TF-IDF entre `texts`."""
    if len(texts) < 2:
        return np.zeros((len(texts), len(texts)))
    vectorizer = TfidfVectorizer(
        stop_words=SPANISH_STOPWORDS,
        max_features=20000,
        ngram_range=(1, 2),
        min_df=1,
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Vocabulario vacío (textos muy cortos/idénticos en stopwords)
        return np.zeros((len(texts), len(texts)))
    return cosine_similarity(matrix)


def pairwise_similarity(text_a: str, text_b: str) -> float:
    matrix = similarity_matrix([text_a, text_b])
    return float(matrix[0][1]) if matrix.size else 0.0
