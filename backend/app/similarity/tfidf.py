"""TF-IDF similarity (VeriGraph.md section 17). No generative model."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Articles reaching this stage may be written in any language, so the
# stopword list is bilingual (English + Spanish) on purpose: dropping the
# non-English entries would leave common filler words weighting the vectors
# of Spanish-language coverage.
STOPWORDS = [
    # English
    "the", "a", "an", "of", "in", "on", "and", "or", "to", "is", "was",
    "for", "with", "by", "from", "at", "as", "that",
    # Spanish
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "que", "en", "por", "para", "con", "su", "sus", "es", "fue",
    "ser", "se", "no", "mas", "sobre", "como", "entre", "tras", "segun",
]


def similarity_matrix(texts: list[str]) -> np.ndarray:
    """Returns an NxN matrix of TF-IDF cosine similarity between `texts`."""
    if len(texts) < 2:
        return np.zeros((len(texts), len(texts)))
    vectorizer = TfidfVectorizer(
        stop_words=STOPWORDS,
        max_features=20000,
        ngram_range=(1, 2),
        min_df=1,
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Empty vocabulary (texts too short, or made up only of stopwords)
        return np.zeros((len(texts), len(texts)))
    return cosine_similarity(matrix)


def pairwise_similarity(text_a: str, text_b: str) -> float:
    matrix = similarity_matrix([text_a, text_b])
    return float(matrix[0][1]) if matrix.size else 0.0
