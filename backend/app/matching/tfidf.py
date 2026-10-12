"""METHOD 3 - TF-IDF + cosine similarity.

TF-IDF turns each profile's text into a vector; rare, meaningful words get more weight.
Cosine similarity then measures how close two vectors point.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocess import expand_synonyms


def build_tfidf_matrix(docs: list[str]) -> np.ndarray:
    """Return an n x n cosine-similarity matrix for n documents."""
    cleaned = [expand_synonyms(d) for d in docs]
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        X = vec.fit_transform(cleaned)
    except ValueError:  # all documents empty
        return np.zeros((len(docs), len(docs)))
    return cosine_similarity(X)
